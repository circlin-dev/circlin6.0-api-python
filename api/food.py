from . import api
from adapter.database import db_session
from adapter.orm import food_mappers, food_category_mappers, food_rating_mappers, food_rating_image_mappers, food_review_mappers
from adapter.repository.food import FoodRepository
from adapter.repository.food_brand import FoodBrandRepository
from adapter.repository.food_category import FoodCategoryRepository
from adapter.repository.food_flavor import FoodFlavorRepository
from adapter.repository.food_food_category import FoodFoodCategoryRepository
from adapter.repository.food_image import FoodImageRepository
from adapter.repository.food_rating import FoodRatingRepository
from adapter.repository.food_rating_image import FoodRatingImageRepository
from adapter.repository.food_rating_review import FoodRatingReviewRepository
from adapter.repository.food_review import FoodReviewRepository
from adapter.repository.notification import NotificationRepository
from adapter.repository.point_history import PointHistoryRepository
from adapter.repository.user import UserRepository
from domain.food import Food, FoodBrand, FoodRating
from helper.constant import ERROR_RESPONSE, INITIAL_DESCENDING_PAGE_CURSOR
from helper.function import authenticate, failed_response, get_query_strings_from_request
from services import food_services

from flask import request
import json
import random
from sqlalchemy.orm import clear_mappers
from typing import List


