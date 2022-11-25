import abc
from domain.feed import FeedCheck
from domain.user import User
from sqlalchemy import select, update, insert, and_, text, func


class AbstractFeedCheckRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, new_like: FeedCheck) -> FeedCheck:
        pass

    @abc.abstractmethod
    def get_liked_record(self, feed_like: FeedCheck) -> FeedCheck:
        pass

    @abc.abstractmethod
    def get_liked_user_list(self, feed_id: int, page_cursor: int, limit: int) -> list:
        pass

    @abc.abstractmethod
    def count_number_of_like(self, feed_id: int) -> int:
        pass

    @abc.abstractmethod
    def delete(self, feed_like: FeedCheck) -> FeedCheck:
        pass


class FeedCheckRepository(AbstractFeedCheckRepository):
    def __init__(self, session):
        self.session = session

    def add(self, new_like: FeedCheck):
        sql = insert(
            FeedCheck
        ).values(
            feed_id=new_like.feed_id,
            user_id=new_like.user_id
        )
        self.session.execute(sql)

    def get_liked_record(self, feed_like: FeedCheck):
        sql = select(
            FeedCheck
        ).where(
            and_(
                FeedCheck.feed_id == feed_like.feed_id,
                FeedCheck.user_id == feed_like.user_id,
                FeedCheck.deleted_at == None
            )
        )
        return self.session.execute(sql).first()

    def get_liked_user_list(self, feed_id: int, page_cursor: int, limit: int) -> list:
        sql = select(
            User.id,
            User.nickname,
            User.greeting,
            User.profile_image,
            func.concat(func.lpad(FeedCheck.id, 15, '0')).label('cursor')
        ).select_from(
            User
        ).join(
            FeedCheck, FeedCheck.user_id == User.id
        ).where(
            and_(
                FeedCheck.feed_id == feed_id,
                FeedCheck.id > page_cursor,
                FeedCheck.deleted_at == None
            )
        ).limit(limit)
        result = self.session.execute(sql)

        return result

    def count_number_of_like(self, feed_id: int) -> int:
        sql = select(func.count(FeedCheck.id)).where(FeedCheck.feed_id == feed_id, FeedCheck.deleted_at == None)
        total_count = self.session.execute(sql).scalar()
        return total_count

    def delete(self, feed_like: FeedCheck):
        sql = update(
            FeedCheck
        ).values(FeedCheck.deleted_at, func.now()).where(
            and_(
                FeedCheck.feed_id == feed_like.feed_id,
                FeedCheck.user_id == feed_like.user_id
            )
        )
        self.session.execute(sql)
