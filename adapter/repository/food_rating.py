from domain.food import FoodRating

import abc
from sqlalchemy import and_, func, insert, select


class AbstractFoodRatingRepository(abc.ABC):
    @abc.abstractmethod
    def get_rating_list_by_food_and_user(self, food_id: int, user_id: int) -> list:
        pass

    @abc.abstractmethod
    def add(self, food_rating: FoodRating) -> int:
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

    def add(self, food_rating: FoodRating) -> int:
        if food_rating.body is None:
            sql = insert(
                FoodRating
            ).values(
                food_id=food_rating.food_id,
                user_id=food_rating.user_id,
                rating=food_rating.rating
            )
        else:
            sql = insert(
                FoodRating
            ).values(
                food_id=food_rating.food_id,
                user_id=food_rating.user_id,
                rating=food_rating.rating,
                body=food_rating.body
            )
        result = self.session.execute(sql)
        return result.inserted_primary_key[0]
