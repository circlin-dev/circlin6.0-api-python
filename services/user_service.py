from adapter.repository.board import AbstractBoardRepository
from adapter.repository.chat_message import AbstractChatMessageRepository
from adapter.repository.feed import AbstractFeedRepository
from adapter.repository.feed_like import AbstractFeedCheckRepository
from adapter.repository.follow import AbstractFollowRepository
from adapter.repository.point_history import AbstractPointHistoryRepository
from adapter.repository.user import AbstractUserRepository
from adapter.repository.user_stat import AbstractUserStatRepository
from adapter.repository.user_favorite_category import AbstractUserFavoriteCategoryRepository
from domain.user import UserFavoriteCategory, UserStat, User
from services import chat_service, point_service
from helper.constant import REASONS_HAVE_DAILY_REWARD_RESTRICTION
from helper.function import generate_token, failed_response

import bcrypt
from flask import current_app
from flask_mail import Message
import json
import random
import re
import string


# region signup
def agreed_to_all_required_consent_items(agree_terms_and_policy: bool, agree_privacy: bool, agree_location: bool) -> bool:
    return agree_terms_and_policy is True and agree_privacy is True and agree_location is True


def email_format_validation(email: str) -> bool:
    # 참고: https://dojang.io/mod/page/view.php?id=2439
    # 아래의 laravel 기존 정규식은 기존 코드. 도메인이 2자 이상 3자 이하가 아닐 경우 정규식을 통과하지 못한다.
    # ex: kunwoo.choi@youha.info (x)  |  kunwoo.choi@youha.com (O)  |  kunwoo.choi@circlin.co.kr (O)
    # pattern = re.compile('^[0-9a-zA-Z_.-]+@([KFAN]|[0-9a-zA-Z]([-_.]?[0-9a-zA-Z])*\.[a-zA-Z]{2,3})$')
    # 따라서 아래와 같이 1자 이상으로 제한을 풀어둔다.
    pattern = re.compile('^[0-9a-zA-Z_.-]+@([KFAN]|[0-9a-zA-Z]([-_.]?[0-9a-zA-Z])*\.[a-zA-Z]{1,})$')
    return True if pattern.match(email) is not None else False


def email_exists(email: str, user_repo: AbstractUserRepository) -> bool:
    result = user_repo.get_one_by_email(email)
    return True if result is not None else False


def password_format_validation(password: str) -> bool:
    # 영문 대소문자 + 특수문자 + 숫자로 이루어진 6자 이상의 문자열
    pattern = re.compile('^(?=.*[a-zA-Z])(?=.*\d)(?=.*[!@#$%^&*()])[a-zA-Z\d!@#$%^&*()]{6,}$')
    return True if pattern.match(password) is not None else False


def generate_invite_code(length: int) -> str:
    pool: str = string.digits + string.ascii_uppercase
    invite_code: str = ''
    for i in range(length):
        invite_code += random.choice(pool)
    return invite_code


