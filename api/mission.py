from . import api
from adapter.database import db_session
from adapter.orm import mission_category_mappers, user_favorite_category_mappers
from adapter.repository.mission_category import MissionCategoryRepository
from adapter.repository.user_favorite_category import UserFavoriteCategoryRepository
from helper.constant import ERROR_RESPONSE
from helper.function import authenticate
from services.mission_service import get_mission_categories
from services.user_service import get_favorite_mission_categories

from flask import request
import json
from sqlalchemy.orm import clear_mappers


@api.route('/mission/category', methods=['GET'])
def mission_category():
    user_id = authenticate(request, db_session)
    if user_id is None:
        result = {
            'result': False,
            'error': ERROR_RESPONSE[401]
        }
        return json.dumps(result, ensure_ascii=False), 401

    if request.method == 'GET':
        user_favorite_category_mappers()
        repo = UserFavoriteCategoryRepository(db_session)
        favorite_mission_categories = get_favorite_mission_categories(user_id, repo)
        clear_mappers()

        mission_category_mappers()
        repo = MissionCategoryRepository(db_session)
        mission_categories = get_mission_categories(repo, favorite_mission_categories)
        clear_mappers()

        result = {
            'result': True,
            'data': mission_categories
        }

        return json.dumps(result, ensure_ascii=False), 200
