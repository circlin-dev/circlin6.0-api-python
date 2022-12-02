from helper.constant import CIRCLINOFFICIAL_USER_ID
from domain.food import FoodRating

import abc
from sqlalchemy import and_, func, select


class AbstractFoodRatingRepository(abc.ABC):
    @abc.abstractmethod
    def get_rating_list_by_food_and_user(self, food_id: int, user_id: int) -> list:
        pass


class FoodRatingRepository(AbstractFoodRatingRepository):
    def __init__(self, session):
        self.session = session

    def get_rating_list_by_food_and_user(self, food_id: int, user_id: int) -> list:
        sql = select(
            FoodRating
        ).where(
            and_(
                FoodRating.food_id == food_id,
                FoodRating.user_id == user_id
            )
        )
        result = self.session.execute(sql).all()
        return result