def signup(
        login_method: str,
        email: str,
        password: str or None,
        sns_email: str or None,
        phone_number: str or None,
        device_type: str,
        agree_terms_and_policy: bool,
        agree_privacy: bool,
        agree_location: bool,
        agree_email_marketing: bool,
        agree_sms_marketing: bool,
        agree_advertisement: bool,
        user_repo: AbstractUserRepository,
        user_stat_repo: AbstractUserStatRepository
):
    if not agreed_to_all_required_consent_items(agree_terms_and_policy, agree_privacy, agree_location):
        error_message = '필수 동의 항목에 모두 동의해 주셔야 서비스를 이용할 수 있습니다.'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    elif not email_format_validation(email):
        error_message = "입력하신 이메일 형식이 올바르지 않습니다. 유효한 이메일임에도 불구하고 이 오류가 발생한다면, 카카오톡 채널 '써클인'으로 문의해 주시기 바랍니다."
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    elif email_exists(email, user_repo):
        error_message = '이미 가입된 이메일입니다.'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    elif login_method == 'email' and not password_format_validation(password):
        error_message = '입력하신 비밀번호 형식이 올바르지 않습니다.'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    else:
        invite_code = generate_invite_code(10)
        # 중복된 추천인 코드를 가진 유저가 생성되지 않게 하기
        while user_repo.get_one_by_invite_code(invite_code) is not None:
            invite_code = generate_invite_code(10)

        if login_method == 'email':
            # 이메일 회원가입 유저
            hashed_password = generate_hashed_password(password, 'ascii')
            decoded_hashed_password: str = decode_string(hashed_password, 'ascii')

            new_user_id = user_repo.add(
                login_method,
                email,
                decoded_hashed_password,
                sns_email,
                phone_number,
                device_type,
                agree_terms_and_policy,
                agree_privacy,
                agree_location,
                agree_email_marketing,
                agree_sms_marketing,
                agree_advertisement,
                invite_code,
            )
        else:
            # SNS 회원가입 유저
            new_user_id = user_repo.add(
                login_method,
                email,
                password,
                sns_email,
                phone_number,
                device_type,
                agree_terms_and_policy,
                agree_privacy,
                agree_location,
                agree_email_marketing,
                agree_sms_marketing,
                agree_advertisement,
                invite_code,
            )

        new_user_stat: UserStat = UserStat(
            user_id=new_user_id,
            birthday=None,
            height=None,
            weight=None,
            bmi=None,
            yesterday_feeds_count=None
        )
        user_stat_repo.add(new_user_stat)
        return {'result': True, 'userId': new_user_id}
# endregion


# region login
def login_by_email(email: str, password: str, device_type: str, client_ip: str, user_repo: AbstractUserRepository):
    target_user = user_repo.get_one_by_email(email)

    if target_user is None:
        error_message = '존재하지 않는 유저입니다. 이메일 주소를 확인 후 다시 로그인해 주세요.'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    elif target_user.login_method != 'email':
        error_message = '이메일로 가입한 유저가 아닙니다. SNS 로그인으로 시작하신 유저는 이메일로 로그인하실 수 없습니다.'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    elif not encode_password_and_check_if_same(password, target_user.password, 'ascii'):
        error_message = '비밀번호를 확인 후 다시 로그인해 주세요.'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    else:
        # user_data = user_repo.user_data(target_user.id)
        user_repo.update_info_when_email_login(target_user.id, client_ip, device_type)
        new_token = generate_token(target_user.id)
        result: dict = {
            "result": True,
            "data": new_token,
        }
        return result


def login_by_sns(
        sns_name: str,
        email: str,
        sns_email: str or None,
        device_type: str,
        phone_number: str or None,
        client_ip: str,
        user_repo: AbstractUserRepository
):
    """
    '가입하기' 혹은 '로그인하기'가 가능한 이메일과 달리, SNS는 반드시 먼저 login을 시도한 후 등록된 회원정보의 존재 여부에 따라 회원가입으로 안내해야 한다.
    :param sns_name: 사용하려는 SNS 이름(kakao, naver, apple, facebook)
    :param email: '123456@F', '1234567@K'와 같이 SNS 플랫폼별 유저 ID값 + 플랫폼 첫 알파벳 대문자로 생성하던 email값
    :param sns_email: SNS 플랫폼별 유저의 제공 동의 하에 주어지는, 'id@xxxx.com' 형태의 실제 email 주소값(facebook은 현재 항상 획득 불가)
    :param device_type: iOS, Android 기기 OS 종류
    :param phone_number: SNS 플랫폼별 유저의 제공 동의 하에 주어지는, 실제 휴대폰 번호(facebook은 현재 항상 획득 불가)
    :param client_ip:
    :param user_repo: AbstractUserRepository
    :return:
    """
    target_user = user_repo.get_one_by_email(email)
    if target_user is None:
        # 회원정보가 존재하지 않는 유저. 회원가입을 유도한다.
        error_message = '존재하지 않는 유저입니다. SNS 계정으로 회원가입 후 써클인을 이용해 보세요!'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    else:
        # 기존 유저: email, phone, loginMethod를 update해야 한다. 단, sns_email과 phone은 아래와 같이 update 조건이 있다.
        # (1) DB의 value가 null일 경우, 업데이트 한다.
        # (2) DB의 sns_email이 not null이고 새로운 sns_email과 불일치하면, 업데이트 한다.
        if phone_number is None and sns_email is None:
            pass
        elif phone_number is None and sns_email is not None:
            None if target_user.sns_email == sns_email else user_repo.update_info_when_sns_login(target_user.id, sns_email, phone_number, sns_name, client_ip, device_type)
        elif sns_email is None and phone_number is not None:
            None if target_user.phone == phone_number else user_repo.update_info_when_sns_login(target_user.id, sns_email, phone_number, sns_name, client_ip, device_type)
        else:
            user_repo.update_info_when_sns_login(target_user.id, sns_email, phone_number, sns_name, client_ip, device_type)

        new_token = generate_token(target_user.id)
        result: dict = {
            "result": True,
            "data": new_token,
        }
        return result
