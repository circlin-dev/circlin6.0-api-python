from domain.feed import FeedComment
from domain.user import User
import abc
from sqlalchemy import select, delete, insert, update, join, desc, and_, case, func, text


class AbstractFeedCommentRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, new_comment: FeedComment) -> int:
        pass

    @abc.abstractmethod
    def get_one(self, feed_comment_id: int) -> FeedComment:
        pass

    @abc.abstractmethod
    def get_list(self, feed_id: int, page_cursor: int, limit: int, user_id: int) -> list:
        pass

    @abc.abstractmethod
    def update(self, comment: FeedComment):
        pass

    @abc.abstractmethod
    def delete(self, comment: FeedComment):
        pass

    @abc.abstractmethod
    def count_number_of_comment(self, feed_id: int) -> int:
        pass

    @abc.abstractmethod
    def get_maximum_comment_group_value(self, feed_id: int) -> int or None:
        pass

    @abc.abstractmethod
    def get_users_who_belonged_to_same_comment_group(self, feed_id: int, group: int) -> int or None:
        pass

    @abc.abstractmethod
    def get_a_root_comment_by_feed_and_comment_group(self, feed_id: int, group: int) -> int:
        pass


class FeedCommentRepository(AbstractFeedCommentRepository):
    def __init__(self, session):
        self.session = session

    def add(self, new_comment: FeedComment) -> int:
        sql = insert(
            FeedComment
        ).values(
            feed_id=new_comment.feed_id,
            user_id=new_comment.user_id,
            group=new_comment.group,
            depth=new_comment.depth,
            comment=new_comment.comment
        )
        result = self.session.execute(sql)  # =====> inserted row의 id값을 반환해야 한다.

        return result.inserted_primary_key[0]

    def get_one(self, feed_comment_id: int) -> FeedComment:
        sql = select(FeedComment).where(FeedComment.id == feed_comment_id)
        result = self.session.execute(sql).scalars().first()
        return result

    def get_list(self, feed_id: int, page_cursor: int, limit: int, user_id: int) -> list:
        sql = select(
            FeedComment.id,
            func.date_format(FeedComment.created_at, '%Y/%m/%d %H:%i:%s').label('created_at'),
            FeedComment.group,
            FeedComment.depth,
            FeedComment.comment,
            FeedComment.user_id,
            case(
                (text(f"feed_comments.user_id IN (SELECT target_id FROM blocks WHERE user_id = {user_id})"), 1),
                else_=0
            ).label('is_blocked'),
            User.nickname,
            User.gender,
            User.profile_image,
            func.concat(func.lpad(FeedComment.group, 15, '0')).label('cursor')
        ).select_from(
            FeedComment
        ).join(
            User, FeedComment.user_id == User.id
        ).where(
            and_(
                FeedComment.feed_id == feed_id,
                FeedComment.deleted_at == None,
                FeedComment.group < page_cursor
            )
        ).order_by(desc(FeedComment.group), FeedComment.depth, FeedComment.created_at).limit(limit)
        result = self.session.execute(sql)
        return result

    def update(self, comment: FeedComment):
        sql = update(FeedComment).where(FeedComment.id == comment.id).values(comment=comment.comment)
        return self.session.execute(sql)

    def delete(self, comment: FeedComment):
        sql = update(FeedComment).where(FeedComment.id == comment.id).values(deleted_at=func.now())
        return self.session.execute(sql)

    def count_number_of_comment(self, feed_id: int) -> int:
        sql = select(
            func.count(FeedComment.id)
        ).where(
            and_(
                FeedComment.feed_id == feed_id,
                FeedComment.deleted_at == None
            )
        )
        total_count = self.session.execute(sql).scalar()
        return total_count

    def get_maximum_comment_group_value(self, feed_id: int) -> int or None:
        sql = select(
            func.max(FeedComment.group).label('max_group')
        ).where(
            and_(
                FeedComment.feed_id == feed_id,
                FeedComment.deleted_at == None
            )
        )
        maximum_comment_group_value: [int, None] = self.session.execute(sql).scalar()
        return maximum_comment_group_value

    def get_users_who_belonged_to_same_comment_group(self, feed_id: int, group: int) -> list:
        sql = select(
            FeedComment.user_id
        ).where(
            and_(
                FeedComment.feed_id == feed_id,
                FeedComment.group == group
            )
        )
        commented_users: list = self.session.execute(sql).scalars().all()
        return commented_users

    def get_a_root_comment_by_feed_and_comment_group(self, feed_id: int, group: int) -> int or None:
        sql = select(
            FeedComment.user_id
        ).where(
            and_(
                FeedComment.feed_id == feed_id,
                FeedComment.group == group,
                FeedComment.depth == 0
            )
        )
        commented_user: int or None = self.session.execute(sql).scalars().first()
        return commented_user
