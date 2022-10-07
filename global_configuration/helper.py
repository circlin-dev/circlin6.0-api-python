import hashlib
import base64
import subprocess
import moviepy.editor as mp
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
import string
from werkzeug.utils import secure_filename

from global_configuration.constants import S3_BUCKET, JWT_SECRET_KEY, JWT_AUDIENCE, API_CIRCLIN, INVALID_MIMES, \
    RESIZE_WIDTHS_IMAGE, RESIZE_WIDTHS_VIDEO, APP_ROOT, APP_TEMP, FFMPEG_PATH2, FFMPEG_PATH1, FFMPEG_PATH3, \
    FIREBASE_AUTHORIZATION_KEY
from global_configuration.database import DATABASE
from global_configuration.table import Files, Notifications, Users, PushHistories


# region database
def db_connection():
    connection = pymysql.connect(
        user=DATABASE['user'],
        passwd=DATABASE['password'],
        host=DATABASE['host'],
        db=DATABASE['scheme'],
        charset=DATABASE['charset'])

    return connection


def get_dict_cursor(connection):
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    return cursor
# endregion


# region authentication
def authenticate(request, cursor):
    token = request.headers.get('token')
    uid = jwt.decode(token, audience=JWT_AUDIENCE, options={"verify_signature": False})['uid']

    if uid == '' or uid is None:
        user_id = {'user_id': None}
    else:
        user_id = {'user_id': int(uid)}

    # if request.cookies.get('circlinapi_session') is not None:
    #     #     cookie = request.cookies.get('circlinapi_session')
    #     #     sql = Query.from_(
    #     #         Sessions
    #     #     ).select(
    #     #         Sessions.user_id
    #     #     ).where(
    #     #         Sessions.id == cookie
    #     #     ).get_sql()
    #     #
    #     #     cursor.execute(sql)
    #     #     # user_id = json.dumps(cursor.fetchone(), indent=4, ensure_ascii=False)
    #     #     user_id = cursor.fetchone()
    #     # else:
    #     #     token = request.headers.get('token')
    #     #     user_id = {
    #     #         'user_id': int(jwt.decode(token, options={"verify_signature": False}))   # out secret key
    #     #     }

    return user_id
# endregion


# region etc
def convert_timestamp_to_string(query_result: dict, keys: list):
    for data in query_result:
        for key in keys:
            if data[key] is None:
                pass
            else:
                data[key] = data[key].strftime('%Y-%m-%d %H:%M:%S')

    return query_result


def return_json(result: dict):
    return json.dumps(result, ensure_ascii=False)


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
            page = int(request.args.get(param))
        else:
            result = ''

    return result

# endregion