# endregion


# region password
def encode_string(original_string: str, method: str) -> bytes:
    return original_string.encode(method)


def decode_string(hashed_password: bytes, method: str) -> str:
    return hashed_password.decode(method)


def generate_hashed_password(original_string: str, method: str) -> bytes:
    # (1) Input string ascii 인코딩
    ascii_encoded_password = original_string.encode(method)
    # (2) 암호화
    return bcrypt.hashpw(ascii_encoded_password, bcrypt.gensalt(10))


def encode_password_and_check_if_same(password_string: str, current_password_database: str, method: str) -> bool:
    encoded_password_input: bytes = encode_string(password_string, method)
    encoded_current_password_database: bytes = encode_string(current_password_database, method)
    return bcrypt.checkpw(encoded_password_input, encoded_current_password_database)


def update_password(user_id: int, current_password_input: str, new_password_input: str, new_password_validation: str, user_repo: AbstractUserRepository) -> dict:
    target_user: User = user_repo.get_one(user_id)

    if target_user is None:
        error_message = '존재하지 않는 유저입니다.'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result

    if target_user.login_method != 'email':
        error_message = '이메일로 가입한 유저가 아닙니다. SNS 로그인으로 시작하신 유저는 비밀번호를 변경할 수 없습니다.'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    elif not encode_password_and_check_if_same(current_password_input, target_user.password, 'ascii'):
        error_message = '입력하신 현재 비밀번호가 실제 현재 비밀번호와 일치하지 않습니다. 확인 후 다시 시도해 주세요.'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    elif current_password_input == new_password_input or current_password_input == new_password_validation:
        error_message = '입력하신 새 비밀번호 또는 확인용 새 비밀번호가 입력하신 현재 비밀번호와 같습니다. 확인 후 다시 시도해 주세요.'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    elif encode_password_and_check_if_same(new_password_input, target_user.password, 'ascii') or encode_password_and_check_if_same(new_password_validation, target_user.password, 'ascii'):
        error_message = '입력하신 새 비밀번호 또는 확인용 새 비밀번호가 실제 현재 비밀번호와 같습니다. 확인 후 다시 시도해 주세요.'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    elif new_password_input != new_password_validation:
        error_message = "입력하신 '새 비밀번호'와 '확인용 새 비밀번호'가 서로 다릅니다. 동일하게 입력한 후 다시 시도해 주세요."
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    else:
        hashed_new_password_input: bytes = generate_hashed_password(new_password_input, 'ascii')
        decoded_hashed_new_password_input: str = decode_string(hashed_new_password_input, 'ascii')
        user_repo.update_password(target_user, decoded_hashed_new_password_input)
        return {'result': True}


