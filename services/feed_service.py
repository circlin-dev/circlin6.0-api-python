from adapter.repository.feed import AbstractFeedRepository
from adapter.repository.feed_like import AbstractFeedCheckRepository
from adapter.repository.feed_comment import AbstractFeedCommentRepository
from domain.feed import Feed

import json


def get_newsfeeds(user_id: int, page_cursor: int, limit: int, feed_repo: AbstractFeedRepository) -> list:
    newsfeeds: list = feed_repo.get_newsfeeds(user_id, page_cursor, limit)
    entries: list = [dict(
        id=feed.id,
        createdAt=feed.created_at,
        body=feed.body,
        images=json.loads(feed.images),
        user=dict(
            id=feed.user_id,
            nickname=feed.nickname,
            profile=feed.profile_image,
            followed=True if feed.followed == 1 else False,
            area=json.loads(feed.user_additional_information)["area"],
            followers=json.loads(feed.user_additional_information)["followers"],
            gender=feed.gender,
            isBlocked=True if feed.is_blocked == 1 else False,
            isChatBlocked=True if feed.is_chat_blocked == 1 else False
        ),
        commentsCount=json.loads(feed.feed_additional_information)["comments_count"],
        checksCount=json.loads(feed.feed_additional_information)["checks_count"],
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
        cursor=feed.cursor,
    ) for feed in newsfeeds]

    return entries


def get_count_of_newsfeeds(user_id: int, feed_repo: AbstractFeedRepository):
    total_count = feed_repo.count_number_of_newsfeed(user_id)
    return total_count


def get_recently_most_checked_feeds(user_id: int, feed_repo: AbstractFeedRepository) -> list:
    recommendation = feed_repo.get_recently_most_checked_feeds(user_id)
    entries: list = [dict(
        id=feed.id,
        createdAt=feed.created_at,
        body=feed.body,
        images=json.loads(feed.images),
        user=dict(
            id=feed.user_id,
            nickname=feed.nickname,
            profile=feed.profile_image,
            followed=True if feed.followed == 1 else False,
            area=json.loads(feed.user_additional_information)["area"],
            followers=json.loads(feed.user_additional_information)["followers"],
            gender=feed.gender,
            isBlocked=True if feed.is_blocked == 1 else False,
            isChatBlocked=True if feed.is_chat_blocked == 1 else False
        ),
        commentsCount=json.loads(feed.feed_additional_information)["comments_count"],
        checksCount=json.loads(feed.feed_additional_information)["checks_count"],
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
        product=json.loads(feed.product)
    ) for feed in recommendation]
    return entries


def get_comment_count_of_the_feed(board_id, repo: AbstractFeedCommentRepository) -> int:
    return repo.count_number_of_comment(board_id)


def get_comments(board_id: int, page_cursor: int, limit: int, user_id: int, repo: AbstractFeedCommentRepository) -> list:
    comments: list = repo.get_list(board_id, page_cursor, limit, user_id)
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


def get_like_count_of_the_feed(feed_id: int, repo: AbstractFeedCheckRepository) -> int:
    return repo.count_number_of_like(feed_id)


def get_user_list_who_like_this_feed(feed_id: int, page_cursor: int, limit: int, repo: AbstractFeedCheckRepository) -> list:
    liked_users: list = repo.get_liked_user_list(feed_id, page_cursor, limit)
    entries: list = [dict(
        id=user.id,
        nickname=user.nickname,
        greeting=user.greeting,
        profileImage=user.profile_image,
        cursor=user.cursor
    ) for user in liked_users]

    return entries


def get_a_feed(feed_id: int, user_id: int, feed_repo: AbstractFeedRepository) -> dict:
    feed: Feed = feed_repo.get_one(feed_id, user_id)

    feed_dict = dict(
        id=feed.id,
        createdAt=feed.created_at,
        body=feed.body,
        images=[] if feed.images is None else json.loads(feed.images),
        checked=feed.checked,
        commentsCount=json.loads(feed.feed_additional_information)["comments_count"],
        checksCount=json.loads(feed.feed_additional_information)["checks_count"],
        # checkedUsers = json.loads(feed.feed_additional_information["checked_users"]),
        user=dict(
            id=feed.user_id,
            nickname=feed.nickname,
            profile=feed.profile_image,
            gender=feed.gender,
            followed=True if feed.followed == 1 else False,
            isBlocked=True if feed.is_blocked == 1 else False,
            isChatBlocked=True if feed.is_chat_blocked == 1 else False,
            area=json.loads(feed.user_additional_information)["area"],
            followers=json.loads(feed.user_additional_information)["followers"],
        ),
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
        product=json.loads(feed.product)
    ) if feed is not None else None

    return feed_dict


def update_a_feed(feed_id: int, feed_repo: AbstractFeedRepository) -> bool:
    # check_if_user_is_the_owner_of_the_feed is True && feed is not None && feed_is_undeleted is True
    pass


def delete_a_feed(feed_id: int, feed_repo: AbstractFeedRepository) -> bool:
    # check_if_user_is_the_owner_of_the_feed is True && feed is not None && feed_is_undeleted is True
    pass
