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


@api.route('/signup', methods=['POST'])
def signup():
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
        elif 'agreeTermsAndPolicy' not in params.keys() or params['agreeTermsAndPolicy'] is None:
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (agreeTermsAndPolicy).'  # 서비스 이용약관
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        elif 'agreePrivacy' not in params.keys() or params['agreePrivacy'] is None:
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (agreePrivacy).'  # 개인정보 이용 약관
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        elif 'agreeLocation' not in params.keys() or params['agreeLocation'] is None:
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (agreeLocation).'  # 위치정보 이용
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        elif 'agreeEmailMarketing' not in params.keys() or params['agreeEmailMarketing'] is None:
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (agreeEmailMarketing).'  # 이메일 마케팅 수신
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        elif 'agreeSmsMarketing' not in params.keys() or params['agreeSmsMarketing'] is None:
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (agreeSmsMarketing).'  # SMS 마케팅 수신
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        elif 'agreeAdvertisement' not in params.keys() or params['agreeAdvertisement'] is None:
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (agreeAdvertisement).'  # 광고 수신
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        else:
            email: str = params['email']
            password: str = params['password']
            device_type: str = params['deviceType']
            agree_terms_and_policy: bool = params['agreeTermsAndPolicy']
            agree_privacy: bool = params['agreePrivacy']
            agree_location: bool = params['agreeLocation']
            agree_email_marketing: bool = params['agreeEmailMarketing']
            agree_sms_marketing: bool = params['agreeSmsMarketing']
            agree_advertisement: bool = params['agreeAdvertisement']

            user_mappers()
            user_repo: UserRepository = UserRepository(db_session)
            user_stat_repo: UserStatRepository = UserStatRepository(db_session)
            signup = user_service.signup(
                login_method='email',
                email=email,
                password=password,
                sns_email=None,
                phone_number=None,
                device_type=device_type,
                agree_terms_and_policy=agree_terms_and_policy,
                agree_privacy=agree_privacy,
                agree_location=agree_location,
                agree_email_marketing=agree_email_marketing,
                agree_sms_marketing=agree_sms_marketing,
                agree_advertisement=agree_advertisement,
                user_repo=user_repo,
                user_stat_repo=user_stat_repo
            )
            clear_mappers()
            if signup['result']:
                db_session.commit()
                db_session.close()
                return json.dumps(signup, ensure_ascii=False), 200
            else:
                db_session.close()
                return json.dumps({key: value for key, value in signup.items() if key != 'status_code'}, ensure_ascii=False), signup['status_code']
    else:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[405]} ({request.method})'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 405


@api.route('/signup/sns', methods=['POST'])
def signup_sns():
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
        if 'snsEmail' not in params.keys():   # 페이스북 로그인의 경우 이메일을 제공받지 못하고 있고, 다른 SNS 수단도 제공에 동의하지 않은 경우가 있을 수 있으므로 null checK는 생략해야 함.
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (snsEmail).'
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        if 'phoneNumber' not in params.keys():   # 제공에 동의하지 않은 경우가 있을 수 있으므로 null checK는 생략해야 함.
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (phoneNumber).'
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        elif 'agreeTermsAndPolicy' not in params.keys() or params['agreeTermsAndPolicy'] is None:
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (agreeTermsAndPolicy).'  # 서비스 이용약관
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        elif 'agreePrivacy' not in params.keys() or params['agreePrivacy'] is None:
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (agreePrivacy).'  # 개인정보 이용 약관
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        elif 'agreeLocation' not in params.keys() or params['agreeLocation'] is None:
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (agreeLocation).'  # 위치정보 이용
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        elif 'agreeEmailMarketing' not in params.keys() or params['agreeEmailMarketing'] is None:
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (agreeEmailMarketing).'  # 이메일 마케팅 수신
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        elif 'agreeSmsMarketing' not in params.keys() or params['agreeSmsMarketing'] is None:
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (agreeSmsMarketing).'  # SMS 마케팅 수신
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        elif 'agreeAdvertisement' not in params.keys() or params['agreeAdvertisement'] is None:
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (agreeAdvertisement).'  # 광고 수신
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        else:
            email: str = params['email']
            method: str = params['snsName']
            sns_email: str = params['snsEmail']
            device_type: str = params['deviceType']
            phone_number: str = params['phoneNumber']
            agree_terms_and_policy: bool = params['agreeTermsAndPolicy']
            agree_privacy: bool = params['agreePrivacy']
            agree_location: bool = params['agreeLocation']
            agree_email_marketing: bool = params['agreeEmailMarketing']
            agree_sms_marketing: bool = params['agreeSmsMarketing']
            agree_advertisement: bool = params['agreeAdvertisement']

            user_mappers()
            user_repo: UserRepository = UserRepository(db_session)
            user_stat_repo: UserStatRepository = UserStatRepository(db_session)
            sns_signup = user_service.signup(
                login_method=method,
                email=email,
                password=None,  # password
                sns_email=sns_email,
                phone_number=phone_number,
                device_type=device_type,
                agree_terms_and_policy=agree_terms_and_policy,
                agree_privacy=agree_privacy,
                agree_location=agree_location,
                agree_email_marketing=agree_email_marketing,
                agree_sms_marketing=agree_sms_marketing,
                agree_advertisement=agree_advertisement,
                user_repo=user_repo,
                user_stat_repo=user_stat_repo
            )
            clear_mappers()
            if sns_signup['result']:
                db_session.commit()
                db_session.close()
                return json.dumps(sns_signup, ensure_ascii=False), 200
            else:
                db_session.close()
                return json.dumps({key: value for key, value in sns_signup.items() if key != 'status_code'}, ensure_ascii=False), sns_signup['status_code']
    else:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[405]} ({request.method})'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 405