# region file processing
def upload_single_file_to_s3(file, object_path):
    connection = db_connection()
    cursor = get_dict_cursor(connection)
    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=15))

    s3_client = boto3.client('s3')

    # 1. Save request image first.
    if type(file) != bytes:
        request_file = file.filename
    else:
        request_file = file['uri'].split('/')[-1]  # file path form from react-native client.
    secure_file = secure_filename(request_file)
    if not os.path.exists(secure_file):
        file.save(secure_file)

    request_path = os.path.join(os.getcwd(), 'temp', request_file)
    # request_path = os.path.join(APP_TEMP, request_file)
    if os.path.exists(secure_file):
        shutil.move(secure_file, request_path)

    # 2. Check image mime type & change if invalid.
    mime_type = check_mimetype(request_path)['mime_type'].split('/')[0]
    request_ext = check_mimetype(request_path)['mime_type'].split('/')[1]

    if request_ext in INVALID_MIMES['image']:  # or video
        original_file = heic_to_jpg(request_path)
    # elif request_ext in INVALID_MIMES['video']:
    #     original_file = video_to_mp4(request_path)
    else:
        original_file = request_path

    original_file_name = original_file.split('/')[-1]  # Insert to DB
    hashed_file_name = f"{hashlib.sha256(original_file_name.split('.')[0].encode()).hexdigest()}_{random_string}.{original_file_name.split('.')[1]}"
    hashed_file = os.path.join(os.getcwd(), 'temp', hashed_file_name)
    os.rename(original_file, hashed_file)
    # shutil.move(original_file, hashed_file)

    hashed_object_name = os.path.join(object_path, hashed_file_name)
    hashed_mime_type = check_mimetype(hashed_file)['mime_type']
    hashed_size = get_file_information(hashed_file, mime_type)['size']
    hashed_width = get_file_information(hashed_file, mime_type)['width']
    hashed_height = get_file_information(hashed_file, mime_type)['height']
    hashed_s3_pathname = os.path.join("https://circlin-app.s3.ap-northeast-2.amazonaws.com/", hashed_object_name)

    s3_client.upload_file(hashed_file, S3_BUCKET, hashed_object_name, ExtraArgs={'ContentType': mime_type})

    sql = Query.into(
        Files
    ).columns(
        Files.created_at,
        Files.updated_at,
        Files.pathname,
        Files.original_name,
        Files.mime_type,
        Files.size,
        Files.width,
        Files.height
    ).insert(
        fn.Now(),
        fn.Now(),
        hashed_s3_pathname,
        original_file_name,
        hashed_mime_type,
        hashed_size,
        hashed_width,
        hashed_height
    ).get_sql()

    cursor.execute(sql)
    connection.commit()
    original_file_id = cursor.lastrowid

    # 3. Generate resized image
    resized_file_list = generate_resized_file(hashed_file_name.split('.')[1], hashed_file, mime_type)

    for resized_path in resized_file_list:
        object_name = os.path.join(object_path, resized_path.split('/')[-1])
        resized_mime_type = check_mimetype(resized_path)['mime_type']
        resized_size = get_file_information(resized_path, mime_type)['size']
        resized_width = get_file_information(resized_path, mime_type)['width']
        resized_height = get_file_information(resized_path, mime_type)['height']
        resized_s3_pathname = os.path.join("https://circlin-app.s3.ap-northeast-2.amazonaws.com/", object_name)

        s3_client.upload_file(resized_path, S3_BUCKET, object_name, ExtraArgs={'ContentType': mime_type})

        sql = Query.into(
            Files
        ).columns(
            Files.created_at,
            Files.updated_at,
            Files.pathname,
            Files.original_name,
            Files.mime_type,
            Files.size,
            Files.width,
            Files.height,
            Files.original_file_id
        ).insert(
            fn.Now(),
            fn.Now(),
            resized_s3_pathname,
            original_file_name,
            resized_mime_type,
            resized_size,
            resized_width,
            resized_height,
            original_file_id
        ).get_sql()

        cursor.execute(sql)
        os.remove(resized_path)

    os.remove(hashed_file)
    connection.commit()
    connection.close()

    result = {'result': True, 'original_file_id': original_file_id}

    return result


def heic_to_jpg(path):
    heif_file = pyheif.read(path)
    new_image = Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        "raw",
        heif_file.mode,
        heif_file.stride,
    )

    new_path = f"{path.split('/')[-1].split('.')[0]}.jpg"
    new_image.save(new_path, "JPEG")
    if os.path.exists(path):
        os.remove(path)

    return new_path


def video_to_mp4(path):
    original_file = cv2.VideoCapture(path)
    height = int(original_file.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width = int(original_file.get(cv2.CAP_PROP_FRAME_WIDTH))

    if width % 2 != 0:
        width += 1
    else:
        pass

    if height % 2 != 0:
        height += 1
    else:
        pass

    new_path = os.path.join(os.getcwd(), 'temp', f"{path.split('/')[-1].split('.')[0]}.mp4")
    mp.VideoFileClip(path).resize((width, height)).write_videofile(new_path,
                                                                   codec='libx264',
                                                                   audio_codec='aac',  # Super important for sound
                                                                   remove_temp=True)
    # os.system(f"ffmpeg -i {path} -vf scale={width}x{height} {new_path}")

    if os.path.exists(path):
        os.remove(path)

    return new_path


def check_mimetype(path):
    result = {'mime_type': filetype.guess(path).mime}
    return result


def get_file_information(path, file_type):
    if file_type == 'image':
        image = cv2.imread(path, cv2.IMREAD_COLOR)
        height, width, channel = image.shape
    else:
        video = cv2.VideoCapture(path)
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))

    result = {
        'size': int(os.path.getsize(path)),
        'width': width,
        'height': height
    }

    return result


