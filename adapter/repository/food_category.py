from domain.food import FoodCategory

import abc
from sqlalchemy import select, func


class AbstractFoodCategoryRepository(abc.ABC):
    @abc.abstractmethod
    def get_list(self) -> list:
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
