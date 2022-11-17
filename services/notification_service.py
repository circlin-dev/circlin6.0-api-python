from adapter.repository.notification import AbstractNotificationRepository
from domain.notification import Notification
from helper.function import replace_notification_message_variable, replace_notification_link_by_type
import json


def create_notification(new_notification: Notification, notification_repo: AbstractNotificationRepository):
    notification_repo.add(new_notification)
    return True


def get_notification_list(user_id: int, page_cursor: int, limit: int, notification_repo: AbstractNotificationRepository) -> list:
    notification_list: list = notification_repo.get_list(user_id, page_cursor, limit)

    entries: list = [
        dict(
            id=notification.id,
            # ids=notification.ids,
            createdAt=notification.created_at,
            userId=notification.user_id,
            gender=notification.gender,
            isFollowing=True if notification.is_following == 1 else False,
            profileImage=notification.profile_image,
            type=notification.type,
            message=replace_notification_message_variable(
                notification['message'],
                {
                    'board_comment': notification.board_comment,
                    'count': notification.count,
                    'feed_comment': notification.feed_comment,
                    'mission_title': notification.mission_title,
                    'mission_comment': notification.mission_comment,
                    'nickname': notification.nickname,
                    'notice_comment': notification.notice_comment,
                    'point': None if notification.variables is None or 'point' not in notification.variables.keys()
                    else notification.variables['point'] * notification.count
                }
            ),
            missionImage=notification.mission_image,
            feedImage=notification[-2],
            feedImageType=notification[-1],
            variables=notification.variables,
            link=replace_notification_link_by_type(notification.type),
            # link=notification.link,  # Must parse json to text
            # linkLeft=notification.link_left,  # Must parse json to text
            # linkRight=notification.link_right,  # Must parse json to text
            cursor=notification.cursor
        ) for notification in notification_list
    ]
    return entries


def get_count_of_the_notification(user_id: int, repo: AbstractNotificationRepository):
    count: int = repo.count_number_of_notification(user_id)
    return count
