from adapter.orm import point_histories
from domain.point_history import PointHistory

import abc
from sqlalchemy import and_, func, insert, or_, select, text


class AbstractPointHistoryRepository(abc.ABC):
    @abc.abstractmethod
    def get_one(self, point_history: PointHistory) -> [PointHistory, None]:
        pass

    @abc.abstractmethod
    def get_list(self, user_id: int, page_cursor: int, limit: int) -> list:
        pass

    @abc.abstractmethod
    def calculate_daily_gathered_point_by_reasons(self, user_id: int, reasons: list, date: str) -> int:
        pass

    @abc.abstractmethod
    def calculate_feed_comment_point_by_feed_id_and_user_id(self, feed_id: int, user_id: int) -> int:
        pass

    @abc.abstractmethod
    def add(self, new_point_history: PointHistory):
        pass


class PointHistoryRepository(AbstractPointHistoryRepository):
    def __init__(self, session):
        self.session = session

    def get_one(self, point_history: PointHistory) -> [PointHistory, None]:
        reason = point_history.reason
        user_id = point_history.user_id

        if "feed_check" in reason:
            feed_id = point_history.feed_id
            sql = select(
                point_histories
            ).where(
                and_(
                    point_histories.c.user_id == user_id,
                    point_histories.c.feed_id == feed_id,
                )
            )
        elif "feed_comment" in reason:
            feed_id = point_history.feed_id
            feed_comment_id = point_history.feed_comment_id
            sql = select(
                point_histories
            ).where(
                and_(
                    point_histories.c.user_id == user_id,
                    point_histories.c.feed_id == feed_id,
                    point_histories.c.feed_comment_id == feed_comment_id,
                )
            )
        elif "food" in reason:
            food_rating_id = point_history.food_rating_id
            sql = select(
                point_histories
            ).where(
                and_(
                    point_histories.c.user_id == user_id,
                    point_histories.c.food_rating_id == food_rating_id,
                )
            )
        elif "mission" in reason:
            sql = ''
        elif "order" in reason:
            sql = ''
        else:
            return None

        result = self.session.execute(sql).first()
        return result

    def get_list(self, user_id: int, page_cursor: int, limit: int) -> list:
        pass

    def calculate_daily_gathered_point_by_reasons(self, user_id: int, reasons: list, date: str) -> int:
        if date == 'today':
            sql = select(
                func.sum(point_histories.c.point)
            ).where(
                and_(
                    point_histories.c.user_id == user_id,
                    func.TIMESTAMPDIFF(text("DAY"), func.DATE(point_histories.c.created_at), func.now()) == 0,
                    point_histories.c.created_at >= func.DATE(func.now()),
                    point_histories.c.reason.in_(reasons)
                )
            )
            result = self.session.execute(sql).scalar()
            return 0 if result is None else int(result)
        elif date == 'yesterday':
            sql = select(
                func.sum(point_histories.c.point)
            ).where(
                and_(
                    point_histories.c.user_id == user_id,
                    func.TIMESTAMPDIFF(text("DAY"), func.now(), func.DATE(point_histories.c.created_at)) == -1,
                    point_histories.c.reason.in_(reasons)
                )
            )
            result = self.session.execute(sql).scalar()
            return 0 if result is None else int(result)
        else:
            return 0

    def calculate_feed_comment_point_by_feed_id_and_user_id(self, feed_id: int, user_id: int) -> int:
        sql = select(
            func.sum(point_histories.c.point).label('point')
        ).where(
            and_(
                point_histories.c.user_id == user_id,
                point_histories.c.feed_id == feed_id,
            )
        ).where(
            or_(
                point_histories.c.reason == "feed_comment_reward",
                point_histories.c.reason == "feed_comment_delete",
            )
        )
        result = self.session.execute(sql).scalars().first()
        return 0 if result is None else int(result)

    def add(self, new_point_history: PointHistory):
        sql = insert(
            point_histories
        ).values(
            created_at=func.now(),
            updated_at=func.now(),
            user_id=new_point_history.user_id,
            point=new_point_history.point,
            result=new_point_history.result,
            reason=new_point_history.reason,
            feed_id=new_point_history.feed_id,
            order_id=new_point_history.order_id,
            mission_id=new_point_history.mission_id,
            food_rating_id=new_point_history.food_rating_id,
            feed_comment_id=new_point_history.feed_comment_id
        )
        self.session.execute(sql)
