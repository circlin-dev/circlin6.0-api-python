import abc
from domain.board import BoardLike
from domain.user import User
from sqlalchemy import select, delete, insert, and_, text, func


class AbstractBoardLikeRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, new_like: BoardLike) -> BoardLike:
        pass

    @abc.abstractmethod
    def get_liked_record(self, board_like: BoardLike) -> BoardLike:
        pass

    @abc.abstractmethod
    def get_liked_user_list(self, board_id: int, page_cursor: int, limit: int) -> list:
        pass

    @abc.abstractmethod
    def count_number_of_like(self, board_id: int) -> int:
        pass

    @abc.abstractmethod
    def delete(self, board_like: BoardLike) -> BoardLike:
        pass


class BoardLikeRepository(AbstractBoardLikeRepository):
    def __init__(self, session):
        self.session = session

    def add(self, new_like: BoardLike):
        sql = insert(
            BoardLike
        ).values(
            board_id=new_like.board_id,
            user_id=new_like.user_id
        )
        self.session.execute(sql)

    def get_liked_record(self, board_like: BoardLike):
        sql = select(
            BoardLike
        ).where(
            and_(
                BoardLike.board_id == board_like.board_id,
                BoardLike.user_id == board_like.user_id
            )
        )
        return self.session.execute(sql).first()

    def get_liked_user_list(self, board_id: int, page_cursor: int, limit: int) -> list:
        sql = select(
            User.id,
            User.nickname,
            User.greeting,
            User.profile_image,
            func.concat(func.lpad(BoardLike.id, 15, '0')).label('cursor')
        ).select_from(
            User
        ).join(
            BoardLike, BoardLike.user_id == User.id
        ).where(
            and_(
                BoardLike.board_id == board_id,
                BoardLike.id > page_cursor
            )
        ).limit(limit)
        result = self.session.execute(sql)

        return result

    def count_number_of_like(self, board_id: int) -> int:
        sql = select(func.count(BoardLike.id)).where(BoardLike.board_id == board_id)
        total_count = self.session.execute(sql).scalar()
        return total_count

    def delete(self, board_like: BoardLike):
        sql = delete(
            BoardLike
        ).where(
            and_(
                BoardLike.board_id == board_like.board_id,
                BoardLike.user_id == board_like.user_id
            )
        )
        self.session.execute(sql)
