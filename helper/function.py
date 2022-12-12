from adapter.orm import user_mappers
from adapter.repository.user import UserRepository
from helper.constant import JWT_AUDIENCE, SLACK_NOTIFICATION_WEBHOOK
from flask import abort
import json
import jwt
import re
import requests
from sqlalchemy.orm import clear_mappers


# region authentication
def authenticate(request, session):
    token = request.headers.get('token')
    uid: int = jwt.decode(token, audience=JWT_AUDIENCE, options={"verify_signature": False})['uid']
    try:
        user_mappers()
        repo: UserRepository = UserRepository(session)
        user = repo.get_one(user_id=uid)
        clear_mappers()

        if user is None:
            return None
        else:
            return int(user.id)
    except Exception as e:
        abort(500, e)
# endregion


# region response
def failed_response(error_message: str) -> dict:
    return {"result": False, "error": error_message}


def slack_error_notification(
        endpoint: str,
        error_message: str,
        ip: str,
        method: str,
        status_code: int,
        type: str,
):
    send_notification_request = requests.post(
        SLACK_NOTIFICATION_WEBHOOK,
        json.dumps({
            "channel": "#circlin-log",
            "username": "써클인 server(python flask)",
            "method": method,
            "text": f"*[경고]* *서버에서 예측하지 못한 오류가 발생했습니다.* \n \
- Status code: `{status_code}` \n \
- HTTP method: `{method}` \n \
- 장애 API: `{endpoint}` \n \
- 장애 유형: `{type}` \n \
- IP: `{ip}` \n \
```에러 로그: {error_message}```",
            "icon_url": "https://www.circlin.co.kr/new/assets/favicon/apple-icon-180x180.png"
        }, ensure_ascii=False).encode('utf-8')
    )

    return send_notification_request
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


# region notification  # service layer로 옮겨야 할까...? 전역적으로 사용하는 게 아니라면 굳이 여기 있을 필요 없을듯.
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


