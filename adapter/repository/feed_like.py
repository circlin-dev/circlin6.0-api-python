from adapter.orm import feeds
from domain.feed import Feed, FeedCheck
from domain.user import User
from sqlalchemy import select, update, insert, and_, text, func
from sqlalchemy.sql.expression import exists

import abc


class AbstractFeedCheckRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, new_like: FeedCheck) -> FeedCheck:
        pass

    @abc.abstractmethod
    def get_one_excluding_deleted_record(self, feed_like: FeedCheck) -> FeedCheck:
        pass

    @abc.abstractmethod
    def get_one_including_deleted_record(self, feed_like: FeedCheck):
        pass

    @abc.abstractmethod
    def record_of_like_with_points_that_were_awarded_to_writer_exists(self, target_feed: Feed, user_who_likes_the_feed: User):
        pass

    @abc.abstractmethod
    def get_liked_user_list(self, feed_id: int, page_cursor: int, limit: int) -> list:
        pass

    @abc.abstractmethod
    def count_number_of_like(self, feed_id: int) -> int:
        pass

    @abc.abstractmethod
    def get_current_like_count_of_user(self, user: User) -> int:
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
            user_id=new_like.user_id,
            point=new_like.point
        )
        self.session.execute(sql)

    def get_one_excluding_deleted_record(self, feed_like: FeedCheck):
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

    def get_one_including_deleted_record(self, feed_like: FeedCheck):
        sql = select(
            FeedCheck
        ).where(
            and_(
                FeedCheck.feed_id == feed_like.feed_id,
                FeedCheck.user_id == feed_like.user_id
            )
        )
        return self.session.execute(sql).first()

    def record_of_like_with_points_that_were_awarded_to_writer_exists(self, target_feed: Feed, user_who_likes_the_feed: User):
        sql = select(
            FeedCheck
        ).join(
            Feed, Feed.id == FeedCheck.feed_id
        ).where(
            and_(
                FeedCheck.deleted_at == None,
                FeedCheck.user_id == user_who_likes_the_feed.id,
                FeedCheck.point > 0,
                func.TIMESTAMPDIFF(text("DAY"), FeedCheck.created_at, func.now()) == 0,
                FeedCheck.created_at >= func.DATE(func.now()),
                Feed.user_id == target_feed.user_id
            )
        )
        result = self.session.execute(exists(sql).select()).scalar()
        return result

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

    def get_current_like_count_of_user(self, user: User) -> int:
        sql = select(
            func.count(FeedCheck.id)
        ).where(
            and_(
                FeedCheck.user_id == user.id,
                FeedCheck.point > 0,
                FeedCheck.created_at >= func.DATE(func.now()),
                func.TIMESTAMPDIFF(text("DAY"), FeedCheck.created_at, func.now()) == 0,
                FeedCheck.deleted_at == None
            )
        )
        result = self.session.execute(sql).scalar()
        return result

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
