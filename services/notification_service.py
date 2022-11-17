from adapter.repository.notification import AbstractNotificationRepository
from domain.notification import Notification

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
            # createdAt=notification.created_at,
            userId=notification.user_id,
            # profileImage=notification.profile_image,
            type=notification.type,
            # feedImage=notification.feed_image,
            # feedImageType=notification.feed_image_type,
            # gender=notification.gender,
            # isFollowing=notification.is_following,
            # link=notification.link,  # Must parse json to text
            # linkLeft=notification.link_left,  # Must parse json to text
            # linkRight=notification.link_right,  # Must parse json to text
            # message=notification.message,
            # missionImage=notification.mission_image,
            cursor=notification.cursor
        ) for notification in notification_list
    ]
    return entries


def get_count_of_the_notification(user_id: int, repo: AbstractNotificationRepository):
    count: int = repo.count_number_of_notification(user_id)
    return count
