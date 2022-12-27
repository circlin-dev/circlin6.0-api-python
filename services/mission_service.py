from adapter.repository.feed import AbstractFeedRepository
from adapter.repository.mission import AbstractMissionRepository
from adapter.repository.mission_category import AbstractMissionCategoryRepository
from adapter.repository.mission_comment import AbstractMissionCommentRepository
from adapter.repository.mission_stat import AbstractMissionStatRepository
from domain.mission import MissionCategory
from helper.constant import INITIAL_ASCENDING_PAGE_CURSOR, INITIAL_PAGE_LIMIT

import json
import random


def get_missions_by_category(user_id: int, category_id: int or None, page_cursor: int, limit: int, sort: str, mission_repo: AbstractMissionRepository, mission_stat_repo: AbstractMissionStatRepository):
    missions = mission_repo.get_list_by_category(user_id, category_id, page_cursor, limit, sort)
    entries = [dict(
        id=mission.id,
        title=mission.title,
        category=json.loads(mission.category),
        description=mission.description,
        thumbnail=mission.thumbnail_image,
        createdAt=mission.created_at,
        startedAt=mission.started_at,
        endedAt=mission.ended_at,
        reserveStartedAt=mission.reserve_started_at,
        status=mission.status,
        reserveEndedAt=mission.reserve_ended_at,
        type=mission.mission_type if mission.mission_type is not None else 'normal',
        producer=json.loads(mission.producer),
        bookmarkedUsersProfile=[
            dict(
                id=user.id,
                gender=user.gender,
                profile=user.profile_image,
                nickname=user.nickname,
            )
            for user in mission_repo.get_participants(mission.id, user_id, INITIAL_ASCENDING_PAGE_CURSOR, INITIAL_PAGE_LIMIT)[-2:]
            if user.id not in [json.loads(mission.producer)['id'], 4340, 2]
        ],
        bookmarksCount=mission.bookmarks_count,
        bookmarked=True if mission_stat_repo.get_one_excluding_ended(user_id, mission.id) else False,
        commentsCount=mission.comments_count,
        missionProducts=json.loads(mission.mission_products) if mission.mission_products is not None else [],  # mission.refund_products와 쿼리가 달라 결과값의 데이터 형태가 다르다.
        refundProducts=json.loads(mission.refund_products) if json.loads(mission.refund_products)[0]['id'] is not None else [],
        bookmarkLimit=mission.user_limit,
        hasPlayground=True if mission.has_playground == 1 else False,
        cursor=mission.cursor
    ) for mission in missions] if missions is not None else []

    return entries


def count_number_of_mission_by_category(category_id: int, mission_repo: AbstractMissionRepository):
    total_count = mission_repo.count_number_of_mission_by_category(category_id)
    return total_count


# region mission participants
def get_mission_participant_list(mission_id: int, user_id: int, page_cursor: int, limit: int, mission_repo: AbstractMissionRepository):
    participants: list = mission_repo.get_participants(mission_id, user_id, page_cursor, limit)
    entries: list = [dict(
        id=participant.id,
        nickname=participant.nickname,
        gender=participant.gender,
        profile=participant.profile_image,
        followed=participant.followed,
        followers=participant.followers,
        cursor=participant.cursor
    ) for participant in participants] if participants is not None else []
    return entries


def count_number_of_mission_participant(mission_id: int, mission_repo: AbstractMissionRepository):
    total_count: int = mission_repo.count_number_of_participants(mission_id)
    return total_count
# endregion


# region category
def get_mission_categories(mission_category_repo: AbstractMissionCategoryRepository, favorite_mission_categories: list):
    category_list = mission_category_repo.get_list()

    entries = [dict(id=category.id,
                    key=str(category.id),
                    missionCategoryId=category.mission_category_id,
                    title=category.title,
                    emoji=category.emoji if category.emoji is not None else '',
                    description=category.description if category.description is not None else '',
                    isFavorite=True if category.id in favorite_mission_categories else False
                    ) for category in category_list]
    return entries
# endregion


# region comments
def get_comment_count_of_the_mission(mission_id, mission_comment_repo: AbstractMissionCommentRepository) -> int:
    return mission_comment_repo.count_number_of_comment(mission_id)


def get_comments(mission_id: int, page_cursor: int, limit: int, user_id: int, mission_comment_repo: AbstractMissionCommentRepository) -> list:
    comments: list = mission_comment_repo.get_list(mission_id, page_cursor, limit, user_id)
    entries: list = [
        dict(
            id=comment.id,
            createdAt=comment.created_at,
            group=comment.group,
            depth=comment.depth,
            comment=comment.comment,
            userId=comment.user_id,
            isBlocked=True if comment.is_blocked == 1 else False,
            nickname=comment.nickname,
            profile=comment.profile_image,
            gender=comment.gender,
            cursor=comment.cursor
        ) for comment in comments
    ]
    return entries
# endregion


# region feeds
def get_feeds_by_mission(mission_id: int, page_cursor: int, limit: int, user_id: int, feed_repo: AbstractFeedRepository, mission_stat_repo: AbstractMissionStatRepository) -> list:
    feeds = feed_repo.get_feeds_by_mission(mission_id, user_id, page_cursor, limit)
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
        missions=[dict(
            id=mission['id'],
            title=mission['title'] if mission['emoji'] is None else f"{mission['emoji']}{mission['title']}",
            isEvent=True if mission['is_event'] == 1 else False,
            isOldEvent=True if mission['is_old_event'] == 1 else False,
            isGround=True if mission['is_ground'] == 1 else False,
            eventType=mission['event_type'],
            thumbnail=mission['thumbnail'],
            bookmarked=True if mission_stat_repo.get_one_excluding_ended(user_id, mission['id']) else False
        ) for mission in json.loads(feed.mission)] if json.loads(feed.mission)[0]['id'] is not None else [],
        checkedUsers=[dict(
            id=user['id'],
            nickname=user['nickname'],
            profile=user['profile_image']
        ) for user in json.loads(feed.checked_users)] if feed.checked_users is not None else [],
        checked=True if feed.checked == 1 else False,
        product=json.loads(feed.product) if json.loads(feed.product)['id'] is not None else None,
        food=json.loads(feed.food) if json.loads(feed.food)['id'] is not None else None,
        cursor=feed.cursor,
    ) for feed in feeds]
    return entries


def get_feed_count_of_the_mission(mission_id: int, feed_repo: AbstractFeedRepository) -> int:
    count = feed_repo.count_number_of_feed_of_mission(mission_id)
    return count
# endregion
