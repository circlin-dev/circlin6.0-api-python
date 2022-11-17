from adapter.orm import notifications
from domain.notification import Notification
from sqlalchemy import select, update, delete, insert, desc, and_, case, text, func

import abc
import json


class AbstractNotificationRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, new_notification: Notification) -> Notification:
        pass

    def get_list(self, user_id: int, page_cursor: int, limit: int) -> list:
        pass

    @abc.abstractmethod
    def count_number_of_notification(self, user_id: int) -> int:
        pass


class NotificationRepository(AbstractNotificationRepository):
    def __init__(self, session):
        self.session = session

    def add(self, new_notification: Notification) -> Notification:
        # new_notification.variables에 None을 mysql에에 저장하려 시도하면  null이 아니라 'null'로 string으로 저장되는 문제가 있어 분기 처리.
        if new_notification.variables is None:
            sql = insert(
                notifications
            ).values(
                target_id=new_notification.target_id,
                type=new_notification.type,
                user_id=new_notification.user_id,
                feed_id=new_notification.feed_id,
                feed_comment_id=new_notification.feed_comment_id,
                mission_id=new_notification.mission_id,
                mission_comment_id=new_notification.mission_comment_id,
                mission_stat_id=new_notification.mission_stat_id,
                notice_id=new_notification.notice_id,
                notice_comment_id=new_notification.notice_comment_id,
                board_id=new_notification.board_id,
                board_comment_id=new_notification.board_comment_id,
                read_at=new_notification.read_at,
            )
        else:
            sql = insert(
                notifications
            ).values(
                target_id=new_notification.target_id,
                type=new_notification.type,
                user_id=new_notification.user_id,
                feed_id=new_notification.feed_id,
                feed_comment_id=new_notification.feed_comment_id,
                mission_id=new_notification.mission_id,
                mission_comment_id=new_notification.mission_comment_id,
                mission_stat_id=new_notification.mission_stat_id,
                notice_id=new_notification.notice_id,
                notice_comment_id=new_notification.notice_comment_id,
                board_id=new_notification.board_id,
                board_comment_id=new_notification.board_comment_id,
                read_at=new_notification.read_at,
                variables=new_notification.variables
            )

        return self.session.execute(sql)

    def get_list(self, user_id: int, page_cursor: int, limit: int) -> list:
        sql = select(
            Notification.id,
            Notification.target_id,
            Notification.user_id,
            Notification.type,
            func.concat(func.lpad(Notification.id, 15, '0')).label('cursor'),
            # func.array_agg(),
            # text("CONCAT(LPAD(notifications.id, 15, '0')) AS 'cursor'")  # cursor
        ).where(
            Notification.target_id == user_id
        ).order_by(desc(Notification.id))

        result = self.session.execute(sql)

        return result

    def count_number_of_notification(self, user_id: int) -> int:
        sql = select(
            func.count(Notification.id)
        ).where(
            Notification.target_id == user_id
        )

        return self.session.execute(sql).scalar()
