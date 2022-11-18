from adapter.database import db_session
from adapter.orm import user_mappers
from adapter.repository.user import UserRepository
from helper.constant import S3_BUCKET, JWT_AUDIENCE, API_CIRCLIN, INVALID_MIMES, RESIZE_WIDTHS_IMAGE, RESIZE_WIDTHS_VIDEO, APP_ROOT, APP_TEMP, FFMPEG_PATH2, FFMPEG_PATH1, FFMPEG_PATH3, FIREBASE_AUTHORIZATION_KEY, AMAZON_URL


import hashlib
import base64
import subprocess
from moviepy.editor import VideoFileClip
import requests
import boto3
import cv2
import filetype
import json
import jwt
import os
import re
from PIL import Image
import pyheif
import pymysql
from pypika import MySQLQuery as Query, functions as fn, Criterion
import random
import shutil
from sqlalchemy.orm import clear_mappers
import string
from werkzeug.utils import secure_filename


# region authentication
def authenticate(request, session):
    token = request.headers.get('token')
    uid: int = jwt.decode(token, audience=JWT_AUDIENCE, options={"verify_signature": False})['uid']

    user_mappers()
    repo: UserRepository = UserRepository(session)
    user = repo.get_one(user_id=uid)
    clear_mappers()

    if user is None:
        return None
    else:
        return user.id
# endregion


# region etc
def get_query_strings_from_request(request, param, init_value):
    if request.args.get(param) is None or request.args.get(param) == '':
        if param == 'word':
            result = init_value
        elif param == 'limit':
            result = init_value
        elif param == 'cursor':
            result = init_value
        elif param == 'page':
            result = init_value
        else:
            result = ''
    else:
        if param == 'word':
            result = request.args.get(param)
        elif param == 'limit':
            result = int(request.args.get(param))
        elif param == 'cursor':
            result = int(request.args.get(param))
        elif param == 'page':
            result = int(request.args.get(param))
        else:
            result = ''

    return result
# endregion


# region notification
def replace_notification_message_variable(message, value_dict: dict):
    values_to_replace = {
        '{%board_comment}': value_dict['board_comment'],
        '{%board_comment_multi}': value_dict['board_comment'],
        '{%count}': str(value_dict['count'] - 1),
        '{%feed_check}': str(value_dict['point']),
        '{%feed_comment}': value_dict['feed_comment'],
        '{%feed_comment_multi}': value_dict['feed_comment'],
        '{%mission}': value_dict['mission_title'],
        '{%mission_comment}': value_dict['mission_comment'],
        '{%mission_comment_multi}': value_dict['mission_comment'],
        '{%nickname}': value_dict['nickname'],
        '{%notice_comment}': value_dict['notice_comment'],
        '{%point}': str(value_dict['point']),
        '{%point2}': str(value_dict['point2'])
    }
    pattern = re.compile("{%[a-z|A-Z|0-9|(-_~`!@#$%^&*()+=\\|/)]+}")   # \\| or \|
    converted_result = regular_expression_converter(pattern, message, values_to_replace)
    return converted_result


def regular_expression_converter(pattern, sentence, dictionary) -> str:
    matches = pattern.findall(sentence)
    for data in matches:
        sentence = sentence.replace(data, dictionary[data])
    return sentence


