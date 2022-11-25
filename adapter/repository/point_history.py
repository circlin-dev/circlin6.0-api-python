from domain.point_history import PointHistory

import abc
from sqlalchemy import and_, func, select, text


class AbstractPointHistoryRepository(abc.ABC):
    @abc.abstractmethod
    def get_one(self, user_id: int, point_history: PointHistory) -> [PointHistory, None]:
        pass

    @abc.abstractmethod
    def get_list(self, user_id: int, page_cursor: int, limit: int) -> list:
        pass

    @abc.abstractmethod
    def calculate_daily_gathered_point_by_reasons(self, user_id: int, reasons: list) -> int:
        pass

    @abc.abstractmethod
    def add(self, new_point_history: PointHistory):
        pass


class PointHistoryRepository(AbstractPointHistoryRepository):
    def __init__(self, session):
        self.session = session

    def get_one(self, user_id: int, point_history: PointHistory) -> [PointHistory, None]:
        reason = point_history.reason
        user_id = point_history.user_id

        if "feed_check" in reason:
            feed_id = point_history.feed_id
            sql = select(
                PointHistory
            ).where(
                and_(
                    PointHistory.user_id == user_id,
                    PointHistory.feed_id == feed_id,
                )
            )
        elif "feed_comment" in reason:
            feed_id = point_history.feed_id
            feed_comment_id = point_history.feed_comment_id
            sql = select(
                PointHistory
            ).where(
                and_(
                    PointHistory.user_id == user_id,
                    PointHistory.feed_id == feed_id,
                    PointHistory.feed_comment_id == feed_comment_id,
                )
            )
        elif "food" in reason:
            sql = ''
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

    def calculate_daily_gathered_point_by_reasons(self, user_id: int, reasons: list) -> int:
        sql = select(
            func.sum(PointHistory.point)
        ).where(
            and_(
                PointHistory.user_id == user_id,
                func.TIMESTAMPDIFF(text("DAY"), PointHistory.created_at, func.now()) == 0,
                PointHistory.created_at >= func.DATE(func.now()),
                PointHistory.reason.in_(reasons)
            )
        )
        result = self.session.execute(sql).scalar()
        return 0 if result is None else int(result)

    def add(self, new_point_history: PointHistory):
        pass