def generate_resized_file(extension, original_file_path, file_type):
    resized_file_list = []
    if file_type == 'image':
        original_file = cv2.imread(original_file_path, cv2.IMREAD_COLOR)
        height, width, channel = original_file.shape

        for new_width in RESIZE_WIDTHS_IMAGE:
            new_height = int(new_width * height / width)
            resized_file = cv2.resize(original_file,
                                      dsize=(new_width, new_height),
                                      interpolation=cv2.INTER_LINEAR)
            temp_path = './temp'
            original_file_name = original_file_path.split('/')[-1]
            resized_file_name = f"{original_file_name.split('.')[0]}_w{str(new_width)}.{extension}"
            resized_file_path = os.path.join(temp_path, resized_file_name)
            cv2.imwrite(resized_file_path, resized_file)
            resized_file_list.append(resized_file_path)
        # return resized_image_list
    else:
        pass
        # original_file = cv2.VideoCapture(original_file_path)
        # height = int(original_file.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # width = int(original_file.get(cv2.CAP_PROP_FRAME_WIDTH))
        #
        # for new_width in RESIZE_WIDTHS_VIDEO:
        #     if new_width % 2 != 0:
        #         new_width += 1
        #     else:
        #         pass
        #
        #     new_height = int(new_width * height / width)
        #     if new_height % 2 != 0:
        #         new_height += 1
        #     else:
        #         pass
        #
        #     temp_path = './temp'
        #     original_file_name = original_file_path.split('/')[-1]
        #     resized_file_name = f"{original_file_name.split('.')[0]}_w{str(new_width)}.{extension}"
        #     resized_file_path = os.path.join(temp_path, resized_file_name)
        #
        #     os.system(f"ffmpeg -i {original_file_path} -vf scale={new_width}x{new_height} {resized_file_path}")
        #     # mp.VideoFileClip(original_file_path).resize((new_width, new_height)).write_videofile(resized_file_path,
        #     #                                                                                      codec='libx264',
        #     #                                                                                      audio_codec='aac', # Super important for sound
        #     #                                                                                      remove_temp=True)
        #
        #     resized_file_list.append(resized_file_path)

    return resized_file_list
# endregion


# region 알림(notification)
def create_notification(target_user_id: any, notification_type: str, user_id: int,  target_table: str, target_table_id: int, target_comment_id: any, variables: any):
    # notification_type: board_like, board_comment, board_reply
    connection = db_connection()
    cursor = get_dict_cursor(connection)

    sql = Query.into(
        Notifications
    ).columns(
        Notifications.created_at,
        Notifications.updated_at,
        Notifications.target_id,
        Notifications.type,
        Notifications.user_id,
        f"{target_table}_id",
        f"{target_table}_comment_id",
        Notifications.variables
    ).insert(
        fn.Now(),
        fn.Now(),
        target_user_id,
        notification_type,
        user_id,
        target_table_id,
        target_comment_id,
        variables
    ).get_sql()

    cursor.execute(sql)
    connection.commit()
    connection.close()

    return True
# endregion