@api.route('/food', methods=['GET', 'POST'])
def food():
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        return json.dumps(failed_response(ERROR_RESPONSE[401]), ensure_ascii=False), 401

    if request.method == 'GET':
        word = get_query_strings_from_request(request, 'word', '')
        limit = get_query_strings_from_request(request, 'limit', 20)
        page_cursor = get_query_strings_from_request(request, 'cursor', INITIAL_DESCENDING_PAGE_CURSOR)

        food_mappers()
        food_repo: FoodRepository = FoodRepository(db_session)
        foods: list = food_services.get_food_list(word, page_cursor, limit, food_repo)
        number_of_foods: int = food_services.get_count_of_foods(word, food_repo)
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

            if 'flavor' not in data.keys():
                db_session.close()
                error_message = f'{ERROR_RESPONSE[400]} (flavor)'
                return json.dumps(failed_response(error_message), ensure_ascii=False), 400
            elif 'categoryLarge' not in data.keys():
                db_session.close()
                error_message = f'{ERROR_RESPONSE[400]} (categoryLarge)'
                return json.dumps(failed_response(error_message), ensure_ascii=False), 400
            elif 'categoryMedium' not in data.keys():
                db_session.close()
                error_message = f'{ERROR_RESPONSE[400]} (categoryMedium)'
                return json.dumps(failed_response(error_message), ensure_ascii=False), 400
            elif 'categorySmall' not in data.keys():
                db_session.close()
                error_message = f'{ERROR_RESPONSE[400]} (categorySmall)'
                return json.dumps(failed_response(error_message), ensure_ascii=False), 400
            elif 'type' not in data.keys():
                db_session.close()
                error_message = f'{ERROR_RESPONSE[400]} (type)'
                return json.dumps(failed_response(error_message), ensure_ascii=False), 400
            elif 'title' not in data.keys():
                db_session.close()
                error_message = f'{ERROR_RESPONSE[400]} (title)'
                return json.dumps(failed_response(error_message), ensure_ascii=False), 400
            elif 'container' not in data.keys():
                db_session.close()
                error_message = f'{ERROR_RESPONSE[400]} (container)'
                return json.dumps(failed_response(error_message), ensure_ascii=False), 400
            elif 'amountPerServing' not in data.keys():
                db_session.close()
                error_message = f'{ERROR_RESPONSE[400]} (amountPerServing)'
                return json.dumps(failed_response(error_message), ensure_ascii=False), 400
            elif 'totalAmount' not in data.keys():
                db_session.close()
                error_message = f'{ERROR_RESPONSE[400]} (totalAmount)'
                return json.dumps(failed_response(error_message), ensure_ascii=False), 400
            elif 'unit' not in data.keys():
                db_session.close()
                error_message = f'{ERROR_RESPONSE[400]} (unit)'
                return json.dumps(failed_response(error_message), ensure_ascii=False), 400
            elif 'servingsPerContainer' not in data.keys():
                db_session.close()
                error_message = f'{ERROR_RESPONSE[400]} (servingsPerContainer)'
                return json.dumps(failed_response(error_message), ensure_ascii=False), 400
            elif 'calorie' not in data.keys():
                db_session.close()
                error_message = f'{ERROR_RESPONSE[400]} (calorie)'
                return json.dumps(failed_response(error_message), ensure_ascii=False), 400
            elif 'carbohydrate' not in data.keys():
                db_session.close()
                error_message = f'{ERROR_RESPONSE[400]} (carbohydrate)'
                return json.dumps(failed_response(error_message), ensure_ascii=False), 400
            elif 'protein' not in data.keys():
                db_session.close()
                error_message = f'{ERROR_RESPONSE[400]} (protein)'
                return json.dumps(failed_response(error_message), ensure_ascii=False), 400
            elif 'fat' not in data.keys():
                db_session.close()
                error_message = f'{ERROR_RESPONSE[400]} (fat)'
                return json.dumps(failed_response(error_message), ensure_ascii=False), 400
            elif 'sodium' not in data.keys():
                db_session.close()
                error_message = f'{ERROR_RESPONSE[400]} (sodium)'
                return json.dumps(failed_response(error_message), ensure_ascii=False), 400
            elif 'sugar' not in data.keys():
                db_session.close()
                error_message = f'{ERROR_RESPONSE[400]} (sugar)'
                return json.dumps(failed_response(error_message), ensure_ascii=False), 400
            elif 'transFat' not in data.keys():
                db_session.close()
                error_message = f'{ERROR_RESPONSE[400]} (transFat)'
                return json.dumps(failed_response(error_message), ensure_ascii=False), 400
            elif 'saturatedFat' not in data.keys():
                db_session.close()
                error_message = f'{ERROR_RESPONSE[400]} (saturatedFat)'
                return json.dumps(failed_response(error_message), ensure_ascii=False), 400
            elif 'cholesterol' not in data.keys():
                db_session.close()
                error_message = f'{ERROR_RESPONSE[400]} (cholesterol)'
                return json.dumps(failed_response(error_message), ensure_ascii=False), 400
            elif 'brand' not in data.keys():
                db_session.close()
                error_message = f'{ERROR_RESPONSE[400]} (brand)'
                return json.dumps(failed_response(error_message), ensure_ascii=False), 400
            elif 'brandType' not in data.keys():
                db_session.close()
                error_message = f'{ERROR_RESPONSE[400]} (brandType)'
                return json.dumps(failed_response(error_message), ensure_ascii=False), 400
            else:
                flavor_tags: List[str] = data['flavor']
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
            images: dict = request.files.to_dict()
            if 'foodId' not in request.form.to_dict().keys():
                db_session.close()
                error_message = f'{ERROR_RESPONSE[400]} (foodId)'
                return json.dumps(failed_response(error_message), ensure_ascii=False), 400
            elif images is None or len(images) == 0:
                db_session.close()
                error_message = f'{ERROR_RESPONSE[400]} (front, back, content images).'
                return json.dumps(failed_response(error_message), ensure_ascii=False), 400
            else:
                food_id: int = int(request.form.to_dict()['foodId'])
                s3_object_path: str = f'food/{str(food_id)}'
                types: List[str] = ["front", "back", "content"]
                food_mappers()
                # food_repo: FoodRepository = FoodRepository(db_session)
                food_image_repo: FoodImageRepository = FoodImageRepository(db_session)

                for type in types:
                    food_services.create_food_images(food_id, type, images[type], s3_object_path, food_image_repo)

                clear_mappers()
                db_session.commit()
                db_session.close()

                result = {'result': True}
                return json.dumps(result, ensure_ascii=False), 200
    else:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[405]} ({request.method})'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 405


@api.route('/food/<int:food_id>/user/rated', methods=['GET'])
def get_user_rated_the_food(food_id: int):
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        return json.dumps(failed_response(ERROR_RESPONSE[401]), ensure_ascii=False), 401

    if food_id is None:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[400]} (foodId)'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 400

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
        error_message = f'{ERROR_RESPONSE[405]} ({request.method})'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 405


