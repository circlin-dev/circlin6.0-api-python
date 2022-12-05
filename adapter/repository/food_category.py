from adapter.orm import food_categories
from domain.food import FoodCategory

import abc
from sqlalchemy import and_, select


class AbstractFoodCategoryRepository(abc.ABC):
    @abc.abstractmethod
    def get_list(self) -> list:
        pass

    @abc.abstractmethod
    def get_one(self, category: dict) -> FoodCategory:
        pass


class FoodCategoryRepository(AbstractFoodCategoryRepository):
    def __init__(self, session):
        self.session = session

    def get_list(self) -> list:
        sql = select(
            FoodCategory.id,
            FoodCategory.large,
            FoodCategory.medium,
            FoodCategory.small
        )
        result = self.session.execute(sql).all()
        return result

    def get_one(self, category: dict) -> FoodCategory:
        sql = select(
            food_categories.c.id,
            food_categories.c.large,
            food_categories.c.medium,
            food_categories.c.small
        ).where(
            and_(
                food_categories.c.large == category['large'],
                food_categories.c.medium == category['medium'],
                food_categories.c.small == category['small']
            )
        )
        result = self.session.execute(sql).first()
        return result
