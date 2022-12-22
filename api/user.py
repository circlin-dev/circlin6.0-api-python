from . import api
from adapter.database import db_session
from adapter.orm import board_mappers, feed_mappers, follow_mappers, user_mappers, user_favorite_category_mappers
from adapter.repository.board import BoardRepository
from adapter.repository.chat_message import ChatMessageRepository
from adapter.repository.feed import FeedRepository
from adapter.repository.feed_like import FeedCheckRepository
from adapter.repository.follow import FollowRepository
from adapter.repository.point_history import PointHistoryRepository
from adapter.repository.user import UserRepository
from adapter.repository.user_favorite_category import UserFavoriteCategoryRepository
from domain.user import UserFavoriteCategory
from helper.constant import INITIAL_DESCENDING_PAGE_CURSOR, INITIAL_PAGE, INITIAL_PAGE_LIMIT
from helper.function import authenticate, failed_response, get_query_strings_from_request
from services import user_service
from helper.constant import ERROR_RESPONSE

from flask import request
import json
from sqlalchemy.orm import clear_mappers


@api.route('/user', methods=['GET'])
def get_user_data():
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        return json.dumps(failed_response(ERROR_RESPONSE[401]), ensure_ascii=False), 401

    if request.method == 'GET':
        feed_mappers()  # Have no idea why user_mappers() raises mapper error at number_of_feed_writer_received_point_today: int = feed_like_repo.get_point_paid_like_count(target_user)
        feed_like_repo: FeedCheckRepository = FeedCheckRepository(db_session)
        point_history_repo: PointHistoryRepository = PointHistoryRepository(db_session)
        user_repo: UserRepository = UserRepository(db_session)
        user_favorite_category_repo: UserFavoriteCategoryRepository = UserFavoriteCategoryRepository(db_session)
        chat_message_repo: ChatMessageRepository = ChatMessageRepository(db_session)
        user_data: dict = user_service.get_user_data(user_id, user_repo, user_favorite_category_repo, point_history_repo, feed_like_repo, chat_message_repo)
        clear_mappers()

        if user_data['result']:
            db_session.close()
            return json.dumps(user_data, ensure_ascii=False), 200
        else:
            db_session.close()
            return json.dumps({key: value for key, value in user_data.items() if key != 'status_code'}, ensure_ascii=False), user_data['status_code']
    else:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[405]} ({request.method})'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 405


@api.route('/users')
def get_all_users():
    user_mappers()
    repo = UserRepository(db_session)
    users = repo.get_list()
    entries = [dict(id=user.id,
                    created_at=user.created_at.strftime('%Y/%m/%d'),
                    updated_at=user.updated_at.strftime('%Y/%m/%d'),
                    nickname=user.nickname,
                    ) for user in users]
    clear_mappers()

    return json.dumps(entries, ensure_ascii=False), 200


@api.route('/user/image', methods=['PATCH', 'DELETE'])
def update_or_delete_profile_image():
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        return json.dumps(failed_response(ERROR_RESPONSE[401]), ensure_ascii=False), 401

    if request.method == 'PATCH':
        user_mappers()
        file = request.files.getlist('file')
        user_repo: UserRepository = UserRepository(db_session)
        update_profile_image = user_service.update_profile_image_by_http_method(user_id, file, user_repo)
        clear_mappers()
        if update_profile_image['result']:
            db_session.commit()
            db_session.close()
            return json.dumps(update_profile_image, ensure_ascii=False), 200
        else:
            db_session.close()
            return json.dumps({key: value for key, value in update_profile_image.items() if key != 'status_code'}, ensure_ascii=False), update_profile_image['status_code']
    elif request.method == 'DELETE':
        user_mappers()
        user_repo: UserRepository = UserRepository(db_session)
        delete_profile_image = user_service.update_profile_image_by_http_method(user_id, None, user_repo)
        clear_mappers()
        if delete_profile_image['result']:
            db_session.commit()
            db_session.close()
            return json.dumps(delete_profile_image, ensure_ascii=False), 200
        else:
            db_session.close()
            return json.dumps({key: value for key, value in delete_profile_image.items() if key != 'status_code'}, ensure_ascii=False), delete_profile_image['status_code']
    else:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[405]} ({request.method})'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 405


