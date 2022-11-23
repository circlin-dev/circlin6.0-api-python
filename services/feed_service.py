from adapter.repository.feed import AbstractFeedRepository
from adapter.repository.feed_comment import AbstractFeedCommentRepository

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
        ) for mission in json.loads(feed.mission)],
        product=json.loads(feed.product),
        cursor=feed.cursor,
    ) for feed in newsfeeds]

    return entries


def get_count_of_newsfeeds(user_id: int, feed_repo: AbstractFeedRepository):
    total_count = feed_repo.count_number_of_newsfeed(user_id)
    return total_count


def get_recently_most_checked_feeds(feed_repo: AbstractFeedRepository):
    pass


def get_feeds_by_mission(mission_id: int, feed_repo: AbstractFeedRepository):
    pass


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