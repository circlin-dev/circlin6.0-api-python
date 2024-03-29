from domain.food import Food, FoodBrand, FoodImage

import abc
from sqlalchemy import and_, desc, func, insert, select, text


class AbstractFoodRepository(abc.ABC):
    @abc.abstractmethod
    def get_one(self, food: Food) -> Food:
        pass

    @abc.abstractmethod
    def get_list(self, word: str, page_cursor: int, limit: int) -> list:
        pass

    @abc.abstractmethod
    def count_number_of_food(self, word: str) -> int:
        pass

    @abc.abstractmethod
    def add_one(self, new_food: Food) -> int:
        pass


class FoodRepository(AbstractFoodRepository):
    def __init__(self, session):
        self.session = session

    def get_one(self, food: Food) -> Food:
        title = food.title
        large_category_title = food.large_category_title
        type = food.type
        sql = select(
            Food
        ).where(
            and_(
                Food.title == title,
                Food.large_category_title == large_category_title,
                Food.type == type,
                Food.deleted_at == None
            )
        )
        return self.session.execute(sql).first()

    def get_list(self, word: str, page_cursor: int, limit: int) -> list:
        sql = select(
            Food.id,
            Food.large_category_title,
            Food.title,
            FoodBrand.title.label('brand'),
            func.json_object(
                "calorie", func.round(Food.calorie, 2),
                "protein", func.round(Food.protein, 2),
                "fat", func.round(Food.fat, 2),
                "carbohydrate", func.round(Food.carbohydrate, 2)
            ).label('nutrition'),
            Food.price,
            Food.total_amount,
            Food.unit,
            Food.amount_per_serving,
            Food.container,
            func.json_arrayagg(
                func.json_object(
                    "width", FoodImage.width,
                    "height", FoodImage.height,
                    "type", FoodImage.type,
                    "mimeType", FoodImage.mime_type,
                    "pathname", FoodImage.path,
                    'resized', text(f"""(SELECT IFNULL(JSON_ARRAYAGG(JSON_OBJECT(
                            'mimeType', fi.mime_type,
                            'pathname', fi.path,
                            'width', fi.width,
                            'height', fi.height
                            )), JSON_ARRAY()) FROM food_images fi WHERE fi.original_file_id = food_images.id)""")
                )
            ).label("images"),
            func.concat(func.lpad(Food.id, 15, '0')).label('cursor'),
        ).join(
            FoodBrand, FoodBrand.id == Food.brand_id, isouter=True
        ).join(
            FoodImage, FoodImage.food_id == Food.id, isouter=True
        ).where(
            and_(
                Food.type == 'product',
                Food.title.like(f'%{word}%'),
                Food.id < page_cursor,
                Food.deleted_at == None,
                FoodImage.original_file_id == None
            )
        ).group_by(
            Food.id
        ).order_by(
            desc(Food.id)
        ).limit(limit)
        result = self.session.execute(sql).all()
        return result

    def count_number_of_food(self, word: str) -> int:
        sql = select(
            func.count(Food.id)
        ).where(
            and_(
                Food.type == 'product',
                Food.title.like(f'%{word}%'),
                Food.deleted_at == None
            )
        )
        result = self.session.execute(sql).scalar()
        return result

    def add_one(self, new_food: Food) -> int:
        sql = insert(Food).values(
            brand_id=new_food.brand_id,
            large_category_title=new_food.large_category_title,
            title=new_food.title,
            user_id=new_food.user_id,
            type=new_food.type,
            container=new_food.container,
            amount_per_serving=new_food.amount_per_serving,
            total_amount=new_food.total_amount,
            unit=new_food.unit,
            servings_per_container=new_food.servings_per_container,
            price=new_food.price,
            calorie=new_food.calorie,
            carbohydrate=new_food.carbohydrate,
            protein=new_food.protein,
            fat=new_food.fat,
            sodium=new_food.sodium,
            sugar=new_food.sugar,
            trans_fat=new_food.trans_fat,
            saturated_fat=new_food.saturated_fat,
            cholesterol=new_food.cholesterol,
            url=new_food.url,
            approved_at=new_food.approved_at,
            deleted_at=new_food.deleted_at
        )
        result = self.session.execute(sql)  # =====> inserted row의 id값을 반환해야 한다.
        return result.inserted_primary_key[0]

