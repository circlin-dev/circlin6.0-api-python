from adapter.repository.board import AbstractBoardRepository
from adapter.repository.feed import AbstractFeedRepository
from adapter.repository.user_favorite_category import AbstractUserFavoriteCategoryRepository
from adapter.repository.user import AbstractUserRepository
from domain.user import UserFavoriteCategory, User
from helper.function import failed_response
import json


def get_a_user(user_id: int, repo: AbstractUserRepository) -> User:
    user: User = repo.get_one(user_id)
    return user


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
            likesCount=board.likes_count,
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
            likesCount=board.likes_count,
            liked=True if board.liked == 1 else False,
            commentsCount=board.comments_count,
            isShow=True if board.is_show == 1 else False,
            cursor=board.cursor
        ) for board in board_list
    ]
    return entries


def get_board_count_of_following_users(user_id: int, category_id: int, board_repo: AbstractBoardRepository) -> int:
    return board_repo.count_number_of_board_of_following_users(user_id, category_id)


def get_feeds_by_user(user_id: int, page_cursor: int, limit: int, feed_repo: AbstractFeedRepository) -> list:
    feeds = feed_repo.get_feeds_by_user(user_id, page_cursor, limit)
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
        checksCount=feed.checks_count,
        checked=True if feed.checked == 1 else False,
        missions=[dict(
            id=mission['id'],
            title=mission['title'] if mission['emoji'] is None else f"{mission['emoji']}{mission['title']}",
            isEvent=True if mission['is_event'] == 1 else False,
            isOldEvent=True if mission['is_old_event'] == 1 else False,
            isGround=True if mission['is_ground'] == 1 else False,
            eventType=mission['event_type'],
            thumbnail=mission['thumbnail'],
            bookmarked=True if mission['bookmarked'] == 1 else False,
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
        checksCount=feed.checks_count,
        missions=[dict(
            id=mission['id'],
            title=mission['title'] if mission['emoji'] is None else f"{mission['emoji']}{mission['title']}",
            isEvent=True if mission['is_event'] == 1 else False,
            isOldEvent=True if mission['is_old_event'] == 1 else False,
            isGround=True if mission['is_ground'] == 1 else False,
            eventType=mission['event_type'],
            thumbnail=mission['thumbnail'],
            bookmarked=True if mission['bookmarked'] == 1 else False,
        ) for mission in json.loads(feed.mission)] if json.loads(feed.mission)[0]['id'] is not None else [],
        product=json.loads(feed.product) if json.loads(feed.product)['id'] is not None else None,
        food=json.loads(feed.food) if json.loads(feed.food)['id'] is not None else None,
        cursor=feed.cursor,
    ) for feed in feeds]

    return entries


def get_checked_feed_count_of_the_user(user_id: int, feed_repo: AbstractFeedRepository) -> int:
    count = feed_repo.count_number_of_checked_feed_of_user(user_id)
    return count


def update_users_current_point(user_id, point: int, user_repo: AbstractUserRepository):
    target_user = user_repo.get_one(user_id)
    user_repo.update_current_point(target_user, int(point))
    return True