def generate_random_password(length: int):
    pool: str = string.digits + string.ascii_letters
    random_password: str = ''
    for i in range(length):
        random_password += random.choice(pool)
    return random_password


def send_temporary_password_by_email(temp_password: str, recipients: list):
    html_message = f"""
안녕하세요, 고객님! 써클인 입니다.<br>
비밀번호 찾기를 요청하신 고객님께 임시 비밀번호를 발송 드립니다.<br><br>
임시 비밀번호: <b>{temp_password}</b><br><br>
발급해드린 임시 비밀번호를 이용하여 패스워드를 반드시 변경해주시기 바랍니다.<br>
써클인 앱에 로그인하신 후 [<b>마이페이지</b> -> <b>옵션</b> -> <b>비밀번호 변경</b>] 을 통해 패스워드를 변경하실 수 있습니다.<br><br>
<b>직접 비밀번호 찾기를 요청하신 것이 아니라면</b>,<br>
<b>카카오톡 채널 -> '써클인'</b>을 검색하셔서 채팅 상담을 통해 신고해 주시기 바랍니다.<br><br>
더욱 더 노력하는 써클인이 되겠습니다<br>
감사합니다.
"""
    message = Message(
        subject='[써클인] 임시 비밀번호 발급 안내 메일',
        html=html_message,
        sender=current_app.config.get('MAIL_USERNAME'),  # 'circlindev@circlin.co.kr',
        recipients=recipients
    )

    # <주의!> 발송 실패 시 AssertionError를 일으키고, 성공적이면 None을 리턴함.
    result = current_app.mail.send(message)
    return result


def issue_temporary_password_and_send_email(email: str, user_repo: AbstractUserRepository):
    """
    (1) 전달된 email로 get a user
    (2) login_method == 'email' 인지 확인 필요 - 아닐 경우 고객센터로 문의 유도
    (3) 임시 비밀번호 생성 (문자열 -> 인코딩 -> 암호화)
    (4) 임시 비밀번호(문자열)를 입력받은 메일로 발송
    (5) 임시 비밀번호로 비밀번호 업데이트 (암호화 -> 디코딩 -> UPDATE)

    - flask_mail로 보낼 때 다음 사항은 파악이 불가하다.
        (1) 이메일 전송 성공 여부: Google mail에서 이메일 발송 실패 여부를 받을 수는 있으나, flask_mail은 발송만 하고 발송 결과를 추적하지 않는다.
            - 따라서 유효하지 않은 이메일 주소(수신이 불가한 상태인 주소)를 구분할 수는 없다.
            - 따라서 유저가 올바르지 않은 형식의 이메일 주소(ex. invalid domain: myemail@test.com)를 입력한 상태라면,
                API 결과는 True일지라도 실제로 이메일은 발송되지 않는다.
    :param email:
    :param user_repo:
    :return:
    """

    target_user = user_repo.get_one_by_email(email)

    if target_user is None:
        error_message = '존재하지 않는 유저입니다.'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result

    elif target_user.login_method != 'email':
        error_message = "이메일로 가입한 유저가 아닙니다. 가입하신 SNS 유형이 기억나지 않으신다면 카카오톡 채널 '써클인'으로 문의해 주세요."
        result = failed_response(error_message)
        result['status_code'] = 400
        return result

    else:
        temporary_password = generate_random_password(8)
        sending_failed = send_temporary_password_by_email(temporary_password, [email])

        if not sending_failed:  # <주의!> 발송 실패 시 메시지를 리턴하고, 성공적이면 None을 리턴함.
            hashed_temporary_password: bytes = generate_hashed_password(temporary_password, 'ascii')
            decoded_temporary_password: str = decode_string(hashed_temporary_password, 'ascii')
            user_repo.update_password(target_user, decoded_temporary_password)
            return {'result': True}
        else:
            error_message = "임시 비밀번호를 발송하지 못했습니다. 이 문제가 계속 발생한다면 카카오톡 채널 '써클인'으로 문의해 주세요."
            result = failed_response(error_message)
            result['status_code'] = 500
            return result
