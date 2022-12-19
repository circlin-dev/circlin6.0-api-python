from . import api
from adapter.database import db_session
from adapter.orm import block_mappers
from adapter.repository.block import BlockRepository
from helper.constant import ERROR_RESPONSE, INITIAL_DESCENDING_PAGE_CURSOR, INITIAL_PAGE, INITIAL_PAGE_LIMIT
from helper.function import authenticate, failed_response, get_query_strings_from_request
from services import block_service

from flask import request
import json
from sqlalchemy.orm import clear_mappers


@api.route('/block', methods=['GET', 'POST', 'DELETE'])
def block():
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        return json.dumps(failed_response(ERROR_RESPONSE[401]), ensure_ascii=False), 401

    if request.method == 'GET':
        page_cursor: int = get_query_strings_from_request(request, 'cursor', INITIAL_DESCENDING_PAGE_CURSOR)
        limit: int = get_query_strings_from_request(request, 'limit', INITIAL_PAGE_LIMIT)
        page: int = get_query_strings_from_request(request, 'page', INITIAL_PAGE)

        block_mappers()
        block_repo: BlockRepository = BlockRepository(db_session)
        block_list: list = block_service.get_list(user_id, page_cursor, limit, block_repo)
        blocked_user_count: int = block_service.count_number_of_blocked_user(user_id, block_repo)
        clear_mappers()

        last_cursor: [str, None] = None if len(block_list) <= 0 else block_list[-1]['cursor']  # 배열 원소의 cursor string

        result: dict = {
            'result': True,
            'data': block_list,
            'cursor': last_cursor,
            'totalCount': blocked_user_count,
        }
        return json.dumps(result, ensure_ascii=False), 200
    elif request.method == 'POST':
        params: dict = json.loads(request.get_data())
        if 'userId' not in params.keys() or params['userId'] is None:
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (userId).'
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        else:
            target_id: int = params['userId']
            block_mappers()
            block_repo: BlockRepository = BlockRepository(db_session)
            block = block_service.block(user_id, target_id, block_repo)
            clear_mappers()
            if block['result']:
                db_session.commit()
                db_session.close()
                return json.dumps(block, ensure_ascii=False), 200
            else:
                db_session.close()
                return json.dumps({key: value for key, value in block.items() if key != 'status_code'}, ensure_ascii=False), block['status_code']
    elif request.method == 'DELETE':
        params: dict = json.loads(request.get_data())
        if 'userId' not in params.keys() or params['userId'] is None:
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (userId).'
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        else:
            target_id: int = params['userId']
            block_mappers()
            block_repo: BlockRepository = BlockRepository(db_session)
            unblock = block_service.unblock(user_id, target_id, block_repo)
            clear_mappers()
            if unblock['result']:
                db_session.commit()
                db_session.close()
                return json.dumps(unblock, ensure_ascii=False), 200
            else:
                db_session.close()
                return json.dumps({key: value for key, value in unblock.items() if key != 'status_code'}, ensure_ascii=False), unblock['status_code']
    else:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[405]} ({request.method})'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 405
