from . import api
from adapter.database import db_session
from adapter.orm import food_mappers, food_category_mappers, food_review_mappers
from adapter.repository.food_category import FoodCategoryRepository
from adapter.repository.food_review import FoodReviewRepository
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

        clear_mappers()


@api.route('/food/category', methods=['GET'])
def get_food_category():
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        result = {'result': False, 'error': ERROR_RESPONSE[401]}
        return json.dumps(result, ensure_ascii=False), 401

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


@api.route('/food/review/tag', methods=['GET'])
def get_food_review_tag():
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        result = {'result': False, 'error': ERROR_RESPONSE[401]}
        return json.dumps(result, ensure_ascii=False), 401

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
