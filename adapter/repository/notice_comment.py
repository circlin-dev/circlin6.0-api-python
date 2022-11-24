from domain.notice import NoticeComment
from domain.user import User
import abc
from sqlalchemy import select, delete, insert, update, join, desc, and_, case, func, text


class AbstractNoticeCommentRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, new_comment: NoticeComment) -> int:
        pass

    @abc.abstractmethod
    def get_one(self, notice_comment_id: int) -> NoticeComment:
        pass

    @abc.abstractmethod
    def get_list(self,  notice_id: int, page_cursor: int, limit: int, user_id: int) -> list:
        pass

    @abc.abstractmethod
    def update(self, comment: NoticeComment):
        pass

    @abc.abstractmethod
    def delete(self, comment: NoticeComment):
        pass

    @abc.abstractmethod
    def count_number_of_comment(self, notice_id: int) -> int:
        pass

    @abc.abstractmethod
    def get_maximum_comment_group_value(self, notice_id: int) -> int or None:
        pass

    @abc.abstractmethod
    def get_users_who_belonged_to_same_comment_group(self, notice_id: int, group: int) -> int or None:
        pass


class NoticeCommentRepository(AbstractNoticeCommentRepository):
    def __init__(self, session):
        self.session = session

    def add(self, new_comment: NoticeComment) -> int:
        sql = insert(
            NoticeComment
        ).values(
            notice_id=new_comment.notice_id,
            user_id=new_comment.user_id,
            group=new_comment.group,
            depth=new_comment.depth,
            comment=new_comment.comment
        )
        result = self.session.execute(sql)  # =====> inserted row의 id값을 반환해야 한다.

        return result.inserted_primary_key[0]

    def get_one(self, notice_comment_id: int) -> NoticeComment:
        sql = select(
            NoticeComment.id,
            NoticeComment.notice_id,
            NoticeComment.user_id,
            NoticeComment.group,
            NoticeComment.depth,
            NoticeComment.comment,
            NoticeComment.deleted_at
        ).where(NoticeComment.id == notice_comment_id)
        result = self.session.execute(sql).first()
        return result

    def get_list(self, notice_id: int, page_cursor: int, limit: int, user_id: int) -> list:
        sql = select(
            NoticeComment.id,
            func.date_format(NoticeComment.created_at, '%Y/%m/%d %H:%i:%s').label('created_at'),
            NoticeComment.group,
            NoticeComment.depth,
            NoticeComment.comment,
            NoticeComment.user_id,
            case(
                (text(f"notice_comments.user_id IN (SELECT target_id FROM blocks WHERE user_id = {user_id})"), 1),
                else_=0
            ).label('is_blocked'),
            User.nickname,
            User.gender,
            User.profile_image,
            func.concat(func.lpad(NoticeComment.group, 15, '0')).label('cursor')
        ).select_from(
            NoticeComment
        ).join(
            User, NoticeComment.user_id == User.id
        ).where(
            and_(
                NoticeComment.notice_id == notice_id,
                NoticeComment.deleted_at == None,
                NoticeComment.group < page_cursor
            )
        ).order_by(desc(NoticeComment.group), NoticeComment.depth, NoticeComment.created_at).limit(limit)
        result = self.session.execute(sql)
        return result

    def update(self, comment: NoticeComment):
        sql = update(NoticeComment).where(NoticeComment.id == comment.id).values(comment=comment.comment)
        return self.session.execute(sql)

    def delete(self, comment: NoticeComment):
        sql = update(NoticeComment).where(NoticeComment.id == comment.id).values(deleted_at=func.now())
        return self.session.execute(sql)

    def count_number_of_comment(self, notice_id: int) -> int:
        sql = select(
            func.count(NoticeComment.id)
        ).where(
            and_(
                NoticeComment.notice_id == notice_id,
                NoticeComment.deleted_at == None
            )
        )
        total_count = self.session.execute(sql).scalar()
        return total_count

    def get_maximum_comment_group_value(self, notice_id: int) -> int or None:
        sql = select(
            func.max(NoticeComment.group).label('max_group')
        ).where(
            and_(
                NoticeComment.notice_id == notice_id,
                NoticeComment.deleted_at == None
            )
        )
        maximum_comment_group_value: [int, None] = self.session.execute(sql).scalar()
        return maximum_comment_group_value

    def get_users_who_belonged_to_same_comment_group(self, notice_id: int, group: int) -> list:
        sql = select(
            NoticeComment.user_id
        ).where(
            and_(
                NoticeComment.notice_id == notice_id,
                NoticeComment.group == group
            )
        )
        commented_users: list = self.session.execute(sql).scalars().all()
        return commented_users