def replace_notification_link_by_type(touch_area_direction: str, notification_type: str, value_dict: dict):
    # CommonCode 테이블에서 확인 가능한 값: where('ctg_lg' = 'click_action')-> return {'ctg_sm': 'content_ko'};
    push_click_action: dict = {
        "board": {
            "route": "Sub",
            "screen": "BoardDetail",
            "params": {
                "id": None,  # "{%id|null}",
                "comment_id": None,  # "{%comment_id|null}"
            }
        },
        "chat": {
            "route": "Sub",
            "screen": "MessageRoom",
            "params": {
                "id": None,  # "{%id|null}"
            }
        },
        "event_mission": {
            "route": "Event",
            "screen": "EventGround",
            "params": {
                "challId": None,  # "{%id|null}",
                "challPk": None,  # "{%mission_stat_id|null}",
                "userPk": None,  # "{%user_id|null}",
                "userData": {
                    "id": None,  # "{%user_id|null}",
                    "nickname": None,  # "{%nickname}"
                }
            }
        },
        "event_mission_intro": {
            "route": "Event",
            "screen": "EventIntro",
            "params": {
                "uid": None,  # "{%user_id|null}",
                "token": None,  # "{%token|null}",
                "challId": None,  # "{%id|null}",
                "userData": {
                    "id": None,  # "{%user_id|null}"
                },
                "toastVisible": False
            }
        },
        "event_mission_old": {
            "route": "Event",
            "screen": "EventMissionDetail",
            "params": {
                "challId": None,  # "{%id|null}",
                "uid": None,  # "{%user_id|null}",
                "userData": {
                    "id": None,  # "{%user_id|null}"
                }
            }
        },
        "feed": {
            "route": "Sub",
            "screen": "Feed",
            "params": {
                "id": None,  # "{%id|null}",
                "comment_id": None,  # "{%comment_id|null}"
            }
        },
        "follow": {
            "route": "Sub",
            "screen": "User",
            "params": {
                "id": None,  # "{%id|null}"
            }
        },
        "home": {
            "route": "BottomNav",
            "screen": "Home",
            "params": {}
        },
        "mission": {
            "route": "Sub",
            "screen": "Mission",
            "params": {
                "id": None,  # "{%id|null}",
                "comment_id": None,  # "{%comment_id|null}"
            }
        },
        "notice": {
            "route": "Option",
            "screen": "NoticeRoom",
            "params": {
                "id": None,  # "{%id|null}",
                "comment_id": None,  # "{%comment_id|null}"
            }
        },
        "point": {
            "route": "Shop",
            "screen": "Shop",
            "params": {
                "id": None,  # "{%id|null}",
                "comment_id": None,  # "{%comment_id|null}",
                "index": 1
            }
        },
        "product": {
            "route": "Shop",
            "screen": "ShopDetail",
            "params": {
                "id": None,  # "{%id|null}"
            }
        },
        "url": {
            "route": None,
            "screen": None,
            "params": {
                "id": None,  # "{%id|null}",
                "url": None,  # "{%url}"
            }
        },
        "user": {
            "route": "Sub",
            "screen": "User",
            "params": {
                "id": None,  # "{%id|null}"
            }
        },
    }

    # 구체적인 리턴 조건 구현 필요
    if touch_area_direction == 'center':
        if notification_type in ['follow', 'follow_multi']:
            push_click_action['user']['params']['id'] = value_dict['user_id']
            return push_click_action['user']
        elif notification_type in [
            'feed_check', 'feed_check_multi', 'feed_comment', 'feed_comment_multi',
            'feed_reply', 'feed_reply_multi', 'feed_upload_place', 'feed_upload_product'
        ]:
            push_click_action['feed']['params']['id'] = value_dict['feed_id']
            push_click_action['feed']['params']['comment_id'] = value_dict['feed_comment_id']
            return push_click_action['feed']
        elif notification_type in [
            'mission_like', 'mission_like_multi', 'mission_comment', 'mission_comment_multi',
            'mission_reply', 'mission_reply_multi', 'challenge_reward_point', 'challenge_reward_point_old',
            'mission_complete', 'mission_invite', 'earn_badge', 'mission_over', 'mission_expire'
        ]:
            if value_dict['is_ground'] is True:
                mission_push_click_action = push_click_action['event_mission']
                mission_push_click_action['params']['challId'] = value_dict['mission_id']
            else:
                mission_push_click_action = push_click_action['mission']
                mission_push_click_action['params']['id'] = value_dict['mission_id']
                mission_push_click_action['params']['comment_id'] = value_dict['mission_comment_id']
            return mission_push_click_action
        elif notification_type in ['feed_check_reward', 'mission_treasure']:
            return push_click_action['point']
        elif notification_type in ['feed_emoji']:
            push_click_action['chat']['params']['id'] = value_dict['user_id']
            return push_click_action['chat']
        elif notification_type in ['board_like', 'board_like_multi', 'board_comment', 'board_comment_multi', 'board_reply', 'board_reply_multi']:
            push_click_action['board']['params']['id'] = value_dict['board_id']
            push_click_action['board']['params']['comment_id'] = value_dict['board_comment_id']
            return push_click_action['board']
        elif notification_type in ['notice_reply', 'notice_reply_multi', 'notice_comment', 'notice_comment_multi']:
            push_click_action['notice']['params']['id'] = value_dict['notice_id']
            push_click_action['notice']['params']['comment_id'] = value_dict['notice_comment_id']
            return push_click_action['notice']
        else:
            return None
    elif touch_area_direction == 'left':
        if notification_type in [
            'follow', 'follow_multi',
            'feed_emoji', 'feed_check', 'feed_check_multi', 'feed_comment',
            'feed_comment_multi', 'feed_reply', 'feed_reply_multi',
            'mission_like', 'mission_like_multi', 'mission_comment', 'mission_comment_multi',
            'mission_reply', 'mission_reply_multi', 'mission_invite'
        ]:
            push_click_action['user']['params']['id'] = value_dict['user_id']
            return push_click_action['user']
        elif notification_type in ['feed_upload_place', 'feed_upload_product']:
            push_click_action['user']['params']['id'] = value_dict['target_id']
            return push_click_action['user']
        elif notification_type in ['feed_check_reward', 'mission_treasure']:
            return push_click_action['point']
        elif notification_type in [
            'challenge_reward_point', 'challenge_reward_point_old', 'earn_badge',
            'mission_complete', 'mission_expire_warning', 'mission_over', 'mission_expire'
        ]:
            if value_dict['is_ground'] is True:
                mission_push_click_action = push_click_action['event_mission']
                mission_push_click_action['params']['challId'] = value_dict['mission_id']
            else:
                mission_push_click_action = push_click_action['mission']
                mission_push_click_action['params']['id'] = value_dict['mission_id']
                mission_push_click_action['params']['comment_id'] = value_dict['mission_comment_id']
            return mission_push_click_action
        elif notification_type in ['board_like', 'board_like_multi', 'board_comment', 'board_comment_multi', 'board_reply', 'board_reply_multi']:
            push_click_action['user']['params']['id'] = value_dict['user_id']
            return push_click_action['user']
        elif notification_type in ['notice_comment', 'notice_comment_multi', 'notice_reply', 'notice_reply_multi']:
            push_click_action['user']['params']['id'] = value_dict['user_id']
            return push_click_action['user']
        else:
            return None
    elif touch_area_direction == 'right':
        if notification_type in ['follow', 'follow_multi']:
            push_click_action['user']['params']['id'] = value_dict['user_id']
            return push_click_action['user']
        elif notification_type in [
            'feed_check', 'feed_check_multi', 'feed_comment', 'feed_comment_multi',
            'feed_reply', 'feed_reply_multi', 'feed_emoji', 'feed_upload_place', 'feed_upload_product'
        ]:
            push_click_action['feed']['params']['id'] = value_dict['feed_id']
            push_click_action['feed']['params']['comment_id'] = value_dict['feed_comment_id']
            return push_click_action['feed']
        elif notification_type in [
            'mission_like', 'mission_like_multi', 'mission_comment', 'mission_comment_multi',
            'mission_reply', 'mission_reply_multi', 'challenge_reward_point', 'challenge_reward_point_old',
            'mission_complete', 'mission_invite', 'mission_expire_warning', 'mission_over', 'mission_expire'
        ]:
            if value_dict['is_ground'] is True:
                mission_push_click_action = push_click_action['event_mission']
                mission_push_click_action['params']['challId'] = value_dict['mission_id']
            else:
                mission_push_click_action = push_click_action['mission']
                mission_push_click_action['params']['id'] = value_dict['mission_id']
                mission_push_click_action['params']['comment_id'] = value_dict['mission_comment_id']
            return mission_push_click_action
        elif notification_type in ['feed_check_reward', 'mission_treasure']:
            return push_click_action['point']
        elif notification_type in ['board_like', 'board_like_multi', 'board_comment', 'board_comment_multi', 'board_reply', 'board_reply_multi']:
            push_click_action['board']['params']['id'] = value_dict['board_id']
            push_click_action['board']['params']['comment_id'] = value_dict['board_comment_id']
            return push_click_action['board']
        elif notification_type in ['notice_comment', 'notice_comment_multi', 'notice_reply', 'notice_reply_multi']:
            push_click_action['notice']['params']['id'] = value_dict['notice_id']
            push_click_action['notice']['params']['comment_id'] = value_dict['notice_comment_id']
            return push_click_action['notice']
    else:
        return None
