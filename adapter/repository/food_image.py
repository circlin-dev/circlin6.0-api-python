from adapter.orm import food_images
from domain.food import FoodImage

import abc
from sqlalchemy import insert


class AbstractFoodImageRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, type: str, new_board_image: FoodImage):
        pass


class FoodImageRepository(AbstractFoodImageRepository):
    def __init__(self, session):
        self.session = session

    def add(self, type: str, new_food_image: FoodImage):
        if new_food_image.original_file_id is None:
            sql = insert(
                food_images
            ).values(
                food_id=new_food_image.board_id,
                type=type,
                path=new_food_image.path,
                file_name=new_food_image.file_name,
                mime_type=new_food_image.mime_type,
                size=new_food_image.size,
                width=new_food_image.width,
                height=new_food_image.height
            )
        else:
            sql = insert(
                new_food_image
            ).values(
                food_id=new_food_image.board_id,
                type=type,
                path=new_food_image.path,
                file_name=new_food_image.file_name,
                mime_type=new_food_image.mime_type,
                size=new_food_image.size,
                width=new_food_image.width,
                height=new_food_image.height,
                original_file_id=new_food_image.original_file_id
            )
        result = self.session.execute(sql)

        return result.inserted_primary_key[0]
