from adapter.orm import food_reviews
from helper.constant import CIRCLINOFFICIAL_USER_ID
from domain.food import FoodReview

import abc
from sqlalchemy import insert, select


class AbstractFoodReviewRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, word: str, user_id: int) -> int:
        pass

    @abc.abstractmethod
    def get_one(self, word: str) -> FoodReview:
        pass

    @abc.abstractmethod
    def get_list(self) -> list:
        pass


class FoodReviewRepository(AbstractFoodReviewRepository):
    def __init__(self, session):
        self.session = session

    def add(self, word: str, user_id: int) -> int:
        sql = insert(
            food_reviews
        ).values(value=word, user_id=user_id)
        result = self.session.execute(sql)
        return result.inserted_primary_key[0]

    def get_one(self, word: str) -> FoodReview:
        sql = select(
            food_reviews
        ).where(
            food_reviews.c.value == word
        )
        return self.session.execute(sql).first()

    def get_list(self) -> list:
        sql = select(
            FoodReview.id,
            FoodReview.value,
        ).where(FoodReview.user_id == CIRCLINOFFICIAL_USER_ID)
        result = self.session.execute(sql).all()
        return result
