from adapter.orm import food_rating_images
from domain.food import FoodRatingImage

import abc
from sqlalchemy import insert


class AbstractFoodRatingImageRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, new_food_rating_image: FoodRatingImage):
        pass


class FoodRatingImageRepository(AbstractFoodRatingImageRepository):
    def __init__(self, session):
        self.session = session

    def add(self,  new_food_rating_image: FoodRatingImage):
        if new_food_rating_image.original_file_id is None:
            sql = insert(
                food_rating_images
            ).values(
                food_rating_id=new_food_rating_image.food_rating_id,
                path=new_food_rating_image.path,
                file_name=new_food_rating_image.file_name,
                mime_type=new_food_rating_image.mime_type,
                size=new_food_rating_image.size,
                width=new_food_rating_image.width,
                height=new_food_rating_image.height
            )
        else:
            sql = insert(
                food_rating_images
            ).values(
                food_rating_id=new_food_rating_image.food_rating_id,
                path=new_food_rating_image.path,
                file_name=new_food_rating_image.file_name,
                mime_type=new_food_rating_image.mime_type,
                size=new_food_rating_image.size,
                width=new_food_rating_image.width,
                height=new_food_rating_image.height,
                original_file_id=new_food_rating_image.original_file_id
            )
        result = self.session.execute(sql)

        return result.inserted_primary_key[0]
