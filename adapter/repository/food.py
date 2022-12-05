from domain.food import Food, FoodBrand, FoodImage

import abc
from sqlalchemy import and_, desc, func, select, text


class AbstractFoodRepository(abc.ABC):
    @abc.abstractmethod
    def get_list(self, word: str, page_cursor: int, limit: int) -> list:
        pass

    @abc.abstractmethod
    def count_number_of_food(self, word: str) -> int:
        pass


class FoodRepository(AbstractFoodRepository):
    def __init__(self, session):
        self.session = session

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
            select(func.json_arrayagg(
                func.json_object(
                    "width", FoodImage.width,
                    "height", FoodImage.height,
                    "type", FoodImage.type,
                    "mimeType", FoodImage.mime_type,
                    "pathname", FoodImage.path,
                    'resized', text(f"""(SELECT IFNULL(JSON_ARRAYAGG(JSON_OBJECT(
                                'mimeType', fi.mime_type,
                                'pathname', fi.path,
                                'width', fi.width
                                )), JSON_ARRAY()) FROM food_images fi WHERE fi.original_file_id = food_images.id)""")
                    )
            )).select_from(FoodImage).where(FoodImage.food_id == Food.id).label("images"),
            # func.ifnull(
            #     func.json_arrayagg(
            #         func.json_object(
            #             'order', BoardImage.order,
            #             'mimeType', BoardImage.mime_type,
            #             'pathname', BoardImage.path,
            #             'resized', text(f"""(SELECT IFNULL(JSON_ARRAYAGG(JSON_OBJECT(
            #                     'mimeType', bi.mime_type,
            #                     'pathname', bi.path,
            #                     'width', bi.width
            #                     )), JSON_ARRAY()) FROM board_images bi WHERE bi.original_file_id = board_images.id)""")
            #         )
            #     ),
            #     func.json_array()
            # ).label('images'),
            func.concat(func.lpad(Food.id, 15, '0')).label('cursor'),
        ).join(
            FoodBrand, FoodBrand.id == Food.brand_id, isouter=True
        ).where(
            and_(
                Food.type == 'product',
                Food.title.like(f'%{word}%'),
                Food.id < page_cursor,
                Food.deleted_at == None
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
