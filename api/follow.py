from . import api
from adapter.database import db_session
from adapter.orm import follow_mappers
from adapter.repository.follow import FollowRepository
from helper.constant import ERROR_RESPONSE, INITIAL_DESCENDING_PAGE_CURSOR, INITIAL_PAGE, INITIAL_PAGE_LIMIT
from helper.function import authenticate, failed_response, get_query_strings_from_request
from services import follow_service

from flask import request
import json
from sqlalchemy.orm import clear_mappers


@api.route('/user/<int:target_id>/following', methods=['GET'])
def get_following(target_id: int):
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        return json.dumps(failed_response(ERROR_RESPONSE[401]), ensure_ascii=False), 401

    if target_id is None:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[400]} (user_id).'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 400

    if request.method == 'GET':
        page_cursor: int = get_query_strings_from_request(request, 'cursor', INITIAL_DESCENDING_PAGE_CURSOR)
        limit: int = get_query_strings_from_request(request, 'limit', INITIAL_PAGE_LIMIT)
        page: int = get_query_strings_from_request(request, 'page', INITIAL_PAGE)

        follow_mappers()
        follow_repo: FollowRepository = FollowRepository(db_session)
        followings: dict = follow_service.get_followings(target_id, user_id, page_cursor, limit, follow_repo)
        total_count: int = follow_service.count_number_of_following(target_id, follow_repo)
        clear_mappers()
        db_session.close()
        last_cursor: [str, None] = None if len(followings) <= 0 else followings[-1]['cursor']  # 배열 원소의 cursor string
        result: dict = {
            'result': True,
            'data': followings,
            'cursor': last_cursor,
            'totalCount': total_count,
        }
        return json.dumps(result, ensure_ascii=False), 200
    else:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[405]} ({request.method})'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 405


@api.route('/user/<int:target_id>/follower', methods=['GET'])
def get_follower(target_id: int):
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        return json.dumps(failed_response(ERROR_RESPONSE[401]), ensure_ascii=False), 401

    if target_id is None:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[400]} (user_id).'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 400

    if request.method == 'GET':
        page_cursor: int = get_query_strings_from_request(request, 'cursor', INITIAL_DESCENDING_PAGE_CURSOR)
        limit: int = get_query_strings_from_request(request, 'limit', INITIAL_PAGE_LIMIT)
        page: int = get_query_strings_from_request(request, 'page', INITIAL_PAGE)

        follow_mappers()
        follow_repo: FollowRepository = FollowRepository(db_session)
        followers: dict = follow_service.get_followers(target_id, user_id, page_cursor, limit, follow_repo)
        total_count: int = follow_service.count_number_of_follower(target_id, follow_repo)
        clear_mappers()
        db_session.close()
        last_cursor: [str, None] = None if len(followers) <= 0 else followers[-1]['cursor']  # 배열 원소의 cursor string
        result: dict = {
            'result': True,
            'data': followers,
            'cursor': last_cursor,
            'totalCount': total_count,
        }
        return json.dumps(result, ensure_ascii=False), 200
    else:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[405]} ({request.method})'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 405


@api.route('/follow', methods=['POST', 'DELETE'])
def follow():
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        return json.dumps(failed_response(ERROR_RESPONSE[401]), ensure_ascii=False), 401

    if request.method == 'POST':
        params: dict = json.loads(request.get_data())
        if 'userId' not in params.keys() or params['userId'] is None:
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (userId).'
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        else:
            target_id: int = params['userId']
            follow_mappers()
            follow_repo: FollowRepository = FollowRepository(db_session)
            follow = follow_service.follow(user_id, target_id, follow_repo)
            clear_mappers()
            if follow['result']:
                db_session.commit()
                db_session.close()
                return json.dumps(follow, ensure_ascii=False), 200
            else:
                db_session.close()
                return json.dumps({key: value for key, value in follow.items() if key != 'status_code'}, ensure_ascii=False), follow['status_code']
    elif request.method == 'DELETE':
        params: dict = json.loads(request.get_data())
        if 'userId' not in params.keys() or params['userId'] is None:
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (userId).'
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        else:
            target_id: int = params['userId']
            follow_mappers()
            follow_repo: FollowRepository = FollowRepository(db_session)
            unfollow = follow_service.unfollow(user_id, target_id, follow_repo)
            clear_mappers()
            if unfollow['result']:
                db_session.commit()
                db_session.close()
                return json.dumps(unfollow, ensure_ascii=False), 200
            else:
                db_session.close()
                return json.dumps({key: value for key, value in unfollow.items() if key != 'status_code'}, ensure_ascii=False), unfollow['status_code']
    else:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[405]} ({request.method})'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 405
