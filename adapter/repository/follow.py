from adapter.orm import areas, follows
from domain.user import Follow, User

import abc
from sqlalchemy import exists, select, delete, insert, update, join, desc, and_, case, func, text
from sqlalchemy.orm import aliased


class AbstractFollowRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, user_id: int, target_id: int):
        pass

    @abc.abstractmethod
    def get_one(self, user_id: int, target_id: int) -> bool:
        pass

    @abc.abstractmethod
    def get_following_list(self,  target_id: int, user_id: int, page_cursor: int, limit: int) -> list:
        pass

    @abc.abstractmethod
    def count_number_of_following(self, user_id: int) -> int:
        pass

    @abc.abstractmethod
    def get_follower_list(self,  target_id: int, user_id: int, page_cursor: int, limit: int) -> list:
        pass

    @abc.abstractmethod
    def count_number_of_follower(self, user_id: int) -> int:
        pass

    @abc.abstractmethod
    def delete(self, user_id: int, target_id: int):
        pass


class FollowRepository(AbstractFollowRepository):
    def __init__(self, session):
        self.session = session

    def add(self, user_id: int, target_id: int):
        sql = insert(Follow).values(user_id=user_id, target_id=target_id)
        return self.session.execute(sql)

    def get_one(self, user_id: int, target_id: int) -> bool:
        sql = select(
            exists(Follow.id)
        ).where(
            and_(
                Follow.user_id == user_id,
                Follow.target_id == target_id
            )
        ).limit(1)
        return self.session.execute(sql).scalar()

    def get_following_list(self,  target_id: int, user_id: int, page_cursor: int, limit: int) -> list:
        area = select(areas.c.name).where(areas.c.code == func.concat(func.substring(User.area_code, 1, 5), '00000')).limit(1)
        follow_aliased_for_my_followings = aliased(Follow)
        follow_aliased_for_follower = aliased(Follow)
        my_followings = select(follow_aliased_for_my_followings.target_id).where(follow_aliased_for_my_followings.user_id == user_id)
        number_of_follower_of_following = select(func.count(follow_aliased_for_follower.id)).where(follow_aliased_for_follower.target_id == User.id)

        sql = select(
            User.id,
            User.nickname,
            User.gender,
            User.profile_image,
            area.label('area'),
            number_of_follower_of_following.label('followers'),
            select(True).label('followed') if target_id == user_id else
            case(
                (User.id.in_(my_followings), True),
                else_=False
            ).label("followed"),  # following에서는 target_id == user_id 면 항상 True
            func.concat(func.lpad(Follow.id, 15, '0')).label('cursor'),
        ).join(
            User, Follow.target_id == User.id
        ).where(
            and_(
                Follow.user_id == target_id,
                Follow.id < page_cursor,
                User.deleted_at == None
            )
        ).order_by(desc(User.id)).limit(limit)

        result = self.session.execute(sql).all()
        return result

    def count_number_of_following(self, target_id: int) -> int:
        sql = select(func.count(Follow.id)).join(User, Follow.user_id == User.id).where(and_(Follow.user_id == target_id, User.deleted_at == None))
        total_count = self.session.execute(sql).scalar()
        return total_count

    def get_follower_list(self, target_id: int, user_id: int, page_cursor: int, limit: int) -> list:
        area = select(areas.c.name).where(areas.c.code == func.concat(func.substring(User.area_code, 1, 5), '00000')).limit(1)
        # follow_aliased_for_followings = aliased(Follow)
        # follow_aliased_for_follower = aliased(Follow)
        # my_followings = select(follow_aliased_for_followings.target_id).where(follow_aliased_for_followings.user_id == user_id)
        # number_of_follower_of_follower = select(func.count(follow_aliased_for_follower.id)).where(follow_aliased_for_follower.target_id == User.id)

        follow_aliased_for_my_followings = aliased(Follow)
        follow_aliased_for_follower = aliased(Follow)
        my_followings = select(follow_aliased_for_my_followings.target_id).where(follow_aliased_for_my_followings.user_id == user_id)
        number_of_follower_of_follower = select(func.count(follow_aliased_for_follower.id)).where(follow_aliased_for_follower.target_id == User.id)

        sql = select(
            User.id,
            User.nickname,
            User.gender,
            User.greeting,
            User.profile_image,
            area.label('area'),
            number_of_follower_of_follower.label('followers'),
            case(
                (User.id.in_(my_followings), True),
                else_=False
            ).label("followed"),
            func.concat(func.lpad(Follow.id, 15, '0')).label('cursor'),
        ).join(
            User, Follow.user_id == User.id
        ).where(
            and_(
                Follow.target_id == target_id,
                Follow.id < page_cursor,
                User.deleted_at == None
            )
        ).order_by(desc(User.id)).limit(limit)

        result = self.session.execute(sql).all()
        return result

    def count_number_of_follower(self, target_id: int) -> int:
        sql = select(func.count(Follow.id)).join(User, Follow.target_id == User.id).where(and_(Follow.target_id == target_id, User.deleted_at == None))
        total_count = self.session.execute(sql).scalar()
        return total_count

    def delete(self, user_id: int, target_id: int):
        sql = delete(
            Follow
        ).where(
            and_(
                Follow.user_id == user_id,
                Follow.target_id == target_id
            )
        )
        return self.session.execute(sql)
