from adapter.orm import food_brands
from domain.food import Food, FoodBrand, FoodImage

import abc
from sqlalchemy import and_, desc, func, exists, insert, select, text


class AbstractFoodBrandRepository(abc.ABC):
    @abc.abstractmethod
    def add_if_not_exists(self, new_brand: FoodBrand):
        pass

    @abc.abstractmethod
    def get_one(self, food_brand: FoodBrand) -> FoodBrand:
        pass


class FoodBrandRepository(AbstractFoodBrandRepository):
    def __init__(self, session):
        self.session = session

    def add_if_not_exists(self, new_brand: FoodBrand):
        # QUERY BUILDER 문법으로 고칠 것.
        sql = text(f"""
            INSERT INTO food_brands(title, type) 
            SELECT
                temp.*
            FROM
                (SELECT '{new_brand.title}', '{new_brand.type}') AS temp
            WHERE NOT EXISTS(
                SELECT
                    id,
                    title,
                    type
                FROM
                    food_brands
                WHERE title = '{new_brand.title}'
                AND type = '{new_brand.type}'
            )
        """)
        return self.session.execute(sql)

    def get_one(self, food_brand: FoodBrand) -> FoodBrand:
        sql = select(
            food_brands.c.id,
            food_brands.c.title,
            food_brands.c.type,
        ).where(
            and_(
                food_brands.c.title == food_brand.title,
                food_brands.c.type == food_brand.type
            )
        )
        result = self.session.execute(sql).first()
        return result