# endregion


# region user information management
def get_a_user(user_id: int, target_id: int, user_repo: AbstractUserRepository, follow_repo: AbstractFollowRepository) -> dict:
    user: User = user_repo.get_one(target_id)

    if user is None:
        error_message = '존재하지 않는 유저입니다.'
        result = failed_response(error_message)
        result['status_code'] = 400
    else:
        if user_id == target_id:
            user_dict = dict(
                id=user.id,
                area=user.area,
                greeting=user.greeting,
                inviteCode=user.invite_code,
                nickname=user.nickname,
                point=user.point,
                profile=user.profile_image,
            ) if user is not None else None
        else:
            followed = True if follow_repo.get_one(user_id, target_id) == 1 else False
            user_dict = dict(
                id=user.id,
                area=user.area,
                greeting=user.greeting,
                inviteCode=user.invite_code,
                nickname=user.nickname,
                followed=followed,
                profile=user.profile_image,
            ) if user is not None else None
        result: dict = {
            "result": True,
            "data": user_dict
        }
    return result


# region user_data
def get_user_data(
        user_id: int,
        user_repo: AbstractUserRepository,
        user_favorite_category_repo: AbstractUserFavoriteCategoryRepository,
        point_history_repo: AbstractPointHistoryRepository,
        feed_like_repo: AbstractFeedCheckRepository,
        chat_message_repo: AbstractChatMessageRepository,
):
    """
    (1) amountOfPointsUserReceivedToday (int): 오늘 하루 ‘유저‘의 체크 행위에 의해 '유저'가 지급받은 '포인트 액수'
    (2) amountOfPointGivenToUserYesterday (int): 어제 하루 ‘유저‘의 체크를 한/받은 행위 + 댓글 이벤트에 의해 '유저'가 지급받은 '포인트 액수'
    (3) checkCountOfUserYesterday (int): 어제 하루 ‘유저‘의 체크를 한 행위 '횟수'
    (4) checkCountOfFollowersToUserYesterday (int): 어제 하루 유저가 '팔로워'에게 체크 받은 '횟수'(전일 받은 체크 수)
        - (3), (4)의 횟수 = 포인트가 지급된 체크 중 취소되지 않은 것의 수 + 포인트 지급되지 않은 체크 중 취소되지 않은 것의 수
    (5) amountOfPointUserReceivedToday: 오늘 하루 ‘유저‘가 팔로워의 '유저' 피드 체크, 피드 체크, 댓글 이벤트로 획득한 ‘포인트‘(int)
    (6) availablePointToday (int): # 오늘 ‘유저’가 팔로워의 '유저' 피드 체크, 피드 체크, 댓글 이벤트로 더 획득할 수 있는 포인트
    :param user_id: int
    :param user_repo: AbstractUserRepository
    :param user_favorite_category_repo: AbstractUserFavoriteCategoryRepository
    :param point_history_repo: AbstractPointHistoryRepository
    :param feed_like_repo: AbstractFeedCheckRepository
    :param chat_message_repo: AbstractChatMessageRepository
    :return: userData
    """

    target_user: User = user_repo.user_data(user_id)

    if target_user is None:
        error_message = '존재하지 않는 유저입니다.'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    else:
        user_favorite_categories: list = user_favorite_category_repo.get_favorites(target_user.id)
        user_favorite_categories: list = [dict(
            id=category.id,
            title=category.title
        ) for category in user_favorite_categories] if user_favorite_categories is not None else []

        number_of_feed_writer_received_point_today: int = feed_like_repo.get_point_paid_like_count(target_user)
        available_point_today, current_gathered_point = point_service.points_available_to_receive_for_the_rest_of_the_day(
            target_user.id,
            REASONS_HAVE_DAILY_REWARD_RESTRICTION,
            'today',
            point_history_repo
        )
        available_point_yesterday, yesterday_gathered_point = point_service.points_available_to_receive_for_the_rest_of_the_day(
            target_user.id,
            REASONS_HAVE_DAILY_REWARD_RESTRICTION,
            'yesterday',
            point_history_repo
        )

        unread_messages_count = chat_service.count_unread_messages_by_user(target_user.id, chat_message_repo)

        user_dict: dict = dict(
            id=target_user.id,
            area=target_user.area,
            agreeTermsAndPolicy=True if target_user.agree1 == 1 else False,
            agreePrivacy=True if target_user.agree2 == 1 else False,
            agreeLocation=True if target_user.agree3 == 1 else False,
            agreeEmailMarketing=True if target_user.agree4 == 1 else False,
            agreeSmsMarketing=True if target_user.agree5 == 1 else False,
            agreePush=True if target_user.agree_push == 1 else False,
            agreePushMission=True if target_user.agree_push_mission == 1 else False,
            agreeAdvertisement=True if target_user.agree_ad == 1 else False,
            badge=dict(notifications=target_user.unread_notifications_count, messages=unread_messages_count),
            birthday=target_user.birthday,
            category=user_favorite_categories,

            numberOfFeedWriterReceivedPointToday=number_of_feed_writer_received_point_today,
            amountOfPointsUserReceivedToday=current_gathered_point,
            availablePointToday=available_point_today,
            numberOfChecksUserDidYesterday=target_user.number_of_checks_user_did_yesterday,
            numberOfChecksUserReceivedYesterday=target_user.number_of_checks_user_received_yesterday,
            amountOfPointsGivenToUserYesterday=yesterday_gathered_point,

            gender=target_user.gender,
            greeting=target_user.greeting,
            inviteCode=target_user.invite_code,
            nickname=target_user.nickname,
            point=target_user.point,
            profile=target_user.profile_image,
            wallpapers=json.loads(target_user.wallpapers) if json.loads(target_user.wallpapers)[0]['id'] is not None else []
        )
        result = {
            'result': True,
            'data': user_dict
        }
        return result