# endregion


# # region file processing
# def upload_single_file_to_s3(file, object_path):
#     connection = db_connection()
#     cursor = get_dict_cursor(connection)
#     random_string = ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=15))
#
#     s3_client = boto3.client('s3')
#
#     # 1. Save request image first.
#     if type(file) != bytes:
#         request_file = file.filename
#     else:
#         request_file = file['uri'].split('/')[-1]  # file path form from react-native client.
#
#     filename = secure_filename(request_file)
#     if filename == '':
#         result = {
#             'result': f'filename: {filename}, file: {file}',
#         }
#         return result
#
#     file.save(filename)
#
#     request_path = os.path.join(os.getcwd(), 'temp', request_file)
#
#     shutil.move(filename, request_path)
#
#     # 2. Check image mime type & change if invalid.
#     mime_type, request_ext = check_mimetype(request_path)['mime_type'].split('/')
#     # request_ext = check_mimetype(request_path)['mime_type'].split('/')[1]
#
#     if request_ext in INVALID_MIMES['image']:  # or video
#         original_file = heic_to_jpg(request_path)
#     elif request_ext in INVALID_MIMES['video']:
#         original_file = video_to_mp4(request_path)
#     else:
#         original_file = request_path
#
#     original_file_name = original_file.split('/')[-1]  # Insert to DB
#     hashed_file_name = f"{hashlib.sha256(original_file_name.split('.')[0].encode()).hexdigest()}_{random_string}.{original_file_name.split('.')[1]}"
#     hashed_file = os.path.join(os.getcwd(), 'temp', hashed_file_name)
#     os.rename(original_file, hashed_file)
#
#     hashed_object_name = os.path.join(object_path, hashed_file_name)
#     hashed_mime_type = check_mimetype(hashed_file)['mime_type']
#     hashed_file_info = get_file_information(hashed_file, mime_type)
#     hashed_s3_pathname = os.path.join(AMAZON_URL, hashed_object_name)
#
#     s3_client.upload_file(hashed_file, S3_BUCKET, hashed_object_name, ExtraArgs={'ContentType': mime_type})
#
#     sql = Query.into(
#         Files
#     ).columns(
#         Files.created_at,
#         Files.updated_at,
#         Files.pathname,
#         Files.original_name,
#         Files.mime_type,
#         Files.size,
#         Files.width,
#         Files.height
#     ).insert(
#         fn.Now(),
#         fn.Now(),
#         hashed_s3_pathname,
#         original_file_name,
#         hashed_mime_type,
#         hashed_file_info['size'],
#         hashed_file_info['width'],
#         hashed_file_info['height']
#     ).get_sql()
#
#     cursor.execute(sql)
#     connection.commit()
#     original_file_id = cursor.lastrowid
#
#     # 3. Generate resized image
#     if hashed_mime_type.split('/')[0] == 'image':
#         resized_file_list = generate_resized_file(hashed_file_name.split('.')[1], hashed_file, mime_type)
#
#         for resized_path in resized_file_list:
#             object_name = os.path.join(object_path, resized_path.split('/')[-1])
#             resized_mime_type = check_mimetype(resized_path)['mime_type']
#             resized_file_info = get_file_information(resized_path, mime_type)
#             resized_s3_pathname = os.path.join(AMAZON_URL, object_name)
#
#             s3_client.upload_file(resized_path, S3_BUCKET, object_name, ExtraArgs={'ContentType': mime_type})
#
#             sql = Query.into(
#                 Files
#             ).columns(
#                 Files.created_at,
#                 Files.updated_at,
#                 Files.pathname,
#                 Files.original_name,
#                 Files.mime_type,
#                 Files.size,
#                 Files.width,
#                 Files.height,
#                 Files.original_file_id
#             ).insert(
#                 fn.Now(),
#                 fn.Now(),
#                 resized_s3_pathname,
#                 original_file_name,
#                 resized_mime_type,
#                 resized_file_info['size'],
#                 resized_file_info['width'],
#                 resized_file_info['height'],
#                 original_file_id
#             ).get_sql()
#
#             cursor.execute(sql)
#             connection.commit()
#             os.remove(resized_path)
#
#     os.remove(hashed_file)
#     connection.close()
#
#     result = {'result': True, 'original_file_id': original_file_id}
#
#     return result
#
#
# def heic_to_jpg(path):
#     heif_file = pyheif.read(path)
#     new_image = Image.frombytes(
#         heif_file.mode,
#         heif_file.size,
#         heif_file.data,
#         "raw",
#         heif_file.mode,
#         heif_file.stride,
#     )
#
#     new_path = f"{path.split('/')[-1].split('.')[0]}.jpg"
#     new_image.save(new_path, "JPEG")
#     if os.path.exists(path):
#         os.remove(path)
#
#     return new_path
#
#
# def video_to_mp4(path):
#     # new_path = os.path.join(os.getcwd(), 'temp', f"{path.split('/')[-1].split('.')[0]}.mp4")
#     # original_clip = VideoFileClip(path)
#     # original_clip.write_videofile(new_path,
#     #                               codec='libx264',
#     #                               audio_codec='aac',  # Super important for sound
#     #                               remove_temp=True)
#     original_file = cv2.VideoCapture(path)
#     height = int(original_file.get(cv2.CAP_PROP_FRAME_HEIGHT))
#     width = int(original_file.get(cv2.CAP_PROP_FRAME_WIDTH))
#
#     if width % 2 != 0:
#         width += 1
#     else:
#         pass
#
#     if height % 2 != 0:
#         height += 1
#     else:
#         pass
#
#     new_path = os.path.join(os.getcwd(), 'temp', f"{path.split('/')[-1].split('.')[0]}.mp4")
#     original_clip = VideoFileClip(path)
#     original_clip.resize((width, height)).write_videofile(new_path,
#                                                           codec='libx264',
#                                                           audio_codec='aac',  # Super important for sound
#                                                           remove_temp=True)
#     original_clip.close()
#     if os.path.exists(path):
#         os.remove(path)
#
#     return new_path
#
#
# def check_mimetype(path):
#     result = {'mime_type': filetype.guess(path).mime}
#     return result
#
#
# def get_file_information(path, file_type):
#     if file_type == 'image':
#         image = cv2.imread(path, cv2.IMREAD_COLOR)
#         height, width, channel = image.shape
#     else:
#         video = cv2.VideoCapture(path)
#         height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
#         width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
#
#     result = {
#         'size': int(os.path.getsize(path)),
#         'width': width,
#         'height': height
#     }
#
#     return result
#
#
# def generate_resized_file(extension, original_file_path, file_type):
#     resized_file_list = []
#     if file_type == 'image':
#         original_file = cv2.imread(original_file_path, cv2.IMREAD_COLOR)
#         height, width, channel = original_file.shape
#
#         for new_width in RESIZE_WIDTHS_IMAGE:
#             new_height = int(new_width * height / width)
#             resized_file = cv2.resize(original_file,
#                                       dsize=(new_width, new_height),
#                                       interpolation=cv2.INTER_LINEAR)
#             temp_path = './temp'
#             original_file_name = original_file_path.split('/')[-1]
#             resized_file_name = f"{original_file_name.split('.')[0]}_w{str(new_width)}.{extension}"
#             resized_file_path = os.path.join(temp_path, resized_file_name)
#             cv2.imwrite(resized_file_path, resized_file)
#             resized_file_list.append(resized_file_path)
#         # return resized_image_list
#     else:
#         pass
#         # original_file = cv2.VideoCapture(original_file_path)
#         # height = int(original_file.get(cv2.CAP_PROP_FRAME_HEIGHT))
#         # width = int(original_file.get(cv2.CAP_PROP_FRAME_WIDTH))
#         #
#         # for new_width in RESIZE_WIDTHS_VIDEO:
#         #     if new_width % 2 != 0:
#         #         new_width += 1
#         #     else:
#         #         pass
#         #
#         #     new_height = int(new_width * height / width)
#         #     if new_height % 2 != 0:
#         #         new_height += 1
#         #     else:
#         #         pass
#         #
#         #     temp_path = './temp'
#         #     original_file_name = original_file_path.split('/')[-1]
#         #     resized_file_name = f"{original_file_name.split('.')[0]}_w{str(new_width)}.{extension}"
#         #     resized_file_path = os.path.join(temp_path, resized_file_name)
#         #
#         #     os.system(f"ffmpeg -i {original_file_path} -vf scale={new_width}x{new_height} {resized_file_path}")
#         #     # mp.VideoFileClip(original_file_path).resize((new_width, new_height)).write_videofile(resized_file_path,
#         #     #                                                                                      codec='libx264',
#         #     #                                                                                      audio_codec='aac', # Super important for sound
#         #     #                                                                                      remove_temp=True)
#         #
#         #     resized_file_list.append(resized_file_path)
#
#     return resized_file_list
# # endregion


