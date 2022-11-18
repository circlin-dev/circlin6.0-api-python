from adapter.orm import notifications
from domain.board import Board, BoardComment
from domain.common_code import CommonCode
from domain.feed import Feed, FeedComment, FeedImage
from domain.mission import Mission, MissionCategory, MissionComment
from domain.notification import Notification
from domain.notice import Notice, NoticeComment
from domain.user import User

import abc
import json
from sqlalchemy import and_, case, delete, desc, distinct, func, insert, select, text, update


class AbstractNotificationRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, new_notification: Notification) -> Notification:
        pass

    def get_list(self, user_id: int, page_cursor: int, limit: int) -> list:
        pass

    @abc.abstractmethod
    def count_number_of_notification(self, user_id: int) -> int:
        pass

    @abc.abstractmethod
    def update(self, **kwargs):
        pass

    @abc.abstractmethod
    def update_read_at_by_id(self, ids: list):
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
        notification_type: list = [
            'feed_check', 'feed_comment', 'feed_reply',
            'mission_like', 'mission_comment', 'mission_reply',
            'board_like',
            'board_comment',  # 'OO님 외 N명이 내 게시글에 댓글을 남겼습니다' 형식으로 보이게 하려면 주석 해제
            'board_reply',   # 'OO님 외 N명이 내 게시글에 댓글을 남겼습니다' 형식으로 보이게 하려면 주석 해제
            'notice_comment', 'notice_reply'
        ]

        sql = select(
            func.max(Notification.id).label('id'),
            func.date_format(Notification.created_at, '%Y/%m/%d %H:%i:%s').label('created_at'),
            func.count(distinct(func.ifnull(Notification.user_id, 0))).label('count'),
            # func.concat(func.year(Notification.created_at), '|', func.month(Notification.created_at), '|', func.day(Notification.created_at)).label('what'),
            Notification.target_id,
            Notification.user_id,
            User.nickname,
            User.profile_image,
            User.gender,
            case(
                (text(f"users.id IN (SELECT target_id FROM follows WHERE user_id = {user_id})"), 1),
                else_=0
            ).label('is_following'),
            func.IF(
                and_(Notification.type.in_(notification_type), func.count(distinct(func.ifnull(Notification.user_id, 0))) > 1),
                func.concat(Notification.type, '_multi'),
                Notification.type
            ).label('type'),
            func.concat(
                text(f"(SELECT mc.emoji FROM mission_categories mc WHERE mc.id=missions.mission_category_id)"),
                Mission.title
            ).label('mission_title'),
            Mission.thumbnail_image.label('mission_image'),
            Mission.is_ground,
            FeedComment.comment.label('feed_comment'),
            MissionComment.comment.label('mission_comment'),
            BoardComment.comment.label('board_comment'),
            NoticeComment.comment.label('notice_comment'),
            Notification.variables,
            func.max(Notification.feed_id).label('feed_id'),
            func.max(Notification.feed_comment_id).label('feed_comment_id'),
            func.max(Notification.mission_id).label('mission_id'),
            func.max(Notification.mission_comment_id).label('mission_comment_id'),
            func.max(Notification.mission_stat_id).label('mission_stat_id'),
            func.max(Notification.notice_id).label('notice_id'),
            func.max(Notification.notice_comment_id).label('notice_comment_id'),
            func.max(Notification.board_id).label('board_id'),
            func.max(Notification.board_comment_id).label('board_comment_id'),
            func.concat(func.lpad(Notification.id, 15, '0')).label('cursor'),
            text("(SELECT fi.image FROM feed_images fi WHERE fi.feed_id = feeds.id ORDER BY fi.order LIMIT 1)"),
            text("(SELECT fi.type FROM feed_images fi WHERE fi.feed_id = feeds.id ORDER BY fi.order LIMIT 1)"),
            # func.array_agg(),
        ).select_from(
            Notification
        ).join(
            User, User.id == Notification.user_id, isouter=True
        ).join(
            Feed, Feed.id == Notification.feed_id, isouter=True
        ).join(
            FeedComment, FeedComment.id == Notification.feed_comment_id, isouter=True
        ).join(
            Mission, Mission.id == Notification.mission_id, isouter=True
        ).join(
            MissionComment, MissionComment.id == Notification.mission_comment_id, isouter=True
        ).join(
            Board, Board.id == Notification.board_id, isouter=True
        ).join(
            BoardComment, BoardComment.id == Notification.board_comment_id, isouter=True
        ).join(
            Notice, Notice.id == Notification.notice_id, isouter=True
        ).join(
            NoticeComment, NoticeComment.id == Notification.notice_comment_id, isouter=True
        ).where(
            and_(
                Notification.target_id == user_id,
                Notification.id < page_cursor,
            )
        ).group_by(
            func.date_format(Notification.created_at, '%Y/%m/%d'),
            func.IF(
                Notification.type == 'follow',
                Notification.user_id,
                func.IF(
                    and_(Notification.type.in_(notification_type)),
                    Notification.type,
                    Notification.id
                )
            ),
            Notification.feed_id,
            Notification.mission_id,
            Notification.board_id,
            Notification.notice_id,
        ).order_by(
            desc(func.max(Notification.id))
        ).limit(limit)

        result = self.session.execute(sql)

        return result

    def count_number_of_notification(self, user_id: int) -> int:
        sql = select(
            func.count(Notification.id)
        ).where(
            Notification.target_id == user_id
        )

        return self.session.execute(sql).scalar()

    def update(self, **kwargs):
        # self.feed_id = kwargs.get('feed_id')
        # self.feed_comment_id = kwargs.get('feed_comment_id')
        # self.mission_id = kwargs.get('mission_id')
        # self.mission_comment_id = kwargs.get('mission_comment_id')
        # self.mission_stat_id = kwargs.get('mission_stat_id')
        # self.notice_id = kwargs.get('notice_id')
        # self.notice_comment_id = kwargs.get('notice_comment_id')
        # self.board_id = kwargs.get('board_id')
        # self.board_comment_id = kwargs.get('board_comment_id')
        pass

    def update_read_at_by_id(self, ids: list):
        sql = update(
            Notification
        ).where(
            and_(
                Notification.id.in_(ids),
                Notification.read_at == None
            )
        ).values(read_at=func.now())
        # sql = update(BoardComment).where(BoardComment.id == comment.id).values(comment=comment.comment)
        return self.session.execute(sql)
