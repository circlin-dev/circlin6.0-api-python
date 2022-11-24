from . import api
from adapter.database import db_session
from adapter.orm import notice_mappers, notice_comment_mappers
from adapter.repository.notice import NoticeRepository
from adapter.repository.notice_comment import NoticeCommentRepository
from domain.notice import Notice, NoticeComment

from helper.function import authenticate, get_query_strings_from_request
from helper.constant import ERROR_RESPONSE, INITIAL_DESCENDING_PAGE_CURSOR, INITIAL_PAGE, INITIAL_PAGE_LIMIT
from services import notice_service
from flask import request
import json
from sqlalchemy.orm import clear_mappers


@api.route('/notice', methods=['GET'])
def get_notices():
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        result = {'result': False, 'error': ERROR_RESPONSE[401]}
        return json.dumps(result, ensure_ascii=False), 401

    if request.method == 'GET':
        page_cursor: int = get_query_strings_from_request(request, 'cursor', INITIAL_DESCENDING_PAGE_CURSOR)
        limit: int = get_query_strings_from_request(request, 'limit', INITIAL_PAGE_LIMIT)
        page: int = get_query_strings_from_request(request, 'page', INITIAL_PAGE)

        notice_mappers()
        repo: NoticeRepository = NoticeRepository(db_session)
        comments: list = notice_service.get_notices(page_cursor, limit, repo)
        number_of_comment: int = notice_service.get_count_of_notices(repo)
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


@api.route('/notice/<int:notice_id>', methods=['GET', 'PATCH', 'DELETE'])
def get_update_delete_notice(notice_id: int):
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        result = {'result': False, 'error': ERROR_RESPONSE[401]}
        return json.dumps(result, ensure_ascii=False), 401

    if notice_id is None:
        db_session.close()
        result = {'result': False, 'error': f'{ERROR_RESPONSE[400]} (notice_id).'}
        return json.dumps(result, ensure_ascii=False), 400

    if request.method == 'GET':
        notice_mappers()
        repo: NoticeRepository = NoticeRepository(db_session)
        notice: Notice = notice_service.get_a_notice(notice_id, repo)
        clear_mappers()

        result: dict = {
            'result': True,
            'data': notice,
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


@api.route('/notice/<int:notice_id>/comment', methods=['GET', 'POST'])
def notice_comment(notice_id: int):
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        result = {'result': False, 'error': ERROR_RESPONSE[401]}
        return json.dumps(result, ensure_ascii=False), 401

    if notice_id is None:
        db_session.close()
        result = {'result': False, 'error': f'{ERROR_RESPONSE[400]} (notice_id).'}
        return json.dumps(result, ensure_ascii=False), 400

    if request.method == 'GET':
        page_cursor: int = get_query_strings_from_request(request, 'cursor', INITIAL_DESCENDING_PAGE_CURSOR)
        limit: int = get_query_strings_from_request(request, 'limit', INITIAL_PAGE_LIMIT)
        page: int = get_query_strings_from_request(request, 'page', INITIAL_PAGE)

        notice_comment_mappers()
        repo: NoticeCommentRepository = NoticeCommentRepository(db_session)
        comments: list = notice_service.get_comments(notice_id, page_cursor, limit, user_id, repo)
        number_of_comment: int = notice_service.get_comment_count_of_the_notice(notice_id, repo)
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