# # region 알림(notification)
# def create_notification(target_user_id: int, notification_type: str, user_id: int,  target_table: str, target_table_id: int, target_comment_id: any, variables: any):
#     # notification_type: board_like, board_comment, board_reply
#     connection = db_connection()
#     cursor = get_dict_cursor(connection)
#
#     sql = Query.into(
#         Notifications
#     ).columns(
#         Notifications.created_at,
#         Notifications.updated_at,
#         Notifications.target_id,
#         Notifications.type,
#         Notifications.user_id,
#         f"{target_table}_id",
#         f"{target_table}_comment_id",
#         Notifications.variables
#     ).insert(
#         fn.Now(),
#         fn.Now(),
#         target_user_id,
#         notification_type,
#         user_id,
#         target_table_id,
#         target_comment_id,
#         variables
#     ).get_sql()
#
#     cursor.execute(sql)
#     connection.commit()
#     connection.close()
#
#     return True
# # endregion
#
#
# # region 푸시(push)
# def send_fcm_push(target_ids: list, push_type: str, user_id: int, board_id: int, comment_id: any, push_title: str, push_body: str):
#     connection = db_connection()
#     cursor = get_dict_cursor(connection)
#
#     url = 'https://fcm.googleapis.com/fcm/send'
#     headers = {
#         'Authorization': FIREBASE_AUTHORIZATION_KEY,
#         'Content-Type': 'application/json'
#     }
#
#     # target별 푸시 전송
#     for index, target in enumerate(target_ids):
#         if target != user_id:
#             # 3-1. target 정보 조회
#             sql = Query.from_(
#                 Users
#             ).select(
#                 Users.nickname,
#                 Users.device_token,
#                 Users.device_type,
#                 Users.agree_push
#             ).where(
#                 Criterion.all([
#                     Users.id == int(target),
#                 ])
#             ).get_sql()
#
#             cursor.execute(sql)
#             target_user = cursor.fetchone()
#             target_user_device_token = target_user['device_token']
#             # device_token = 'ekLzPt2Qw0KOqvcB5U-s71:APA91bGuIMPMb373oPEkkNlAZW3NT5pYerdqyz2Zs5zhZG4OanQj2BJC4UdSlwbqMyeN1wbx11r1odCVO7FRABxBCVR0F4jXb8aw2P0x2eFzQA_64BJdOLE_VY1A9dNG9OM8aE1_w_ZO'
#             target_user_device_type = target_user['device_type']
#             target_user_push_agreement = True if target_user['agree_push'] == 1 else False
#
#             # 3-2. 푸시 메시지 발송 요청(Firebase API)
#             if target_user_push_agreement is True and target_user_device_token is not None and target_user_device_token.strip() != '':
#                 processed_push_body = re.sub('\\\\"', '"', push_body)  # for Firebase push text form.
#                 data = {
#                     "registration_ids": [target_user_device_token],
#                     "notification": {
#                         "tag": push_type,
#                         "body": processed_push_body,
#                         "subtitle" if target_user_device_type == "ios" else "title": push_title,
#                         "channel_id": "Circlin"
#                     },
#                     "priority": "high",
#                     "data": {
#                         "link": {
#                             "route": "Sub",
#                             "screen": "BoardDetail",
#                             "params": {
#                                 "id": board_id,
#                                 "comment_id": comment_id
#                             }
#                         }
#                     }
#                 }
#
#                 response = requests.post(
#                     url=url,
#                     headers=headers,
#                     json=data
#                 ).json()
#
#                 # 4. 발송 결과 DB에 저장
#                 data.pop('registration_ids')
#                 push_body_mysql = re.sub('\r', '\\\\r', push_body)
#                 push_body_mysql = re.sub('\n', '\\\\n', push_body_mysql)
#                 data['notification']['body'] = push_body_mysql  # for mysql
#                 sql = Query.into(
#                     PushHistories
#                 ).columns(
#                     PushHistories.created_at,
#                     PushHistories.updated_at,
#                     PushHistories.target_id,
#                     PushHistories.device_token,
#                     PushHistories.title,
#                     PushHistories.message,
#                     PushHistories.type,
#                     PushHistories.result,
#                     PushHistories.json,
#                     PushHistories.result_json
#                 ).insert(
#                     fn.Now(),
#                     fn.Now(),
#                     int(target),
#                     target_user_device_token,
#                     push_title,
#                     push_body,
#                     push_type,
#                     True if response['results'][0]['message_id'] else False,
#                     json.dumps(data, ensure_ascii=False),
#                     json.dumps(response['results'][0], ensure_ascii=False)
#                 ).get_sql()
#                 cursor.execute(sql)
#             else:
#                 pass
#         else:
#             pass
#     connection.commit()
#     connection.close()
#     return True
# # endregion