# endregion


def nickname_exists(new_nickname: str, user_repo: AbstractUserRepository):
    user = user_repo.get_one_by_nickname(new_nickname)
    return True if user is not None else False


def update_profile_image_by_http_method(user_id: int, new_image, user_repo: AbstractUserRepository):
    if new_image is None:
        user_repo.update_profile_image(user_id, new_image)
        return {'result': True}
    else:
        pass


def withdraw(user_id: int, reason: str or None, user_repo: AbstractUserRepository):
    user_repo.delete(user_id, reason)
    return {'result': True}
# endregion


# region board
def get_boards_by_user(target_user_id: int, category_id: int, page_cursor: int, limit: int, board_repo: AbstractBoardRepository) -> list:
    board_list = board_repo.get_list_by_user(target_user_id, category_id, page_cursor, limit)
    entries = [
        dict(
            id=board.id,
            body=board.body,
            createdAt=board.created_at,
            images=json.loads(board.images) if json.loads(board.images)[0]['pathname'] is not None else [],
            user=dict(
                id=board.user_id,
                profile=board.profile_image,
                followed=True if (board.followed == 1 or board.user_id == target_user_id) else False,
                nickname=board.nickname,
                followers=board.followers,
                isBlocked=True if board.is_blocked == 1 else False,
                area=board.area,
            ) if board.user_id is not None else None,
            boardCategoryId=board.board_category_id,
            likedUsers=[dict(
                id=user['id'],
                nickname=user['nickname'],
                profile=user['profile_image']
            ) for user in json.loads(board.liked_users)] if board.liked_users is not None else [],
            liked=True if board.liked == 1 else False,
            commentsCount=board.comments_count,
            isShow=True if board.is_show == 1 else False,
            cursor=board.cursor
        ) for board in board_list
    ]
    return entries