@api.route('/user/nickname', methods=['GET'])
def user_nickname():
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        return json.dumps(failed_response(ERROR_RESPONSE[401]), ensure_ascii=False), 401

    if request.method == 'GET':
        nickname: str = request.args.get('nickname')
        user_mappers()
        user_repo: UserRepository = UserRepository(db_session)
        nickname_exists = user_service.nickname_exists(nickname, user_repo)
        clear_mappers()
        db_session.close()

        if nickname_exists:
            error_message = f'이미 존재하는 닉네임입니다.'
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        else:
            return json.dumps({'result': True}, ensure_ascii=False), 200
    else:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[405]} ({request.method})'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 405


@api.route('/user/password', methods=['PATCH'])
def update_password():
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        return json.dumps(failed_response(ERROR_RESPONSE[401]), ensure_ascii=False), 401

    # 비밀번호 변경
    if request.method == 'PATCH':
        params = json.loads(request.get_data())

        if 'currentPassword' not in params.keys() or params['currentPassword'].strip() == '':
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (currentPassword)'
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        elif 'newPassword' not in params.keys() or params['newPassword'].strip() == '':
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (newPassword)'
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        elif 'newPasswordValidation' not in params.keys() or params['newPasswordValidation'].strip() == '':
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (newPasswordValidation)'
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        else:
            current_password: str = str(params['currentPassword'])
            new_password: str = str(params['newPassword'])
            new_password_validation: str = str(params['newPasswordValidation'])

            user_mappers()
            user_repo: UserRepository = UserRepository(db_session)
            update_user_password: dict = user_service.update_password(user_id, current_password, new_password, new_password_validation, user_repo)
            clear_mappers()

            if update_user_password['result']:
                db_session.commit()
                db_session.close()
                return json.dumps(update_user_password, ensure_ascii=False), 200
            else:
                db_session.close()
                return json.dumps({key: value for key, value in update_user_password.items() if key != 'status_code'}, ensure_ascii=False), update_user_password['status_code']
    else:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[405]} ({request.method})'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 405


@api.route('/user/password/reissue-temporary', methods=['POST'])
def issue_temporary_password():
    # 임시 비밀번호 생성 & 이메일로 통지
    if request.method == 'POST':
        params = json.loads(request.get_data())
        if 'email' not in params.keys() or params['email'] is None or params['email'].strip() == '':
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (email)'
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        else:
            user_mappers()
            email: str = params['email']
            user_repo: UserRepository = UserRepository(db_session)
            issue_temporary_password_and_send_email = user_service.issue_temporary_password_and_send_email(email, user_repo)
            clear_mappers()

            if issue_temporary_password_and_send_email['result']:
                db_session.commit()
                db_session.close()
                return json.dumps(issue_temporary_password_and_send_email, ensure_ascii=False), 200
            else:
                db_session.close()
                return json.dumps({key: value for key, value in issue_temporary_password_and_send_email.items() if key != 'status_code'}, ensure_ascii=False), issue_temporary_password_and_send_email['status_code']
    else:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[405]} ({request.method})'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 405


@api.route('/user/profile', methods=['GET', 'PATCH'])
def update_profile():
    # 닉네임 (AddInfo1)
    # 동네 (AddInfo2) => /area API로 검색 필요   ==> 카카오 검색으로 바꾸면 어떨까...
    # 성별 (AddInfo3)
    # 생년월일 (AddInfo4) -> UserStat
    # 자기소개
    pass
    # 다른 API로 뺄 것
    # 관심 카테고리 (AddInfo05)
    # 프로필 이미지 (AddInfo06)
    # 추천 유저 + 팔로잉 (AddInfo07)
    # 추천인 코드 입력 (AddInfo08) -> /user/recommended  --> user_recommend 테이블 따로 생성해서 옮기기


@api.route('/user/withdraw', methods=['DELETE'])
def withdraw():
    user_id = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        return json.dumps(failed_response(ERROR_RESPONSE[401]), ensure_ascii=False), 401

    if request.method == 'DELETE':
        params: dict = json.loads(request.get_data())
        if 'reason' not in params.keys():
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (reason)'
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        else:
            reason = params['reason']
            user_mappers()
            user_repo: UserRepository = UserRepository(db_session)
            withdrawing = user_service.withdraw(user_id, reason, user_repo)
            clear_mappers()

            if withdrawing['result']:
                db_session.commit()
                db_session.close()
                return json.dumps(withdrawing, ensure_ascii=False), 200
            else:
                db_session.close()
                return json.dumps({key: value for key, value in withdrawing.items() if key != 'status_code'}, ensure_ascii=False), withdrawing['status_code']
    else:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[405]} ({request.method})'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 405