# region 푸시(push)
def send_fcm_push(target_ids: list, push_type: str, user_id: int, board_id: int, comment_id: any, push_title: str, push_body: str):
    connection = db_connection()
    cursor = get_dict_cursor(connection)

    url = 'https://fcm.googleapis.com/fcm/send'
    headers = {
        'Authorization': FIREBASE_AUTHORIZATION_KEY,
        'Content-Type': 'application/json'
    }

    # 1. target_ids 에서 유저 정보 획득
    sql = Query.from_(
        Users
    ).select(
        Users.nickname
    ).where(
        Users.id == user_id
    ).get_sql()
    cursor.execute(sql)
    user = cursor.fetchone()
    user_nickname = user['nickname']

    # 3. target별 푸시 전송
    for index, target in enumerate(target_ids):
        if target != user_id:
            # 3-1. target 정보 조회
            sql = Query.from_(
                Users
            ).select(
                Users.nickname,
                Users.device_token,
                Users.device_type,
                Users.agree_push
            ).where(
                Criterion.all([
                    Users.id == int(target),
                ])
            ).get_sql()

            cursor.execute(sql)
            target_user = cursor.fetchone()
            target_user_device_token = target_user['device_token']
            # device_token = 'ekLzPt2Qw0KOqvcB5U-s71:APA91bGuIMPMb373oPEkkNlAZW3NT5pYerdqyz2Zs5zhZG4OanQj2BJC4UdSlwbqMyeN1wbx11r1odCVO7FRABxBCVR0F4jXb8aw2P0x2eFzQA_64BJdOLE_VY1A9dNG9OM8aE1_w_ZO'
            target_user_device_type = target_user['device_type']
            target_user_push_agreement = True if target_user['agree_push'] == 1 else False

            # 3-2. 푸시 메시지 발송 요청(Firebase API)
            if target_user_push_agreement is True and target_user_device_token is not None and target_user_device_token.strip() != '':
                processed_push_body = re.sub('\\\\"', '"', push_body)  # for Firebase push text form.
                data = {
                    "registration_ids": [target_user_device_token],
                    "notification": {
                        "tag": push_type,
                        "body": processed_push_body,
                        "subtitle" if target_user_device_type == "ios" else "title": push_title,
                        "channel_id": "Circlin"
                    },
                    "priority": "high",
                    "data": {
                        "link": {
                            "route": "Sub",
                            "screen": "Board",
                            "params": {
                                "id": board_id,
                                "comment_id": comment_id
                            }
                        }
                    }
                }

                response = requests.post(
                    url=url,
                    headers=headers,
                    json=data
                ).json()

                # 4. 발송 결과 DB에 저장
                data.pop('registration_ids')
                push_body_mysql = re.sub('\r', '\\\\r', push_body)
                push_body_mysql = re.sub('\n', '\\\\n', push_body_mysql)
                data['notification']['body'] = push_body_mysql  # for mysql
                sql = Query.into(
                    PushHistories
                ).columns(
                    PushHistories.created_at,
                    PushHistories.updated_at,
                    PushHistories.target_id,
                    PushHistories.device_token,
                    PushHistories.title,
                    PushHistories.message,
                    PushHistories.type,
                    PushHistories.result,
                    PushHistories.json,
                    PushHistories.result_json
                ).insert(
                    fn.Now(),
                    fn.Now(),
                    int(target),
                    target_user_device_token,
                    push_title,
                    push_body,
                    push_type,
                    True if response['results'][0]['message_id'] else False,
                    json.dumps(data, ensure_ascii=False),
                    json.dumps(response['results'][0], ensure_ascii=False)
                ).get_sql()
                cursor.execute(sql)
            else:
                pass
        else:
            pass
    connection.commit()
    connection.close()
    return True
# endregion


def point_request(token, point: int, reason: string, type: string, food_rating_id: int):
    response = requests.post(
        f"{API_CIRCLIN}/point",
        headers={"token": token},
        json={
            "point": point,
            "reason": reason,
            "type": type,
            "id": food_rating_id
        }
    ).json()

    return response

    # result = {
    #     'result': response,
    #     'status_code': response['status_code']
    # }

   # return json.dumps(response, ensure_ascii=False)

