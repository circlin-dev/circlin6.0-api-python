from domain.block import Block
from domain.user import User

import abc
from sqlalchemy import exists, select, delete, insert, update, join, desc, and_, case, func, text


class AbstractBlockRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, user_id: int, target_id: int):
        pass

    @abc.abstractmethod
    def get_one(self, user_id: int, target_id: int) -> bool:
        pass

    @abc.abstractmethod
    def get_list(self,  user_id: int, page_cursor: int, limit: int) -> list:
        pass

    @abc.abstractmethod
    def count_number_of_blocked_user(self, user_id: int) -> int:
        pass

    @abc.abstractmethod
    def delete(self, user_id: int, target_id: int):
        pass


class BlockRepository(AbstractBlockRepository):
    def __init__(self, session):
        self.session = session

    def add(self, user_id: int, target_id: int):
        sql = insert(Block).values(user_id=user_id, target_id=target_id)
        return self.session.execute(sql)

    def get_one(self, user_id: int, target_id: int) -> bool:
        sql = select(
            exists(Block.id)
        ).where(
            and_(
                Block.user_id == user_id,
                Block.target_id == target_id
            )
        ).limit(1)
        return self.session.execute(sql).scalar()

    def get_list(self,  user_id: int, page_cursor: int, limit: int) -> list:
        sql = select(
            User.id,
            User.nickname,
            User.gender,
            User.greeting,
            User.profile_image,
            func.concat(func.lpad(Block.id, 15, '0')).label('cursor'),
        ).join(
            User, Block.target_id == User.id
        ).where(
            and_(
                Block.user_id == user_id,
                Block.id < page_cursor
            )
        ).order_by(desc(Block.created_at)).limit(limit)

        result = self.session.execute(sql).all()
        return result

    def count_number_of_blocked_user(self, user_id: int) -> int:
        sql = select(func.count(Block.id)).where(Block.user_id == user_id)
        total_count = self.session.execute(sql).scalar()
        return total_count

    def delete(self, user_id: int, target_id: int):
        sql = delete(
            Block
        ).where(
            and_(
                Block.user_id == user_id,
                Block.target_id == target_id
            )
        )
        return self.session.execute(sql)
