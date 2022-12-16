from adapter.repository.board import AbstractBoardRepository
from adapter.repository.feed import AbstractFeedRepository
from adapter.repository.feed_like import AbstractFeedCheckRepository
from adapter.repository.point_history import AbstractPointHistoryRepository
from adapter.repository.user_favorite_category import AbstractUserFavoriteCategoryRepository
from adapter.repository.user import AbstractUserRepository
from domain.user import UserFavoriteCategory, User
from services import point_service
from helper.constant import REASONS_HAVE_DAILY_REWARD_RESTRICTION
from helper.function import failed_response

import bcrypt
import json


def get_user_data(
        user_id: int,
        user_repo: AbstractUserRepository,
        user_favorite_category_repo: AbstractUserFavoriteCategoryRepository,
        point_history_repo: AbstractPointHistoryRepository,
        feed_like_repo: AbstractFeedCheckRepository
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


        # amount_of_points_user_received_by_check_today = point_history_repo.calculate_daily_gathered_point_by_reasons(target_user.id, [])
        # sql = select(
        #     func.sum(point_histories.c.point)
        # ).where(
        #     and_(
        #         point_histories.c.user_id == user_id,
        #         func.TIMESTAMPDIFF(text("DAY"), point_histories.c.created_at, func.now()) == 0,
        #         point_histories.c.created_at >= func.DATE(func.now()),
        #         point_histories.c.reason.in_(reasons)
        #     )
        # )
        # result = self.session.execute(sql).scalar()

        user_dict: dict = dict(
            id=target_user.id,
            area=target_user.area,
            agree1=True if target_user.agree1 == 1 else False,
            agree2=True if target_user.agree2 == 1 else False,
            agree3=True if target_user.agree3 == 1 else False,
            agree4=True if target_user.agree4 == 1 else False,
            agree5=True if target_user.agree5 == 1 else False,
            agreePush=True if target_user.agree_push == 1 else False,
            agreePushMission=True if target_user.agree_push_mission == 1 else False,
            badge=json.loads(target_user.badge),
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


def get_a_user(user_id: int, repo: AbstractUserRepository) -> User:
    user: User = repo.get_one(user_id)
    return user


# region authentication
def encode_string(string: str, method: str) -> bytes:
    return string.encode(method)


def decode_string(hashed_password: bytes, method: str) -> str:
    return hashed_password.decode(method)


def generate_hashed_password(string: str, method: str) -> bytes:
    # (1) Input string ascii 인코딩
    ascii_encoded_password = string.encode(method)
    # (2) 암호화
    return bcrypt.hashpw(ascii_encoded_password, bcrypt.gensalt(10))


def encode_password_and_check_if_same(password_string: str, current_password_database: str, method: str) -> bool:
    # (1) Input string, DB string ascii 인코딩
    encoded__password_input: bytes = encode_string(password_string, method)
    encoded_current_password_database: bytes = encode_string(current_password_database, method)
    return bcrypt.checkpw(encoded__password_input, encoded_current_password_database)


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
            nickname=feed.nickname,
            profile=feed.profile_image,
            isBlocked=True if feed.is_blocked == 1 else False,
        ) if feed.user_id is not None else None,
        commentsCount=feed.comments_count,
        checkedUsers=[dict(
            id=user['id'],
            nickname=user['nickname'],
            profile=user['profile_image']
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