def get_board_count_of_the_user(user_id: int, category_id: int, board_repo: AbstractBoardRepository) -> int:
    return board_repo.count_number_of_board_of_user(user_id, category_id)


def get_boards_of_following_users(target_user_id: int, category_id: int, page_cursor: int, limit: int, board_repo: AbstractBoardRepository) -> list:
    board_list = board_repo.get_list_of_following_users(target_user_id, category_id, page_cursor, limit)
    entries = [
        dict(
            id=board.id,
            body=board.body,
            createdAt=board.created_at,
            images=json.loads(board.images) if json.loads(board.images)[0]['pathname'] is not None else [],
            user=dict(
                id=board.user_id,
                profile=board.profile_image,
                followed=True if (board.followed == 1 or board.user_id == target_user_id) else False,
                nickname=board.nickname,
                followers=board.followers,
                isBlocked=True if board.is_blocked == 1 else False,
                area=board.area,
            ) if board.user_id is not None else None,
            boardCategoryId=board.board_category_id,
            likedUsers=[dict(
                id=user['id'],
                nickname=user['nickname'],
                profile=user['profile_image']
            ) for user in json.loads(board.liked_users)] if board.liked_users is not None else [],
            liked=True if board.liked == 1 else False,
            commentsCount=board.comments_count,
            isShow=True if board.is_show == 1 else False,
            cursor=board.cursor
        ) for board in board_list
    ]
    return entries


def get_board_count_of_following_users(user_id: int, category_id: int, board_repo: AbstractBoardRepository) -> int:
    return board_repo.count_number_of_board_of_following_users(user_id, category_id)
# endregion


# region feed
def get_feeds_by_user(target_user_id: int, request_user_id: int, page_cursor: int, limit: int, feed_repo: AbstractFeedRepository) -> list:
    feeds = feed_repo.get_feeds_by_user(target_user_id, request_user_id, page_cursor, limit)

    entries: list = [dict(
        id=feed.id,
        createdAt=feed.created_at,
        body=feed.body,
        distance=None if feed.distance is None
        else f'{str(round(feed.distance, 2))} L' if feed.laptime is None and feed.distance_origin is None and feed.laptime_origin is None
        else f'{round(feed.distance, 2)} km',
        images=[] if feed.images is None else json.loads(feed.images),
        isShow=True if feed.is_hidden == 0 else False,
        user=dict(
            id=feed.user_id,
            nickname=feed.nickname,
            profile=feed.profile_image,
            followed=True if feed.followed == 1 else False,
            area=feed.area,
            followers=feed.followers,
            gender=feed.gender,
            isBlocked=True if feed.is_blocked == 1 else False,
            isChatBlocked=True if feed.is_chat_blocked == 1 else False
        ) if feed.user_id is not None else None,
        commentsCount=feed.comments_count,
        checkedUsers=[dict(
            id=user['id'],
            nickname=user['nickname'],
            profile=user['profile_image']
        ) for user in json.loads(feed.checked_users)] if feed.checked_users is not None else [],
        checked=True if feed.checked == 1 else False,
        missions=[dict(
            id=mission['id'],
            title=mission['title'] if mission['emoji'] is None else f"{mission['emoji']}{mission['title']}",
            isEvent=True if mission['is_event'] == 1 else False,
            isOldEvent=True if mission['is_old_event'] == 1 else False,
            isGround=True if mission['is_ground'] == 1 else False,
            eventType=mission['event_type'],
            thumbnail=mission['thumbnail'],
            bookmarked=True if mission['bookmarked'] == 1 else False
        ) for mission in json.loads(feed.mission)] if json.loads(feed.mission)[0]['id'] is not None else [],
        product=json.loads(feed.product) if json.loads(feed.product)['id'] is not None else None,
        food=json.loads(feed.food) if json.loads(feed.food)['id'] is not None else None,
        cursor=feed.cursor,
    ) for feed in feeds]

    return entries


