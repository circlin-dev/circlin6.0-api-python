from . import api
from adapter.database import db_session
from adapter.orm import feed_mappers, feed_check_mappers, feed_comment_mappers
from adapter.repository.feed import FeedRepository
from adapter.repository.feed_like import FeedCheckRepository
from adapter.repository.feed_comment import FeedCommentRepository
from domain.feed import Feed
from helper.constant import ERROR_RESPONSE, INITIAL_ASCENDING_PAGE_CURSOR, INITIAL_DESCENDING_PAGE_CURSOR, INITIAL_PAGE, INITIAL_PAGE_LIMIT
from helper.function import authenticate, get_query_strings_from_request
from services import feed_service

from flask import request
import json
from sqlalchemy.orm import clear_mappers


@api.route('/feed/<int:feed_id>', methods=['GET', 'PATCH', 'DELETE'])
def feed(feed_id: int):
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        result = {'result': False, 'error': ERROR_RESPONSE[401]}
        return json.dumps(result, ensure_ascii=False), 401

    if feed_id is None:
        db_session.close()
        result = {'result': False, 'error': f'{ERROR_RESPONSE[400]} (feed_id).'}
        return json.dumps(result, ensure_ascii=False), 400

    if request.method == 'GET':
        feed_mappers()
        repo: FeedRepository = FeedRepository(db_session)
        data: dict = feed_service.get_a_feed(feed_id, user_id, repo)
        clear_mappers()

        result: dict = {
            'result': True,
            'data': data
        }
        db_session.close()
        return json.dumps(result, ensure_ascii=False), 200
    elif request.method == 'PATCH':
        pass
    elif request.method == 'DELETE':
        pass
    else:
        db_session.close()
        result: dict = {
            'result': False,
            'error': f'{ERROR_RESPONSE[405]} ({request.method})'
        }
        return json.dumps(result), 405


@api.route('/feed', methods=['POST'])
def post_a_feed():
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        result = {'result': False, 'error': ERROR_RESPONSE[401]}
        return json.dumps(result, ensure_ascii=False), 401

    if request.method == 'POST':
        pass
    else:
        db_session.close()
        result: dict = {
            'result': False,
            'error': f'{ERROR_RESPONSE[405]} ({request.method})'
        }
        return json.dumps(result), 405


@api.route('/feed/<int:feed_id>/comment', methods=['GET', 'POST'])
def feed_comment(feed_id: int):
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        result = {'result': False, 'error': ERROR_RESPONSE[401]}
        return json.dumps(result, ensure_ascii=False), 401

    if feed_id is None:
        db_session.close()
        result = {'result': False, 'error': f'{ERROR_RESPONSE[400]} (feed_id).'}
        return json.dumps(result, ensure_ascii=False), 400

    if request.method == 'GET':
        page_cursor: int = get_query_strings_from_request(request, 'cursor', INITIAL_DESCENDING_PAGE_CURSOR)
        limit: int = get_query_strings_from_request(request, 'limit', INITIAL_PAGE_LIMIT)
        page: int = get_query_strings_from_request(request, 'page', INITIAL_PAGE)

        feed_comment_mappers()
        repo: FeedCommentRepository = FeedCommentRepository(db_session)
        comments: list = feed_service.get_comments(feed_id, page_cursor, limit, user_id, repo)
        number_of_comment: int = feed_service.get_comment_count_of_the_feed(feed_id, repo)
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
        result: dict = {
            'result': False,
            'error': f'{ERROR_RESPONSE[405]} ({request.method})'
        }
        return json.dumps(result), 405


@api.route('/feed/<int:feed_id>/comment/<int:feed_comment_id>', methods=['PATCH', 'DELETE'])
def feed_comment_manipulate(feed_id: int, feed_comment_id: int):
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        result = {'result': False, 'error': ERROR_RESPONSE[401]}
        return json.dumps(result, ensure_ascii=False), 401

    if feed_id is None:
        db_session.close()
        result = {'result': False, 'error': f'{ERROR_RESPONSE[400]} (feed_id).'}
        return json.dumps(result, ensure_ascii=False), 400

    if feed_comment_id is None:
        db_session.close()
        result = {'result': False, 'error': f'{ERROR_RESPONSE[400]} (feed_comment_id).'}
        return json.dumps(result, ensure_ascii=False), 400

    if request.method == 'PATCH':
        pass
    elif request.method == 'DELETE':
        pass
    else:
        db_session.close()
        result: dict = {
            'result': False,
            'error': f'{ERROR_RESPONSE[405]} ({request.method})'
        }
        return json.dumps(result), 405


