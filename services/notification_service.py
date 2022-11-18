from adapter.repository.common_code import AbstractCommonCodeRepository
from adapter.repository.notification import AbstractNotificationRepository
from domain.notification import Notification
from helper.function import replace_notification_message_variable, replace_notification_link_by_type
import json


def create_notification(new_notification: Notification, notification_repo: AbstractNotificationRepository):
    notification_repo.add(new_notification)
    return True


def get_notification_list(user_id: int, page_cursor: int, limit: int, notification_repo: AbstractNotificationRepository, common_code_repo: AbstractCommonCodeRepository) -> list:
    notification_list: list = notification_repo.get_list(user_id, page_cursor, limit)
    get_message_template_with_notification_type: dict = common_code_repo.get_content_by_large_category('notifications')

    read_notification_ids = []
    entries: list = []
    for notification in notification_list:
        message_type: str = get_message_template_with_notification_type[notification.type]
        value_dict_for_link: dict = {
                "target_id": notification.target_id,
                "user_id": notification.user_id,
                "feed_id": notification.feed_id,
                "feed_comment_id": notification.feed_comment_id,
                "mission_id": notification.mission_id,
                "mission_comment_id": notification.mission_comment_id,
                "is_ground": True if notification.is_ground == 1 else False,
                "notice_id": notification.notice_id,
                "notice_comment_id": notification.notice_comment_id,
                "board_id": notification.board_id,
                "board_comment_id": notification.board_comment_id,
        }
        value_dict_for_message: dict = {
            'board_comment': notification.board_comment,
            'count': notification.count,
            'feed_comment': notification.feed_comment,
            'mission_title': notification.mission_title,
            'mission_comment': notification.mission_comment,
            'nickname': notification.nickname,
            'notice_comment': notification.notice_comment,
            'point': None if notification.variables is None or 'point' not in notification.variables.keys()
            else notification.variables['point'] * notification.count,
            'point2': None if notification.variables is None or 'point2' not in notification.variables.keys()
            else notification.variables['point2']
        }

        read_notification_ids.append(notification.id)  # 응답 속도 저하가 발생한다면 notification.read_at is None 인 것만 append하는 것으로 코드 변경하기.
        entries.append(dict(
            id=notification.id,
            createdAt=notification.created_at,
            userId=notification.user_id,
            gender=notification.gender,
            isFollowing=True if notification.is_following == 1 else False,
            profileImage=notification.profile_image,
            type=notification.type,
            message=replace_notification_message_variable(message_type, value_dict_for_message), # notification['message']
            missionImage=notification.mission_image,
            feedImage=notification[-2],
            feedImageType=notification[-1],
            variables=notification.variables,
            link=replace_notification_link_by_type('center', notification.type, value_dict_for_link),
            linkLeft=replace_notification_link_by_type('left', notification.type, value_dict_for_link),
            linkRight=replace_notification_link_by_type('right',notification.type, value_dict_for_link),
            cursor=notification.cursor
        ))

    update_notification_as_read(read_notification_ids, notification_repo)
    return entries


def get_count_of_the_notification(user_id: int, notification_repo: AbstractNotificationRepository):
    count: int = notification_repo.count_number_of_notification(user_id)
    return count


def update_notification_as_read(ids: list, notification_repo: AbstractNotificationRepository):
    notification_repo.update_read_at_by_id(ids)
    return True
