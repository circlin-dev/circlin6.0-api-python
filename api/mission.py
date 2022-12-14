from . import api
from adapter.database import db_session
from adapter.orm import feed_mappers, mission_category_mappers, mission_comment_mappers, user_favorite_category_mappers
from adapter.repository.feed import FeedRepository
from adapter.repository.mission_category import MissionCategoryRepository
from adapter.repository.mission_comment import MissionCommentRepository
from adapter.repository.user_favorite_category import UserFavoriteCategoryRepository
from helper.constant import ERROR_RESPONSE, INITIAL_DESCENDING_PAGE_CURSOR, INITIAL_PAGE, INITIAL_PAGE_LIMIT
from helper.function import authenticate, failed_response, get_query_strings_from_request
from services import mission_service
from services.user_service import get_favorite_mission_categories

from flask import request
import json
from sqlalchemy.orm import clear_mappers


@api.route('/mission/category', methods=['GET'])
def mission_category():
    user_id = authenticate(request, db_session)
    if user_id is None:
        return json.dumps(failed_response(ERROR_RESPONSE[401]), ensure_ascii=False), 401

    if request.method == 'GET':
        user_favorite_category_mappers()
        repo = UserFavoriteCategoryRepository(db_session)
        favorite_mission_categories = get_favorite_mission_categories(user_id, repo)
        clear_mappers()

        mission_category_mappers()
        repo = MissionCategoryRepository(db_session)
        mission_categories = mission_service.get_mission_categories(repo, favorite_mission_categories)
        clear_mappers()

        result = {
            'result': True,
            'data': mission_categories
        }

        return json.dumps(result, ensure_ascii=False), 200
    else:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[405]} ({request.method})'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 405


@api.route('/mission/<int:mission_id>/comment', methods=['GET', 'POST'])
def mission_comment(mission_id: int):
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        return json.dumps(failed_response(ERROR_RESPONSE[401]), ensure_ascii=False), 401

    if mission_id is None:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[400]} (mission_id).'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 400

    if request.method == 'GET':
        page_cursor: int = get_query_strings_from_request(request, 'cursor', INITIAL_DESCENDING_PAGE_CURSOR)
        limit: int = get_query_strings_from_request(request, 'limit', INITIAL_PAGE_LIMIT)
        page: int = get_query_strings_from_request(request, 'page', INITIAL_PAGE)

        mission_comment_mappers()
        repo: MissionCommentRepository = MissionCommentRepository(db_session)
        comments: list = mission_service.get_comments(mission_id, page_cursor, limit, user_id, repo)
        number_of_comment: int = mission_service.get_comment_count_of_the_mission(mission_id, repo)
        clear_mappers()

        last_cursor: [str, None] = None if len(comments) <= 0 else comments[-1]['cursor']  # 배열 원소의 cursor string

        result: dict = {
            'result': True,
            'data': comments,
            'cursor': last_cursor,
            'totalCount': number_of_comment,
        }
        db_session.close()
        return json.dumps(result, ensure_ascii=False), 200
    elif request.method == 'POST':
        pass
    else:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[405]} ({request.method})'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 405


@api.route('/mission/<int:mission_id>/feed', methods=['GET'])
def mission_feeds(mission_id: int):
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        return json.dumps(failed_response(ERROR_RESPONSE[401]), ensure_ascii=False), 401

    if mission_id is None:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[400]} (mission_id).'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 400

    if request.method == 'GET':
        page_cursor: int = get_query_strings_from_request(request, 'cursor', INITIAL_DESCENDING_PAGE_CURSOR)
        limit: int = get_query_strings_from_request(request, 'limit', INITIAL_PAGE_LIMIT)
        page: int = get_query_strings_from_request(request, 'page', INITIAL_PAGE)

        feed_mappers()
        feed_repo: FeedRepository = FeedRepository(db_session)
        feeds: list = mission_service.get_feeds_by_mission(mission_id, page_cursor, limit, user_id, feed_repo)
        number_of_feeds: int = mission_service.get_feed_count_of_the_mission(mission_id, feed_repo)
        clear_mappers()

        last_cursor: [str, None] = None if len(feeds) <= 0 else feeds[-1]['cursor']  # 배열 원소의 cursor string

        result: dict = {
            'result': True,
            'data': feeds,
            'cursor': last_cursor,
            'totalCount': number_of_feeds,
        }
        db_session.close()
        return json.dumps(result, ensure_ascii=False), 200
