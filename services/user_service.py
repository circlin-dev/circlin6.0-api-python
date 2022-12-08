from adapter.repository.feed import AbstractFeedRepository
from adapter.repository.user_favorite_category import AbstractUserFavoriteCategoryRepository
from adapter.repository.user import AbstractUserRepository
from domain.user import UserFavoriteCategory, User
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
        return {'result': False, 'error': '이미 내 목표로 설정한 목표를 중복 추가할 수 없습니다!'}
    else:
        repo.add(new_mission_category)
        return {'result': True}


def delete_from_favorite_mission_category(mission_category_to_delete: UserFavoriteCategory, repo: AbstractUserFavoriteCategoryRepository) -> dict:
    my_category_list = repo.get_favorites(mission_category_to_delete.user_id)

    if not chosen_category(mission_category_to_delete.mission_category_id, my_category_list):
        return {'result': False, 'error': '내 목표로 설정하지 않은 목표를 삭제할 수 없습니다!'}
    else:
        repo.delete(mission_category_to_delete)
        return {'result': True}


def get_feeds_by_user(user_id: int, page_cursor: int, limit: int, feed_repo: AbstractFeedRepository) -> list:
    feeds = feed_repo.get_feeds_by_user(user_id, page_cursor, limit)
    entries: list = [dict(
        id=feed.id,
        createdAt=feed.created_at,
        body=feed.body,
        isShow=True if feed.is_hidden == 0 else False,
        images=json.loads(feed.images),
        # user=dict(
        #     id=feed.user_id,
        #     nickname=feed.nickname,
        #     profile=feed.profile_image,
        #     followed=True if feed.followed == 1 else False,
        #     # area=json.loads(feed.user_additional_information)["area"],
        #     # followers=json.loads(feed.user_additional_information)["followers"],
        #     gender=feed.gender,
        #     isBlocked=True if feed.is_blocked == 1 else False,
        #     # isChatBlocked=True if feed.is_chat_blocked == 1 else False
        # ),
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
        product=json.loads(feed.product),
        food=json.loads(feed.food),
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
        isShow=True if feed.is_hidden == 0 else False,
        images=json.loads(feed.images),
        user=dict(
            id=feed.user_id,
            nickname=feed.nickname,
            profile=feed.profile_image,
            isBlocked=True if feed.is_blocked == 1 else False,
        ),
        commentsCount=feed.comments_count,
        checksCount=feed.checks_count,
        product=json.loads(feed.product),
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
