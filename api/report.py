from . import api
from adapter.database import db_session
from adapter.orm import report_mappers
from adapter.repository.report import ReportRepository
from helper.constant import ERROR_RESPONSE, INITIAL_DESCENDING_PAGE_CURSOR, INITIAL_PAGE, INITIAL_PAGE_LIMIT
from helper.function import authenticate, failed_response, get_query_strings_from_request
from services import report_service
from flask import request
import json
from sqlalchemy.orm import clear_mappers


@api.route('/report', methods=['GET', 'POST'])
def report():
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        return json.dumps(failed_response(ERROR_RESPONSE[401]), ensure_ascii=False), 401

    if request.method == 'GET':
        page_cursor: int = get_query_strings_from_request(request, 'cursor', INITIAL_DESCENDING_PAGE_CURSOR)
        limit: int = get_query_strings_from_request(request, 'limit', INITIAL_PAGE_LIMIT)
        page: int = get_query_strings_from_request(request, 'page', INITIAL_PAGE)

    elif request.method == 'POST':
        params: dict = json.loads(request.get_data())

        if 'reason' not in params.keys():
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (reason).'
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        elif params['reason'].strip() == '' or len(params['reason'].strip()) < 10:
            db_session.close()
            error_message = f'고객님의 불편함을 충분히 해소할 수 있도록, 최소 10자 이상의 신고 사유를 작성해 주세요.'
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        else:
            for key in list(params.keys()):
                if key == 'reason':
                    pass
                elif key not in ['userId', 'feedId', 'missionId', 'feedCommentId', 'noticeCommentId', 'missionCommentId']:
                    db_session.close()
                    error_message = f'{ERROR_RESPONSE[400]} ({key}).'
                    return json.dumps(failed_response(error_message), ensure_ascii=False), 400

            reason = params.pop('reason')
            target = list(params.keys())[0]
            target_id = params[target]

            report_mappers()
            report_repo: ReportRepository = ReportRepository(db_session)
            reporting: dict = report_service.report(user_id, target, target_id, reason, report_repo)

            clear_mappers()
            if reporting['result']:
                db_session.commit()
                db_session.close()
                return json.dumps(reporting, ensure_ascii=False), 200
            else:
                db_session.close()
                return json.dumps({key: value for key, value in reporting.items() if key != 'status_code'}, ensure_ascii=False), reporting['status_code']
    else:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[405]} ({request.method})'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 405
