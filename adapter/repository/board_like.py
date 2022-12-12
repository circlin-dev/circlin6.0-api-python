from adapter.orm import areas, follows
from domain.board import BoardLike
from domain.user import User
from sqlalchemy import case, desc, select, delete, insert, and_, text, func

import abc


class AbstractBoardLikeRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, new_like: BoardLike) -> BoardLike:
        pass

    @abc.abstractmethod
    def get_liked_record(self, board_like: BoardLike) -> BoardLike:
        pass

    @abc.abstractmethod
    def get_liked_user_list(self, board_id: int, user_id: int, page_cursor: int, limit: int) -> list:
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

    def get_liked_user_list(self, board_id: int, user_id: int, page_cursor: int, limit: int) -> list:
        followings = select(follows.c.target_id).where(follows.c.user_id == user_id)
        sql = select(
            User.id,
            User.nickname,
            User.gender,
            User.profile_image,
            case(
                (User.id.in_(followings), True),
                else_=False
            ).label("followed"),
            select(func.count(follows.c.id)).where(follows.c.target_id == User.id).label('followers'),
            select(areas.c.name).where(areas.c.code == func.concat(func.substring(User.area_code, 1, 5), '00000')).limit(1).label('area'),
            func.row_number().over(
                order_by=[
                    desc(
                        case(
                            (User.id.in_(followings), True),
                            else_=False
                        )
                    )
                ]
            ).label('cursor')
        ).select_from(
            User
        ).join(
            BoardLike, BoardLike.user_id == User.id
        ).where(
            and_(
                BoardLike.board_id == board_id,
                BoardLike.id > page_cursor
            )
        ).order_by(
            desc('followed'),
            'cursor'
        )
        candidate = self.session.execute(sql)
        result = [data for data in candidate if data.cursor > page_cursor][:limit]

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
