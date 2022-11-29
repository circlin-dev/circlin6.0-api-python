from . import api
from adapter.database import db_session
from adapter.orm import feed_mappers, user_mappers, user_favorite_category_mappers
from adapter.repository.feed import FeedRepository
from adapter.repository.user import UserRepository
from adapter.repository.user_favorite_category import UserFavoriteCategoryRepository
from domain.user import UserFavoriteCategory
from helper.constant import INITIAL_DESCENDING_PAGE_CURSOR, INITIAL_PAGE, INITIAL_PAGE_LIMIT
from helper.function import authenticate, get_query_strings_from_request
from services import user_service
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
        favorite_mission_categories = user_service.get_favorite_mission_categories(user_id, repo)

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
        added_to_favorite_categories = user_service.add_to_favorite_mission_category(new_mission_category, repo)
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

        delete_from_favorite_categories = user_service.delete_from_favorite_mission_category(mission_category_to_delete, repo)
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


@api.route('/user/<int:user_id>/feed', methods=['GET'])
def get_user_feeds(user_id: int):
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        result = {'result': False, 'error': ERROR_RESPONSE[401]}
        return json.dumps(result, ensure_ascii=False), 401

    if user_id is None:
        db_session.close()
        result = {'result': False, 'error': f'{ERROR_RESPONSE[400]} (user_id).'}
        return json.dumps(result, ensure_ascii=False), 400

    if request.method == 'GET':
        page_cursor: int = get_query_strings_from_request(request, 'cursor', INITIAL_DESCENDING_PAGE_CURSOR)
        limit: int = get_query_strings_from_request(request, 'limit', INITIAL_PAGE_LIMIT)
        page: int = get_query_strings_from_request(request, 'page', INITIAL_PAGE)

        feed_mappers()
        repo: FeedRepository = FeedRepository(db_session)
        feeds: list = user_service.get_feeds_by_user(user_id, page_cursor, limit, repo)
        number_of_feeds: int = user_service.get_feed_count_of_the_user(user_id, repo)
        clear_mappers()

        db_session.close()
        last_cursor: [str, None] = None if len(feeds) <= 0 else feeds[-1]['cursor']  # 배열 원소의 cursor string

        result: dict = {
            'result': True,
            'data': feeds,
            'cursor': last_cursor,
            'totalCount': number_of_feeds,
        }
        return json.dumps(result, ensure_ascii=False), 200
