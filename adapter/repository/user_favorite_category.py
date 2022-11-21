import abc
from domain.user import UserFavoriteCategory
from sqlalchemy import select, delete, insert, desc


class AbstractUserFavoriteCategoryRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, new_favorite_category) -> UserFavoriteCategory:
        pass

    @abc.abstractmethod
    def get_favorites(self, user_id) -> list:
        pass

    @abc.abstractmethod
    def delete(self, new_favorite_category) -> UserFavoriteCategory:
        pass


class UserFavoriteCategoryRepository(AbstractUserFavoriteCategoryRepository):
    def __init__(self, session):
        self.session = session

    def add(self, new_favorite_category):
        sql = insert(
            UserFavoriteCategory
        ).values(
            user_id=new_favorite_category.user_id,
            mission_category_id=new_favorite_category.mission_category_id
        )
        self.session.execute(sql)

    def get_favorites(self, user_id) -> list:
        sql = select(
            UserFavoriteCategory.mission_category_id
        ).where(
            UserFavoriteCategory.user_id == user_id
        ).order_by(
            desc(UserFavoriteCategory.mission_category_id)
        )
        result = self.session.execute(sql).scalars().all()   # version2.x 스타일!
        return result

    def delete(self, favorite_category):
        sql = delete(
            UserFavoriteCategory
        ).where(
            UserFavoriteCategory.user_id == favorite_category.user_id
        ).where(
            UserFavoriteCategory.mission_category_id == favorite_category.mission_category_id
        )
        self.session.execute(sql)