@api.route('/feed/<int:feed_id>/like', methods=['GET', 'POST', 'DELETE'])
def feed_check(feed_id: int):
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        result = {'result': False, 'error': ERROR_RESPONSE[401]}
        return json.dumps(result, ensure_ascii=False), 401

    if feed_id is None:
        db_session.close()
        result = {'result': False, 'error': f'{ERROR_RESPONSE[400]} (feed_id).'}
        return json.dumps(result, ensure_ascii=False), 400

    if request.method == 'GET':
        page_cursor: int = get_query_strings_from_request(request, 'cursor', INITIAL_ASCENDING_PAGE_CURSOR)
        limit: int = get_query_strings_from_request(request, 'limit', INITIAL_PAGE_LIMIT)
        page: int = get_query_strings_from_request(request, 'page', INITIAL_PAGE)

        feed_check_mappers()
        feed_check_repo: FeedCheckRepository = FeedCheckRepository(db_session)
        liked_users: list = feed_service.get_user_list_who_like_this_feed(feed_id, page_cursor, limit, feed_check_repo)
        number_of_liked_users: int = feed_service.get_like_count_of_the_feed(feed_id, feed_check_repo)
        clear_mappers()

        last_cursor: [str, None] = None if len(liked_users) <= 0 else liked_users[-1]['cursor']  # 배열 원소의 cursor string

        result: dict = {
            'result': True,
            'data': liked_users,
            'cursor': last_cursor,
            'totalCount': number_of_liked_users,
        }
        db_session.close()
        return json.dumps(result, ensure_ascii=False), 200
    elif request.method == 'POST':
        pass
    elif request.method == 'DELETE':
        pass
    else:
        db_session.close()
        result: dict = {
            'result': False,
            'error': f'{ERROR_RESPONSE[405]} ({request.method})'
        }
        return json.dumps(result), 405


@api.route("/newsfeed", methods=['GET'])
def get_newsfeed():
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        result = {'result': False, 'error': ERROR_RESPONSE[401]}
        return json.dumps(result, ensure_ascii=False), 401

    if request.method == 'GET':
        page_cursor: int = get_query_strings_from_request(request, 'cursor', INITIAL_DESCENDING_PAGE_CURSOR)
        limit: int = get_query_strings_from_request(request, 'limit', INITIAL_PAGE_LIMIT)
        page: int = get_query_strings_from_request(request, 'page', INITIAL_PAGE)

        feed_mappers()
        feed_repo: FeedRepository = FeedRepository(db_session)
        newsfeeds: list = feed_service.get_newsfeeds(user_id, page_cursor, limit, feed_repo)
        number_of_newsfeeds: int = feed_service.get_count_of_newsfeeds(user_id, feed_repo)
        clear_mappers()

        last_cursor: [str, None] = None if len(newsfeeds) <= 0 else newsfeeds[-1]['cursor']  # 배열 원소의 cursor string

        result: dict = {
            'result': True,
            'data': newsfeeds,
            'cursor': last_cursor,
            'totalCount': number_of_newsfeeds,
        }
        db_session.close()
        return json.dumps(result, ensure_ascii=False), 200
    else:
        db_session.close()
        result: dict = {
            'result': False,
            'error': f'{ERROR_RESPONSE[405]} ({request.method})'
        }
        return json.dumps(result), 405


@api.route('/feed/recently-most-checked', methods=['GET'])
def get_recently_most_checked_feeds():
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        result = {'result': False, 'error': ERROR_RESPONSE[401]}
        return json.dumps(result, ensure_ascii=False), 401

    if request.method == 'GET':
        feed_mappers()
        feed_repo: FeedRepository = FeedRepository(db_session)
        feeds_for_recommendation: list = feed_service.get_recently_most_checked_feeds(user_id, feed_repo)
        clear_mappers()

        result: dict = {
            'result': True,
            'data': feeds_for_recommendation,
            'totalCount': len(feeds_for_recommendation)
        }
        db_session.close()
        return json.dumps(result, ensure_ascii=False), 200
    else:
        db_session.close()
        result: dict = {
            'result': False,
            'error': f'{ERROR_RESPONSE[405]} ({request.method})'
        }
        return json.dumps(result), 405
