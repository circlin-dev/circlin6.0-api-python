from adapter.orm import mission_categories, user_favorite_categories
from domain.user import UserFavoriteCategory
import abc
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
            mission_categories.c.id,
            mission_categories.c.emoji,
            mission_categories.c.title,
        ).join(
            user_favorite_categories, user_favorite_categories.c.mission_category_id == mission_categories.c.id
        ).where(
            user_favorite_categories.c.user_id == user_id
        )
        result = self.session.execute(sql).all()   # version2.x 스타일!
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
