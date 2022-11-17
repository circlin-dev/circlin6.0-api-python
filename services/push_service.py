from adapter.repository.push import AbstractPushHistoryRepository
from domain.push import PushHistory
from helper.constant import FIREBASE_AUTHORIZATION_KEY

import json
import re
import requests


def send_fcm_push(device_type: str, push_message: PushHistory, push_history_repo: AbstractPushHistoryRepository):
    url: str = 'https://fcm.googleapis.com/fcm/send'
    headers: dict = {
        'Authorization': FIREBASE_AUTHORIZATION_KEY,
        'Content-Type': 'application/json'
    }
    push_type: str = push_message.type
    device_token: str = push_message.device_token
    push_title: str = push_message.title
    push_body: str = push_message.message
    link_data: dict = push_message.json

    push_body_for_fcm: str = re.sub('\\\\"', '"', push_body)  # for Firebase push text form.
    data: dict = {
        "registration_ids": [device_token],
        "notification": {
            "tag": push_type,
            "body": push_body_for_fcm,
            "subtitle" if device_type == "ios" else "title": push_title,
            "channel_id": "Circlin"
        },
        "priority": "high",
        "data": {
            "link": link_data
        }
    }

    response = requests.post(
        url=url,
        headers=headers,
        json=data
    ).json()

    data.pop('registration_ids')
    # push_body_for_database = re.sub('\r', '\\\\r', push_body)
    # push_body_for_database = re.sub('\n', '\\\\n', push_body_for_database)
    # data['notification']['body'] = push_body_for_database  # for mysql
    data['notification']['body'] = push_body

    push_message.result = 1 if response['results'][0]['message_id'] else 0
    push_message.json = data  # json.dumps(data, ensure_ascii=False)
    push_message.json['data']['link'] = link_data[0]
    push_message.result_json = response['results'][0]  # json.dumps(response['results'][0], ensure_ascii=False)

    push_history_repo.add(push_message)

    return True
