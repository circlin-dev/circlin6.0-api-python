from adapter.orm import food_flavors

import abc
from sqlalchemy import insert


class AbstractFoodFlavorRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, food_id: int, flavor_tags: list):
        pass

    @abc.abstractmethod
    def get_list_by_food_id(self, food_id) -> list:
        pass


class FoodFlavorRepository(AbstractFoodFlavorRepository):
    def __init__(self, session):
        self.session = session

    def add(self, food_id: int, flavor_tags: list):
        for tag in flavor_tags:
            sql = insert(food_flavors).values(food_id=food_id, flavors=tag)
            self.session.execute(sql)
        return True

    def get_list_by_food_id(self, food_id: int) -> list:
        pass
