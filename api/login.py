from . import api
from adapter.database import db_session
from adapter.orm import user_mappers
from adapter.repository.user import UserRepository
from adapter.repository.user_stat import UserStatRepository
from helper.constant import ERROR_RESPONSE
from helper.function import failed_response
from services import user_service

from flask import request
import json
from sqlalchemy.orm import clear_mappers


@api.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        params = json.loads(request.get_data())
        if 'email' not in params.keys() or params['email'] is None or params['email'].strip() == '':
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (email).'
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        elif 'password' not in params.keys() or params['password'] is None or params['password'].strip() == '':
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (password).'
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        elif 'deviceType' not in params.keys() or params['deviceType'] is None or params['deviceType'].strip() == '':
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (deviceType).'
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        else:
            email: str = params['email']
            password: str = params['password']
            device_type: str = params['deviceType']
            client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
            user_mappers()
            user_repo: UserRepository = UserRepository(db_session)
            login_email = user_service.login_by_email(email, password, device_type, client_ip, user_repo)
            clear_mappers()

            if login_email['result']:
                db_session.commit()
                db_session.close()
                return json.dumps(login_email, ensure_ascii=False), 200
            else:
                db_session.close()
                return json.dumps({key: value for key, value in login_email.items() if key != 'status_code'}, ensure_ascii=False), login_email['status_code']
    else:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[405]} ({request.method})'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 405


@api.route('/login/sns', methods=['POST'])
def login_sns():
    if request.method == 'POST':
        params = json.loads(request.get_data())
        if 'email' not in params.keys() or params['email'] is None or params['email'].strip() == '':
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (email).'
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        if 'snsName' not in params.keys() or params['snsName'] is None or params['snsName'].strip() == '':
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (snsName).'
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        elif 'snsEmail' not in params.keys():
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (snsEmail).'
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        if 'phoneNumber' not in params.keys():   # 제공에 동의하지 않은 경우가 있을 수 있으므로 null checK는 생략해야 함.
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (phoneNumber).'
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        elif 'deviceType' not in params.keys() or params['deviceType'] is None or params['deviceType'].strip() == '':
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (deviceType).'
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        else:
            email: str = params['email']
            method: str = params['snsName']
            sns_email: str or None = params['snsEmail']
            device_type: str = params['deviceType']
            phone_number: str or None = params['phoneNumber']
            client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
            user_mappers()
            user_repo: UserRepository = UserRepository(db_session)
            login_by_sns = user_service.login_by_sns(method, email, sns_email, device_type, phone_number, client_ip, user_repo)
            clear_mappers()

            if login_by_sns['result']:
                db_session.commit()
                db_session.close()
                return json.dumps(login_by_sns, ensure_ascii=False), 200
            else:
                db_session.close()
                return json.dumps({key: value for key, value in login_by_sns.items() if key != 'status_code'}, ensure_ascii=False), login_by_sns['status_code']

    else:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[405]} ({request.method})'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 405
