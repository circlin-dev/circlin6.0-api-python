from adapter.orm import areas, delete_users, feeds, feed_likes, notifications, point_histories, user_stats, user_wallpapers
from domain.user import User, UserFavoriteCategory, UserStat

import abc
from sqlalchemy.sql import func
from sqlalchemy import and_, insert, select, text, update


class AbstractUserRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, new_version):
        pass

    @abc.abstractmethod
    def user_data(self, user_id: int):
        pass

    @abc.abstractmethod
    def get_one(self, user_id: int) -> User:
        pass

    @abc.abstractmethod
    def get_one_by_email(self, email: str) -> User:
        pass

    @abc.abstractmethod
    def get_one_by_nickname(self, nickname: str) -> User:
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
    def update_password(self, target_user: User, decoded_hashed_new_password: str):
        pass

    @abc.abstractmethod
    def delete(self, user_id: int, reason: str or None):
        pass

    @abc.abstractmethod
    def get_push_target(self, targets: list) -> list:
        pass


class UserRepository(AbstractUserRepository):
    def __init__(self, session):
        self.session = session

    def add(self, version):
        self.session.add(version)

    def user_data(self, user_id: int):
        area = select(
            areas.c.name
        ).where(
            areas.c.code == func.concat(func.substring(User.area_code, 1, 5), '00000')
        ).limit(1)

        number_of_checks_user_did_yesterday = select(
            func.count(feed_likes.c.id)
        ).where(
            and_(
                feed_likes.c.user_id == User.id,
                feed_likes.c.deleted_at == None,
                func.TIMESTAMPDIFF(text("DAY"), func.now(), func.DATE(feed_likes.c.created_at)) == -1,
            )
        )

        number_of_checks_user_received_yesterday = select(
            func.count(feed_likes.c.id)
        ).join(
            feeds, feed_likes.c.feed_id == feeds.c.id
        ).where(
            and_(
                feeds.c.user_id == User.id,
                feed_likes.c.deleted_at == None,
                func.TIMESTAMPDIFF(text("DAY"), func.now(), func.DATE(feed_likes.c.created_at)) == -1
            )
        )

        unread_notifications_count = select(
            func.count(notifications.c.id)
        ).where(
            and_(
                notifications.c.target_id == User.id,
                notifications.c.read_at == None
            )
        )

        # unread_messages_count = ()

        sql = select(
            User.id,
            User.agree1,
            User.agree2,
            User.agree3,
            User.agree4,
            User.agree5,
            User.agree_push,
            User.agree_push_mission,
            area.label('area'),
            func.date_format(user_stats.c.birthday, '%Y/%m/%d').label('birthday'),
            User.gender,
            User.greeting,
            User.invite_code,
            User.nickname,
            User.point,
            User.profile_image,
            func.json_arrayagg(
                func.json_object(
                    'id', user_wallpapers.c.id,
                    'createdAt', func.date_format(user_wallpapers.c.created_at, '%Y/%m/%d %H:%i:%s'),
                    'title', user_wallpapers.c.title,
                    'path', user_wallpapers.c.image
                )
            ).label('wallpapers'),
            func.json_object(
                'notifications', unread_notifications_count,
                'messages', 1,
            ).label('badge'),

            number_of_checks_user_did_yesterday.label('number_of_checks_user_did_yesterday'),
            number_of_checks_user_received_yesterday.label('number_of_checks_user_received_yesterday')
        ).select_from(
            User
        ).join(
            user_stats, user_stats.c.user_id == User.id, isouter=True
        ).join(
            user_wallpapers, user_wallpapers.c.user_id == User.id, isouter=True
        ).where(
            and_(
                User.id == user_id,
                User.deleted_at == None,
            )
        ).limit(1)
        result = self.session.execute(sql).first()
        return result

    def get_one(self, user_id: int) -> User:
        sql = select(
            User
        ).where(
            and_(User.id == user_id, User.deleted_at == None)
        ).limit(1)
        user = self.session.execute(sql).scalars().first()
        return user

    def get_one_by_email(self, email: str) -> User:
        sql = select(
            User
        ).where(
            and_(User.email == email, User.deleted_at == None)
        ).limit(1)
        user = self.session.execute(sql).scalars().first()
        return user

    def get_one_by_nickname(self, nickname: str) -> User:
        sql = select(
            User
        ).where(
            and_(User.nickname == nickname, User.deleted_at == None)
        ).limit(1)
        user = self.session.execute(sql).scalars().first()
        return user

    def get_list(self):
        sql = select(User).limit(10)
        users = self.session.execute(sql).scalars().all()
        return users

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
            point=point
        )
        return self.session.execute(sql)

    def update_password(self, target_user: User, decoded_hashed_new_password: str):
        sql = update(
            User
        ).where(
            User.id == target_user.id
        ).values(
            password=decoded_hashed_new_password
        )
        return self.session.execute(sql)

    def delete(self, user_id: int, reason: str or None):
        sql = update(User).where(User.id == user_id).values(deleted_at=func.now())
        self.session.execute(sql)

        sql = insert(delete_users).values(user_id=user_id, reason=reason)
        self.session.execute(sql)
        return True

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
