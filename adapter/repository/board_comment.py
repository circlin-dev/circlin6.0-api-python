import abc
from domain.board import BoardComment
from domain.user import User
from sqlalchemy import select, delete, insert, update, join, desc, and_, case, func, text


class AbstractBoardCommentRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, new_comment: BoardComment) -> int:
        pass

    @abc.abstractmethod
    def get_one(self, board_comment_id: int) -> BoardComment:
        pass

    @abc.abstractmethod
    def get_list(self,  board_id: int, page_cursor: int, limit: int, user_id: int) -> list:
        pass

    @abc.abstractmethod
    def update(self, comment: BoardComment):
        pass

    @abc.abstractmethod
    def delete(self, comment: BoardComment):
        pass

    @abc.abstractmethod
    def count_number_of_comment(self, board_id: int) -> int:
        pass

    @abc.abstractmethod
    def get_maximum_comment_group_value(self, board_id: int) -> int or None:
        pass

    @abc.abstractmethod
    def get_users_who_belonged_to_same_comment_group(self, board_id: int, group: int) -> int or None:
        pass


class BoardCommentRepository(AbstractBoardCommentRepository):
    def __init__(self, session):
        self.session = session

    def add(self, new_comment: BoardComment) -> int:
        sql = insert(
            BoardComment
        ).values(
            board_id=new_comment.board_id,
            user_id=new_comment.user_id,
            group=new_comment.group,
            depth=new_comment.depth,
            comment=new_comment.comment
        )
        result = self.session.execute(sql)  # =====> inserted row의 id값을 반환해야 한다.

        return result.inserted_primary_key[0]

    def get_one(self, board_comment_id: int) -> BoardComment:
        sql = select(
            BoardComment.id,
            BoardComment.board_id,
            BoardComment.user_id,
            BoardComment.group,
            BoardComment.depth,
            BoardComment.comment,
            BoardComment.deleted_at
        ).where(BoardComment.id == board_comment_id)
        result = self.session.execute(sql).first()
        return result

    def get_list(self, board_id: int, page_cursor: int, limit: int, user_id: int) -> list:
        sql = select(
            BoardComment.id,
            func.date_format(BoardComment.created_at, '%Y/%m/%d %H:%i:%s').label('created_at'),
            BoardComment.group,
            BoardComment.depth,
            BoardComment.comment,
            BoardComment.user_id,
            case(
                (text(f"board_comments.user_id IN (SELECT target_id FROM blocks WHERE user_id = {user_id})"), 1),
                else_=0
            ).label('is_blocked'),
            User.nickname,
            User.gender,
            User.profile_image,
            func.concat(func.lpad(BoardComment.group, 15, '0')).label('cursor')
        ).select_from(
            BoardComment
        ).join(
            User, BoardComment.user_id == User.id
        ).where(
            and_(
                BoardComment.board_id == board_id,
                BoardComment.deleted_at == None,
                BoardComment.group < page_cursor
            )
        ).order_by(desc(BoardComment.group), BoardComment.depth, BoardComment.created_at).limit(limit)
        result = self.session.execute(sql)
        return result

    def update(self, comment: BoardComment):
        sql = update(BoardComment).where(BoardComment.id == comment.id).values(comment=comment.comment)
        return self.session.execute(sql)

    def delete(self, comment: BoardComment):
        sql = update(BoardComment).where(BoardComment.id == comment.id).values(deleted_at=func.now())
        return self.session.execute(sql)

    def count_number_of_comment(self, board_id: int) -> int:
        sql = select(
            func.count(BoardComment.id)
        ).where(
            and_(
                BoardComment.board_id == board_id,
                BoardComment.deleted_at == None
            )
        )
        total_count = self.session.execute(sql).scalar()
        return total_count

    def get_maximum_comment_group_value(self, board_id: int) -> int or None:
        sql = select(
            func.max(BoardComment.group).label('max_group')
        ).where(
            and_(
                BoardComment.board_id == board_id,
                BoardComment.deleted_at == None
            )
        )
        maximum_comment_group_value: [int, None] = self.session.execute(sql).scalar()
        return maximum_comment_group_value

    def get_users_who_belonged_to_same_comment_group(self, board_id: int, group: int) -> list:
        sql = select(
            BoardComment.user_id
        ).where(
            and_(
                BoardComment.board_id == board_id,
                BoardComment.group == group
            )
        )
        commented_users: list = self.session.execute(sql).scalars().all()
        return commented_users