def get_feed_count_of_the_user(user_id: int, feed_repo: AbstractFeedRepository) -> int:
    count = feed_repo.count_number_of_feed_of_user(user_id)
    return count


def get_checked_feeds_by_user(user_id: int, page_cursor: int, limit: int, feed_repo: AbstractFeedRepository) -> list:
    feeds: list = feed_repo.get_checked_feeds_by_user(user_id, page_cursor, limit)
    entries: list = [dict(
        id=feed.id,
        createdAt=feed.created_at,
        body=feed.body,
        distance=None if feed.distance is None
        else f'{str(round(feed.distance, 2))} L' if feed.laptime is None and feed.distance_origin is None and feed.laptime_origin is None
        else f'{round(feed.distance, 2)} km',
        images=[] if feed.images is None else json.loads(feed.images),
        isShow=True if feed.is_hidden == 0 else False,
        user=dict(
            id=feed.user_id,
            area=feed['area'],
            followers=feed.followers,
            nickname=feed.nickname,
            profile=feed.profile_image,
            isBlocked=True if feed.is_blocked == 1 else False,
        ) if feed.user_id is not None else None,
        commentsCount=feed.comments_count,
        checkedUsers=[dict(
            id=user['id'],
            nickname=user['nickname'],
            profile=user['profile_image'],
        ) for user in json.loads(feed.checked_users)] if feed.checked_users is not None else [],
        missions=[dict(
            id=mission['id'],
            title=mission['title'] if mission['emoji'] is None else f"{mission['emoji']}{mission['title']}",
            isEvent=True if mission['is_event'] == 1 else False,
            isOldEvent=True if mission['is_old_event'] == 1 else False,
            isGround=True if mission['is_ground'] == 1 else False,
            eventType=mission['event_type'],
            thumbnail=mission['thumbnail'],
            bookmarked=True if mission['bookmarked'] == 1 else False
        ) for mission in json.loads(feed.mission)] if json.loads(feed.mission)[0]['id'] is not None else [],
        product=json.loads(feed.product) if json.loads(feed.product)['id'] is not None else None,
        food=json.loads(feed.food) if json.loads(feed.food)['id'] is not None else None,
        cursor=feed.cursor,
    ) for feed in feeds]

    return entries


def get_checked_feed_count_of_the_user(user_id: int, feed_repo: AbstractFeedRepository) -> int:
    count = feed_repo.count_number_of_checked_feed_of_user(user_id)
    return count
# endregion


# region mission
def chosen_category(category_id: int, my_category_list: list) -> bool:
    return category_id in my_category_list


def get_favorite_mission_categories(user_id: int, repo) -> list:
    my_category_list = repo.get_favorites(user_id)
    return my_category_list


def add_to_favorite_mission_category(new_mission_category: UserFavoriteCategory, repo: AbstractUserFavoriteCategoryRepository) -> dict:
    my_category_list = repo.get_favorites(new_mission_category.user_id)

    if chosen_category(new_mission_category.mission_category_id, my_category_list):
        error_message = f"이미 내 목표로 설정한 목표를 중복 추가할 수 없습니다!"
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    else:
        repo.add(new_mission_category)
        return {'result': True}


def delete_from_favorite_mission_category(mission_category_to_delete: UserFavoriteCategory, repo: AbstractUserFavoriteCategoryRepository) -> dict:
    my_category_list = repo.get_favorites(mission_category_to_delete.user_id)

    if not chosen_category(mission_category_to_delete.mission_category_id, my_category_list):
        error_message = '내 목표로 설정하지 않은 목표를 삭제할 수 없습니다!'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    else:
        repo.delete(mission_category_to_delete)
        return {'result': True}
# endregion


# region point
def update_users_current_point(user_id, point: int, user_repo: AbstractUserRepository):
    target_user = user_repo.get_one(user_id)
    user_repo.update_current_point(target_user, int(point))
    return True
# endregion