@api.route('/food/<int:food_id>/rating', methods=['GET', 'POST'])
def food_review(food_id: int):
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        return json.dumps(failed_response(ERROR_RESPONSE[401]), ensure_ascii=False), 401

    if food_id is None:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[400]} (foodId)'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 400

    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        num_images: int = len(request.files.to_dict())

        if num_images < 1:
            # 이미지가 없음  ==> 식단 데이터 등록 우선
            data = json.loads(request.get_data())
            if 'body' not in data.keys():
                error_message = f'{ERROR_RESPONSE[400]} (body).'
                return json.dumps(failed_response(error_message), ensure_ascii=False), 400
            elif 'rating' not in data.keys():
                error_message = f'{ERROR_RESPONSE[400]} (rating).'
                return json.dumps(failed_response(error_message), ensure_ascii=False), 400
            elif 'tags' not in data.keys():
                error_message = f'{ERROR_RESPONSE[400]} (tags).'
                return json.dumps(failed_response(error_message), ensure_ascii=False), 400
            elif 'newTags' not in data.keys():
                error_message = f'{ERROR_RESPONSE[400]} (newTags).'
                return json.dumps(failed_response(error_message), ensure_ascii=False), 400
            else:
                body: str = data['body']
                rating: int = int(data['rating'])
                selected_tag_ids: List[int] = data['tags']  # 기본 제공하는 태그 목록 중 선택한 것들의 id 배열
                new_tags_written_by_user: List[str] = data['newTags']   # 직접 작성한 태그들 => food_reviews에 새로 INSERT해야 함

                food_rating_mappers()
                new_food_rating: FoodRating = FoodRating(
                    id=None,
                    food_id=food_id,
                    user_id=user_id,
                    rating=rating,
                    body=None if body.strip() == '' else body  # client-side에서 리뷰 텍스트 기본값을 ''로 했기 때문에 간단히 전처리.
                )
                food_review_repo: FoodReviewRepository = FoodReviewRepository(db_session)
                food_rating_repo: FoodRatingRepository = FoodRatingRepository(db_session)
                food_rating_review_repo: FoodRatingReviewRepository = FoodRatingReviewRepository(db_session)
                # notification_repo: NotificationRepository = NotificationRepository(db_session)
                point_history_repo: PointHistoryRepository = PointHistoryRepository(db_session)
                user_repo: UserRepository = UserRepository(db_session)
                add_food_rating: dict = food_services.add_food_rating(
                    new_food_rating,
                    selected_tag_ids,
                    new_tags_written_by_user,
                    food_review_repo,
                    food_rating_repo,
                    food_rating_review_repo,
                    # notification_repo,
                    point_history_repo,
                    user_repo
                )
                clear_mappers()

                if add_food_rating['result']:
                    db_session.commit()
                    db_session.close()
                    return json.dumps(add_food_rating, ensure_ascii=False), 200
                else:
                    db_session.close()
                    return json.dumps({'result': False}, ensure_ascii=False), 400
        else:
            images: list = request.files.getlist('files[]')
            if 'ratingId' not in request.form.to_dict().keys():
                db_session.close()
                error_message = f'{ERROR_RESPONSE[400]} (ratingId)'
                return json.dumps(failed_response(error_message), ensure_ascii=False), 400
            if images is None or len(images) == 0:
                db_session.close()
                error_message = f'{ERROR_RESPONSE[400]} (files[])'
                return json.dumps(failed_response(error_message), ensure_ascii=False), 400
            else:
                rating_id: int = int(request.form.to_dict()['ratingId'])  # request body가 FormData로 옴.
                food_rating_image_mappers()
                food_rating_image_repo: FoodRatingImageRepository = FoodRatingImageRepository(db_session)
                s3_object_path: str = f'food/{str(food_id)}/rating'

                for image in images:
                    food_services.create_food_rating_images(rating_id, image, s3_object_path, food_rating_image_repo)

                clear_mappers()
                db_session.commit()
                db_session.close()
                result = {'result': True}
                return json.dumps(result, ensure_ascii=False), 200
    else:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[405]} ({request.method})'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 405


@api.route('/food/category', methods=['GET'])
def get_food_category():
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        return json.dumps(failed_response(ERROR_RESPONSE[401]), ensure_ascii=False), 401

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
        error_message = f'{ERROR_RESPONSE[405]} ({request.method})'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 405


@api.route('/food/review/tag', methods=['GET'])
def get_food_review_tag():
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        return json.dumps(failed_response(ERROR_RESPONSE[401]), ensure_ascii=False), 401

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
        error_message = f'{ERROR_RESPONSE[405]} ({request.method})'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 405
