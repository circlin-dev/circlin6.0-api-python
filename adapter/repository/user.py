import abc
from domain.user import User, UserFavoriteCategory
from sqlalchemy.sql import func
from sqlalchemy import select, and_, update


class AbstractUserRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, new_version):
        pass

    @abc.abstractmethod
    def get_one(self, user_id) -> User:
        pass

    @abc.abstractmethod
    def get_list(self) -> User:
        pass

    @abc.abstractmethod
    def update(self, target_user, nickname) -> User:
        pass

    @abc.abstractmethod
    def update_current_point(self, target_user: User, point: int):
        pass

    @abc.abstractmethod
    def delete(self, target_user) -> User:
        pass

    @abc.abstractmethod
    def get_push_target(self, targets: list) -> list:
        pass


class UserRepository(AbstractUserRepository):
    def __init__(self, session):
        self.session = session

    def add(self, version):
        self.session.add(version)

    def get_one(self, user_id):
        sql = select(
            User
        ).where(
            and_(
                User.id == user_id,
                User.deleted_at == None
            )
        ).limit(1)
        result = self.session.execute(sql).scalars().first()
        return result

    def get_list(self):
        sql = select(User).limit(10)
        result = self.session.execute(sql).scalars().all()
        return result

    def update(self, target_user, nickname):
        return self.session.query(User).filter_by(id=target_user.id).update(
            {
                "nickname": nickname,
            },
            synchronize_session="fetch"
        )

    def update_current_point(self, target_user: User, point: int):
        sql = update(
            User
        ).where(
            User.id == target_user.id
        ).values(
            point=target_user.point + point
        )
        return self.session.execute(sql)

    def delete(self, target_user):
        return self.session.query(User).filter_by(id=target_user.id).update(
            {
                "deleted_at": func.Now()
            },
            synchronize_session="fetch"
        )

    def get_push_target(self, targets: list) -> list:
        sql = select(
            User.id,
            User.nickname,
            User.device_token,
            User.device_type
        ).where(
            and_(
                User.id.in_(targets),
                User.device_token != None,
                User.device_token != '',
                User.agree_push == 1
            )
        )

        push_targets: list = self.session.execute(sql).all()
        return push_targets
