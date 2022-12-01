from . import api
from adapter.database import db_session
from adapter.orm import food_mappers
from helper.constant import ERROR_RESPONSE, INITIAL_DESCENDING_PAGE_CURSOR
from helper.function import authenticate, get_query_strings_from_request

from flask import request
import json
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