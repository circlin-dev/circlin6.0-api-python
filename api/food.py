from . import api
from adapter.database import db_session
from adapter.orm import food_mappers, food_category_mappers, food_rating_mappers, food_review_mappers
from adapter.repository.food import FoodRepository
from adapter.repository.food_brand import FoodBrandRepository
from adapter.repository.food_category import FoodCategoryRepository
from adapter.repository.food_flavor import FoodFlavorRepository
from adapter.repository.food_food_category import FoodFoodCategoryRepository
from adapter.repository.food_image import FoodImageRepository
from adapter.repository.food_rating import FoodRatingRepository
from adapter.repository.food_review import FoodReviewRepository
from domain.food import Food, FoodBrand
from helper.constant import ERROR_RESPONSE, INITIAL_DESCENDING_PAGE_CURSOR
from helper.function import authenticate, get_query_strings_from_request
from services import food_services

from flask import request
import json
import random
from sqlalchemy.orm import clear_mappers


@api.route('/food', methods=['GET', 'POST'])
def food():
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        result = {'result': False, 'error': ERROR_RESPONSE[401]}
        return json.dumps(result, ensure_ascii=False), 401

    if request.method == 'GET':
        word = get_query_strings_from_request(request, 'word', '')
        limit = get_query_strings_from_request(request, 'limit', 20)
        page_cursor = get_query_strings_from_request(request, 'cursor', INITIAL_DESCENDING_PAGE_CURSOR)

        food_mappers()
        food_repo: FoodRepository = FoodRepository(db_session)
        foods = food_services.get_food_list(word, page_cursor, limit, food_repo)
        number_of_foods = food_services.get_count_of_foods(word, food_repo)
        clear_mappers()
        db_session.close()

        last_cursor: [str, None] = None if len(foods) <= 0 else foods[-1]['cursor']  # 배열 원소의 cursor string

        result: dict = {
            'result': True,
            'data': foods,
            'cursor': last_cursor,
            'totalCount': number_of_foods,
        }
        db_session.close()
        return json.dumps(result, ensure_ascii=False), 200
    elif request.method == 'POST':
        num_images: int = len(request.files.to_dict())

        if num_images < 1:
            # 이미지가 없음  ==> 식단 데이터 등록 우선
            # Request body가 JSON이므로 request.get_data() 로 확인한다.
            data = json.loads(request.get_data())
            flavor_tags: list = data['flavor']
            category: dict = {
                'large': data['categoryLarge'],
                'medium': data['categoryMedium'],
                'small': data['categorySmall']
            }

            if data['type'] == '제품':
                food_type = 'product'
            elif data['type'] == '레시피':
                food_type = 'recipe'
            elif data['type'] == '대표메뉴':
                food_type = 'menu'
            else:
                food_type = 'original'

            food_mappers()
            new_food: Food = Food(
                id=None,
                brand=None,
                large_category_title=data['categoryLarge'],
                title=data['title'],
                user_id=user_id,
                type=food_type,
                container=data['container'],
                amount_per_serving=data["amountPerServing"],
                total_amount=data["totalAmount"],
                unit=data["unit"],
                servings_per_container=data["servingsPerContainer"],
                price=None,
                calorie=data["calorie"],
                carbohydrate=data["carbohydrate"],
                protein=data["protein"],
                fat=data["fat"],
                sodium=data["sodium"],
                sugar=data["sugar"],
                trans_fat=data["transFat"],
                saturated_fat=data["saturatedFat"],
                cholesterol=data["cholesterol"],
                url=None,
                approved_at=None,
                original_data=None,
                deleted_at=None,
            )
            brand: FoodBrand = FoodBrand(
                id=None,
                title=data['brand'],
                type=data['brandType']
            )
            food_repo: FoodRepository = FoodRepository(db_session)
            food_brand_repo: FoodBrandRepository = FoodBrandRepository(db_session)
            food_category_repo: FoodCategoryRepository = FoodCategoryRepository(db_session)
            food_food_category_repo: FoodFoodCategoryRepository = FoodFoodCategoryRepository(db_session)
            food_flavor_repo: FoodFlavorRepository = FoodFlavorRepository(db_session)
            add_food = food_services.add_food(
                new_food,
                brand,
                category,
                flavor_tags,
                food_repo,
                food_brand_repo,
                food_category_repo,
                food_food_category_repo,
                food_flavor_repo
            )
            clear_mappers()

            if add_food['result']:
                db_session.commit()
                db_session.close()
                return json.dumps(add_food, ensure_ascii=False), 200
            else:
                db_session.close()
                return json.dumps({key: value for key, value in add_food.items() if key != 'status_code'}, ensure_ascii=False), add_food['status_code']
        else:
            # 이미지 등록
            # Request body가 formdata이므로 request.form.to_dict() 로 확인한다.
            food_id = int(request.form.to_dict()['foodId'])
            images = request.files.to_dict()
            s3_object_path = f'food/{str(food_id)}'
            types = ["front", "back", "content"]

            food_mappers()
            food_repo: FoodRepository = FoodRepository(db_session)
            food_image_repo: FoodImageRepository = FoodImageRepository(db_session)

            for type in types:
                food_services.create_food_images(food_id, type, images, s3_object_path, food_image_repo)




    else:
        db_session.close()
        result: dict = {
            'result': False,
            'error': f'{ERROR_RESPONSE[405]} ({request.method})'
        }
        return json.dumps(result), 405