@api.route('/user/<int:target_user_id>', methods=['GET'])
def user_page_data(target_user_id: int):
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        return json.dumps(failed_response(ERROR_RESPONSE[401]), ensure_ascii=False), 401

    if request.method == 'GET':
        user_mappers() if user_id == target_user_id else follow_mappers()

        user_repo: UserRepository = UserRepository(db_session)
        follow_repo: FollowRepository = FollowRepository(db_session)
        get_user_page_data: dict = user_service.get_a_user(user_id, target_user_id, user_repo, follow_repo)
        clear_mappers()

        if get_user_page_data['result']:
            db_session.commit()
            db_session.close()
            return json.dumps(get_user_page_data, ensure_ascii=False), 200
        else:
            db_session.close()
            return json.dumps({key: value for key, value in get_user_page_data.items() if key != 'status_code'}, ensure_ascii=False), get_user_page_data['status_code']
    else:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[405]} ({request.method})'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 405


@api.route('/user/<int:target_user_id>/favoriteCategory', methods=['GET', 'POST', 'DELETE'])
def user_favorite_category(target_user_id: int):
    user_id = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        return json.dumps(failed_response(ERROR_RESPONSE[401]), ensure_ascii=False), 401

    if target_user_id is None:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[400]} (user_id).'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 400

    if request.method == 'GET':
        user_favorite_category_mappers()
        repo = UserFavoriteCategoryRepository(db_session)
        favorite_mission_categories = user_service.get_favorite_mission_categories(target_user_id, repo)

        clear_mappers()

        result = {
            'result': True,
            'data': favorite_mission_categories
        }

        return json.dumps(result, ensure_ascii=False), 200

    elif request.method == 'POST':
        params = json.loads(request.get_data())

        if 'missionCategoryId' not in params.keys():
            error_message = f'{ERROR_RESPONSE[400]} (missionCategoryId).'
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        else:
            mission_category_id = None if params['missionCategoryId'] is None else params['missionCategoryId']
            user_favorite_category_mappers()

            repo = UserFavoriteCategoryRepository(db_session)
            new_mission_category = UserFavoriteCategory(
                id=None,
                user_id=target_user_id,
                mission_category_id=mission_category_id
            )
            added_to_favorite_categories = user_service.add_to_favorite_mission_category(new_mission_category, repo)
            clear_mappers()

            if added_to_favorite_categories['result']:
                db_session.commit()
                db_session.close()
                return json.dumps(added_to_favorite_categories, ensure_ascii=False), 200
            else:
                db_session.close()
                return json.dumps({key: value for key, value in added_to_favorite_categories.items() if key != 'status_code'}, ensure_ascii=False), added_to_favorite_categories['status_code']
    elif request.method == 'DELETE':
        params = json.loads(request.get_data())

        if 'missionCategoryId' not in params.keys():
            error_message = f'{ERROR_RESPONSE[400]} (missionCategoryId).'
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400

        mission_category_id = params['missionCategoryId']
        user_favorite_category_mappers()
        repo = UserFavoriteCategoryRepository(db_session)
        mission_category_to_delete = UserFavoriteCategory(
            id=None,
            user_id=target_user_id,
            mission_category_id=mission_category_id
        )

        delete_from_favorite_categories = user_service.delete_from_favorite_mission_category(mission_category_to_delete, repo)
        clear_mappers()

        if delete_from_favorite_categories['result']:
            db_session.commit()
            db_session.close()
            return json.dumps(delete_from_favorite_categories, ensure_ascii=False), 200
        else:
            db_session.close()
            return json.dumps({key: value for key, value in delete_from_favorite_categories.items() if key != 'status_code'}, ensure_ascii=False), delete_from_favorite_categories['status_code']

    else:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[405]} ({request.method})'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 405


@api.route('/user/<int:target_user_id>/board', methods=['GET'])
def get_user_boards(target_user_id: int):
    user_id = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        return json.dumps(failed_response(ERROR_RESPONSE[401]), ensure_ascii=False), 401

    if target_user_id is None:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[400]} (user_id).'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 400

    if request.method == 'GET':
        category_id = get_query_strings_from_request(request, 'category', 0)
        page_cursor = get_query_strings_from_request(request, 'cursor', INITIAL_DESCENDING_PAGE_CURSOR)
        limit = get_query_strings_from_request(request, 'limit', INITIAL_PAGE_LIMIT)
        page = get_query_strings_from_request(request, 'page', INITIAL_PAGE)

        board_mappers()
        repo: BoardRepository = BoardRepository(db_session)
        board_list: list = user_service.get_boards_by_user(target_user_id, category_id, page_cursor, limit, repo)
        number_of_boards: int = user_service.get_board_count_of_the_user(target_user_id, category_id, repo)
        clear_mappers()

        last_cursor: [str, None] = None if len(board_list) <= 0 else board_list[-1]['cursor']  # 배열 원소의 cursor string

        result: dict = {
            'result': True,
            'data': board_list,
            'cursor': last_cursor,
            'totalCount': number_of_boards,
        }
        db_session.close()
        return json.dumps(result, ensure_ascii=False), 200
    else:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[405]} ({request.method})'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 405


