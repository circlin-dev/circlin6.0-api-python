from . import api
from adapter.database import db_session

from adapter.orm import notification_mappers
from adapter.repository.common_code import CommonCodeRepository
from adapter.repository.notification import NotificationRepository
from domain.notification import Notification

from helper.function import authenticate, failed_response, get_query_strings_from_request
from helper.constant import ERROR_RESPONSE, INITIAL_DESCENDING_PAGE_CURSOR, INITIAL_PAGE, INITIAL_PAGE_LIMIT

from services import notification_service
from flask import request
import json
from sqlalchemy.orm import clear_mappers


@api.route('/notification', methods=['GET'])
def get_notification():
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        return json.dumps(failed_response(ERROR_RESPONSE[401]), ensure_ascii=False), 401

    if request.method == 'GET':
        page_cursor = get_query_strings_from_request(request, 'cursor', INITIAL_DESCENDING_PAGE_CURSOR)
        limit = get_query_strings_from_request(request, 'limit', INITIAL_PAGE_LIMIT)
        page = get_query_strings_from_request(request, 'page', INITIAL_PAGE)

        notification_mappers()
        notification_repo: NotificationRepository = NotificationRepository(db_session)
        common_code_repo: CommonCodeRepository = CommonCodeRepository(db_session)
        notification_list: list = notification_service.get_notification_list(user_id, page_cursor, limit, notification_repo, common_code_repo)
        number_of_notifications: int = notification_service.get_count_of_notifications(user_id, notification_repo)
        db_session.commit()
        clear_mappers()

        last_cursor: [str, None] = None if len(notification_list) <= 0 else notification_list[-1]['cursor']  # 배열 원소의 cursor string

        result: dict = {
            'result': True,
            'data': notification_list,
            'cursor': last_cursor,
            'totalCount': number_of_notifications,
        }
        db_session.close()
        return json.dumps(result, ensure_ascii=False), 200