@api.route('/food/<int:food_id>/user/rated', methods=['GET'])
def get_user_rated_the_food(food_id: int):
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        result = {'result': False, 'error': ERROR_RESPONSE[401]}
        return json.dumps(result, ensure_ascii=False), 401

    if food_id is None:
        db_session.close()
        result: dict = {'result': False, 'error': f'{ERROR_RESPONSE[400]} (food_id).'}
        return json.dumps(result, ensure_ascii=False), 400

    if request.method == 'GET':
        food_rating_mappers()
        food_rating_repo: FoodRatingRepository = FoodRatingRepository(db_session)
        ratings: list = food_services.get_rating_list_by_food_and_user(food_id, user_id, food_rating_repo)
        clear_mappers()
        db_session.close()

        result = {"result": True, "rated": True if len(ratings) > 0 else False}
        return json.dumps(result, ensure_ascii=False), 200
    else:
        db_session.close()
        result: dict = {
            'result': False,
            'error': f'{ERROR_RESPONSE[405]} ({request.method})'
        }
        return json.dumps(result), 405


@api.route('/food/category', methods=['GET'])
def get_food_category():
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        result = {'result': False, 'error': ERROR_RESPONSE[401]}
        return json.dumps(result, ensure_ascii=False), 401

    if request.method == 'GET':
        food_category_mappers()

        food_category_repo: FoodCategoryRepository = FoodCategoryRepository(db_session)
        data: list = food_services.get_food_categories(food_category_repo)
        clear_mappers()
        db_session.close()

        result: dict = {
            "result": True,
            "data": data
        }
        return json.dumps(result, ensure_ascii=False), 200
    else:
        db_session.close()
        result: dict = {
            'result': False,
            'error': f'{ERROR_RESPONSE[405]} ({request.method})'
        }
        return json.dumps(result), 405


@api.route('/food/review/tag', methods=['GET'])
def get_food_review_tag():
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        result = {'result': False, 'error': ERROR_RESPONSE[401]}
        return json.dumps(result, ensure_ascii=False), 401

    if request.method == 'GET':
        food_review_mappers()
        food_review_repo: FoodReviewRepository = FoodReviewRepository(db_session)
        data: list = food_services.get_food_review_tags(food_review_repo)
        random.shuffle(data)

        clear_mappers()
        db_session.close()
        result: dict = {
            "result": True,
            "data": [] if data is None else data
        }
        return json.dumps(result, ensure_ascii=False), 200
    else:
        db_session.close()
        result: dict = {
            'result': False,
            'error': f'{ERROR_RESPONSE[405]} ({request.method})'
        }
        return json.dumps(result), 405