@api.route('/user/<int:target_user_id>/board/following', methods=['GET'])
def get_boards_from_following_users(target_user_id: int):
    user_id = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        return json.dumps(failed_response(ERROR_RESPONSE[401]), ensure_ascii=False), 401

    if target_user_id is None:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[400]} (user_id).'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 400

    if request.method == 'GET':
        category_id = get_query_strings_from_request(request, 'category', 0)
        page_cursor = get_query_strings_from_request(request, 'cursor', INITIAL_DESCENDING_PAGE_CURSOR)
        limit = get_query_strings_from_request(request, 'limit', INITIAL_PAGE_LIMIT)
        page = get_query_strings_from_request(request, 'page', INITIAL_PAGE)

        board_mappers()
        repo: BoardRepository = BoardRepository(db_session)
        board_list: list = user_service.get_boards_of_following_users(target_user_id, category_id, page_cursor, limit, repo)
        number_of_boards: int = user_service.get_board_count_of_following_users(target_user_id, category_id, repo)
        clear_mappers()

        last_cursor: [str, None] = None if len(board_list) <= 0 else board_list[-1]['cursor']  # 배열 원소의 cursor string

        result: dict = {
            'result': True,
            'data': board_list,
            'cursor': last_cursor,
            'totalCount': number_of_boards,
        }
        db_session.close()
        return json.dumps(result, ensure_ascii=False), 200
    else:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[405]} ({request.method})'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 405


@api.route('/user/<int:target_user_id>/feed', methods=['GET'])
def get_user_feeds(target_user_id: int):
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        return json.dumps(failed_response(ERROR_RESPONSE[401]), ensure_ascii=False), 401

    if target_user_id is None:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[400]} (user_id).'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 400

    if request.method == 'GET':
        page_cursor: int = get_query_strings_from_request(request, 'cursor', INITIAL_DESCENDING_PAGE_CURSOR)
        limit: int = get_query_strings_from_request(request, 'limit', INITIAL_PAGE_LIMIT)
        page: int = get_query_strings_from_request(request, 'page', INITIAL_PAGE)

        feed_mappers()
        feed_repo: FeedRepository = FeedRepository(db_session)
        feeds: list = user_service.get_feeds_by_user(target_user_id, user_id, page_cursor, limit, feed_repo)
        number_of_feeds: int = user_service.get_feed_count_of_the_user(target_user_id, feed_repo)
        clear_mappers()

        db_session.close()
        last_cursor: [str, None] = None if len(feeds) <= 0 else feeds[-1]['cursor']  # 배열 원소의 cursor string

        result: dict = {
            'result': True,
            'data': feeds,
            'cursor': last_cursor,
            'totalCount': number_of_feeds,
        }
        return json.dumps(result, ensure_ascii=False), 200


@api.route('/user/<int:target_user_id>/checked/feed', methods=['GET'])
def get_user_checked_feeds(target_user_id: int):
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        return json.dumps(failed_response(ERROR_RESPONSE[401]), ensure_ascii=False), 401

    if target_user_id is None:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[400]} (user_id).'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 400

    if request.method == 'GET':
        page_cursor: int = get_query_strings_from_request(request, 'cursor', INITIAL_DESCENDING_PAGE_CURSOR)
        limit: int = get_query_strings_from_request(request, 'limit', INITIAL_PAGE_LIMIT)
        page: int = get_query_strings_from_request(request, 'page', INITIAL_PAGE)

        feed_mappers()
        feed_repo: FeedRepository = FeedRepository(db_session)
        feeds: list = user_service.get_checked_feeds_by_user(target_user_id, page_cursor, limit, feed_repo)
        number_of_feeds: int = user_service.get_checked_feed_count_of_the_user(target_user_id, feed_repo)
        clear_mappers()

        db_session.close()
        last_cursor: [str, None] = None if len(feeds) <= 0 else feeds[-1]['cursor']  # 배열 원소의 cursor string

        result: dict = {
            'result': True,
            'data': feeds,
            'cursor': last_cursor,
            'totalCount': number_of_feeds,
        }
        return json.dumps(result, ensure_ascii=False), 200
