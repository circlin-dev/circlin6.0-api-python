from domain.food import FoodFoodCategory

import abc
from sqlalchemy import insert


class AbstractFoodFoodCategoryRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, food_id: int, food_category_id: int):
        pass


class FoodFoodCategoryRepository(AbstractFoodFoodCategoryRepository):
    def __init__(self, session):
        self.session = session

    def add(self, food_id: int, food_category_id: int):
        sql = insert(
            FoodFoodCategory
        ).values(food_id=food_id, food_category_id=food_category_id)
        return self.session.execute(sql)
