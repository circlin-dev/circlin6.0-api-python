from helper.constant import CIRCLINOFFICIAL_USER_ID
from domain.food import FoodReview

import abc
from sqlalchemy import select


class AbstractFoodReviewRepository(abc.ABC):
    @abc.abstractmethod
    def get_list(self) -> list:
        pass


class FoodReviewRepository(AbstractFoodReviewRepository):
    def __init__(self, session):
        self.session = session

    def get_list(self) -> list:
        sql = select(
            FoodReview.id,
            FoodReview.value,
        ).where(FoodReview.user_id == CIRCLINOFFICIAL_USER_ID)
        result = self.session.execute(sql).all()
        return result
