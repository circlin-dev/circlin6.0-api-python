from domain.food import FoodRatingReview

import abc
from sqlalchemy import insert


class AbstractFoodRatingReviewRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, food_id: int, food_review_ids: list):
        pass


class FoodRatingReviewRepository(AbstractFoodRatingReviewRepository):
    def __init__(self, session):
        self.session = session

    def add(self, food_rating_id: int, food_review_ids: list):
        for review_id in food_review_ids:
            sql = insert(
                FoodRatingReview
            ).values(food_rating_id=food_rating_id, food_review_id=int(review_id))
            self.session.execute(sql)
        return True
