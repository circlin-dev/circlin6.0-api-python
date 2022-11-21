from . import api
from adapter.database import db_session
from adapter.orm import user_mappers, user_favorite_category_mappers
from adapter.repository.user import UserRepository
from adapter.repository.user_favorite_category import UserFavoriteCategoryRepository
from domain.user import UserFavoriteCategory
from helper.function import authenticate
from services.user_service import get_favorite_mission_categories, add_to_favorite_mission_category, delete_from_favorite_mission_category
from helper.constant import ERROR_RESPONSE

from flask import request
import json
from sqlalchemy.orm import clear_mappers


@api.route('/user')
def get_a_user():
    user_mappers()
    repo = UserRepository(db_session)
    user = repo.get_one(user_id=64477)["User"]
    entries = dict(id=user.id,
                   created_at=user.created_at.strftime('%Y/%m/%d'),
                   updated_at=user.updated_at.strftime('%Y/%m/%d'),
                   nickname=user.nickname,
                   ) if user is not None else {}
    clear_mappers()
    return json.dumps(entries, ensure_ascii=False), 200


@api.route('/users')
def get_all_users():
    user_mappers()
    repo = UserRepository(db_session)
    users = repo.get_list()
    entries = [dict(id=user.id,
                    created_at=user.created_at.strftime('%Y/%m/%d'),
                    updated_at=user.updated_at.strftime('%Y/%m/%d'),
                    nickname=user.nickname,
                    ) for user in users]
    clear_mappers()

    return json.dumps(entries, ensure_ascii=False), 200


@api.route('/user/favoriteCategory', methods=['GET', 'POST', 'DELETE'])
def user_favorite_category():

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

        result = {
            'result': True,
            'data': favorite_mission_categories
        }

        return json.dumps(result, ensure_ascii=False), 200

    elif request.method == 'POST':
        params = json.loads(request.get_data())
        mission_category_id = None if params['missionCateogryId'] is None else params['missionCateogryId']

        if mission_category_id is None:
            result = {
                'result': False,
                'error': ERROR_RESPONSE[400]
            }
            return json.dumps(result, ensure_ascii=False), 400

        user_favorite_category_mappers()

        repo = UserFavoriteCategoryRepository(db_session)
        new_mission_category = UserFavoriteCategory(
            id=None,
            user_id=user_id,
            mission_category_id=mission_category_id
        )
        added_to_favorite_categories = add_to_favorite_mission_category(new_mission_category, repo)
        clear_mappers()

        if added_to_favorite_categories['result']:
            db_session.commit()
            db_session.close()
            return json.dumps(added_to_favorite_categories, ensure_ascii=False), 200
        else:
            db_session.close()
            return json.dumps(added_to_favorite_categories, ensure_ascii=False), 400

    elif request.method == 'DELETE':
        params = json.loads(request.get_data())
        mission_category_id = None if params['missionCateogryId'] is None else params['missionCateogryId']

        if mission_category_id is None:
            result = {
                'result': False,
                'error': ERROR_RESPONSE[400]
            }
            return json.dumps(result, ensure_ascii=False), 400

        user_favorite_category_mappers()
        repo = UserFavoriteCategoryRepository(db_session)
        mission_category_to_delete = UserFavoriteCategory(
            id=None,
            user_id=user_id,
            mission_category_id=mission_category_id
        )

        delete_from_favorite_categories = delete_from_favorite_mission_category(mission_category_to_delete, repo)
        clear_mappers()

        if delete_from_favorite_categories['result']:
            db_session.commit()
            db_session.close()
            return json.dumps(delete_from_favorite_categories, ensure_ascii=False), 200
        else:
            db_session.close()
            return json.dumps(delete_from_favorite_categories, ensure_ascii=False), 400

    else:
        result = {
            'result': False,
            'error': f'{ERROR_RESPONSE[405]} ({request.method})'
        }
        return json.dumps(result), 405
