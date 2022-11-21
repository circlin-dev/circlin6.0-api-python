from . import api
from adapter.database import db_session
from adapter.orm import board_mappers, board_comment_mappers, board_like_mappers
from adapter.repository.board import BoardRepository
from adapter.repository.board_comment import BoardCommentRepository
from adapter.repository.board_image import BoardImageRepository
from adapter.repository.board_like import BoardLikeRepository
from adapter.repository.file import FileRepository
from adapter.repository.user import UserRepository
from adapter.repository.push import PushHistoryRepository
from adapter.repository.notification import NotificationRepository

from domain.board import Board, BoardComment, BoardLike

from helper.function import authenticate, get_query_strings_from_request
from helper.constant import ERROR_RESPONSE, INITIAL_ASCENDING_PAGE_CURSOR, INITIAL_DESCENDING_PAGE_CURSOR, INITIAL_PAGE, INITIAL_PAGE_LIMIT

from services import board_service

from flask import request
import json
from sqlalchemy.orm import clear_mappers


@api.route('/board', methods=['GET', 'POST'])
def board_get_post():
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        result: dict = {'result': False, 'error': ERROR_RESPONSE[401]}
        return json.dumps(result, ensure_ascii=False), 401

    if request.method == 'GET':
        page_cursor = get_query_strings_from_request(request, 'cursor', INITIAL_DESCENDING_PAGE_CURSOR)
        limit = get_query_strings_from_request(request, 'limit', INITIAL_PAGE_LIMIT)
        page = get_query_strings_from_request(request, 'page', INITIAL_PAGE)

        board_mappers()
        repo: BoardRepository = BoardRepository(db_session)
        board_list: list = board_service.get_board_list(user_id, page_cursor, limit, repo)
        number_of_boards: int = board_service.get_count_of_the_board(repo)
        clear_mappers()

        last_cursor: [str, None] = None if len(board_list) <= 0 else board_list[-1]['cursor']  # 배열 원소의 cursor string

        result: dict = {
            'result': True,
            'data': board_list,
            'cursor': last_cursor,
            'totalCount': number_of_boards,
        }
        db_session.close()
        return json.dumps(result, ensure_ascii=False), 200

    elif request.method == 'POST':
        data = request.form.to_dict()
        if data['boardCategoryId'] is None or data['boardCategoryId'].strip() == '':
            db_session.close()
            result = {'result': False, 'error': f'{ERROR_RESPONSE[400]} (boardCategoryId)'}
            return json.dumps(result, ensure_ascii=False), 400
        if data['body'] is None or data['body'].strip() == '':
            db_session.close()
            result = {'result': False, 'error': f'{ERROR_RESPONSE[400]} (body)'}
            return json.dumps(result, ensure_ascii=False), 400

        category_id = int(data['boardCategoryId'])
        body = data['body']
        is_show = int(data['isShow'])

        new_board: Board = Board(
            id=None,
            board_category_id=category_id,
            body=body,
            is_show=True if is_show == 1 else False,
            user_id=user_id,
            deleted_at=None
        )

        board_mappers()
        board_repo: BoardRepository = BoardRepository(db_session)
        inserted_board_id: int = board_service.create_new_board(new_board, board_repo)

        num_files = len(request.files.getlist('files[]'))
        if num_files > 1:
            files = request.files.getlist('files[]')  # request.files.getlist('files[]')
            board_image_repo: BoardImageRepository = BoardImageRepository(db_session)
            s3_object_path = f"board/{str(user_id)}"
            for index, file in enumerate(files):
                board_service.create_board_image(inserted_board_id, index, file, s3_object_path, board_image_repo)  # (1) Upload to S3  (2) Add to BoardFile
                # upload_result = upload_single_file_to_s3(file, f'board/{str(user_id)}')
                #
                # if type(upload_result['result']) == str:
                #     connection.close()
                #     result = {'result': False, 'error': f'{ERROR_RESPONSE[500]} ({upload_result["result"]})'}
                #     return json.dumps(result, ensure_ascii=False), 500
                #
                # if upload_result['result'] is True:
                #     sql = Query.into(
                #         BoardFiles
                #     ).columns(
                #         BoardFiles.board_id,
                #         BoardFiles.order,
                #         BoardFiles.file_id
                #     ).insert(
                #         board_id,
                #         index,
                #         upload_result['original_file_id']
                #     ).get_sql()
                #     cursor.execute(sql)
        else:
            pass

        clear_mappers()
        db_session.commit()
        db_session.close()

        result = {'result': True, 'boardId': inserted_board_id}
        return json.dumps(result, ensure_ascii=False), 200
    else:
        db_session.close()
        result: dict = {
            'result': False,
            'error': f'{ERROR_RESPONSE[405]} ({request.method})'
        }
        return json.dumps(result), 405


@api.route('/board/<int:board_id>', methods=['PATCH', 'DELETE'])
def board_patch_delete(board_id: int):
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        result: dict = {'result': False, 'error': ERROR_RESPONSE[401]}
        return json.dumps(result, ensure_ascii=False), 401

    if board_id is None:
        db_session.close()
        result: dict = {'result': False, 'error': f'{ERROR_RESPONSE[400]} (board_id).'}
        return json.dumps(result, ensure_ascii=False), 400

    if request.method == 'DELETE':
        board_mappers()
        repo: BoardRepository = BoardRepository(db_session)

        delete_board: dict = board_service.delete_board(board_id, user_id, repo)
        clear_mappers()

        if delete_board['result']:
            db_session.commit()
            db_session.close()
            return json.dumps(delete_board, ensure_ascii=False), 200
        else:
            db_session.close()
            return json.dumps({key: value for key, value in delete_board.items() if key != 'status_code'}, ensure_ascii=False), delete_board['status_code']
    elif request.method == 'PATCH':
        data: dict = json.loads(request.get_data())
        new_body: [str, None] = data['body'] if data['body'] is not None or data['body'].strip() != '' else None
        new_is_show: [int, None] = int(data['isShow']) if data['isShow'] is not None else None
        new_board_category_id: [int, None] = int(data['boardCategoryId']) if data['boardCategoryId'] is not None else None

        if new_body is None or new_body.strip() == '':
            db_session.close()
            result: dict = {
                'result': False,
                'error': f'{ERROR_RESPONSE[400]} (body).'
            }
            return json.dumps(result, ensure_ascii=False), 400
        elif new_is_show is None:
            db_session.close()
            result: dict = {
                'result': False,
                'error': f'{ERROR_RESPONSE[400]} (isShow).'
            }
            return json.dumps(result, ensure_ascii=False), 400
        elif new_board_category_id is None:
            db_session.close()
            result: dict = {
                'result': False,
                'error': f'{ERROR_RESPONSE[400]} (boardCategoryId).'
            }
            return json.dumps(result, ensure_ascii=False), 400
        else:
            board_mappers()
            repo: BoardRepository = BoardRepository(db_session)
            new_board: Board = Board(
                id=board_id,
                user_id=user_id,
                body=new_body,
                is_show=True if new_is_show == 1 else False,
                board_category_id=new_board_category_id,
                deleted_at=None
            )
            update_board: dict = board_service.update_board(new_board, user_id, repo)
            clear_mappers()

            if update_board['result']:
                db_session.commit()
                db_session.close()
                return json.dumps(update_board, ensure_ascii=False), 200
            else:
                db_session.close()
                return json.dumps({key: value for key, value in update_board.items() if key != 'status_code'}, ensure_ascii=False), update_board['status_code']
    else:
        db_session.close()
        result = {
            'result': False,
            'error': f'{ERROR_RESPONSE[405]} ({request.method})'
        }
        return json.dumps(result), 405


@api.route('/board/<int:board_id>/like', methods=['GET', 'POST', 'DELETE'])
def board_like(board_id: int):
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        result: dict = {'result': False, 'error': ERROR_RESPONSE[401]}
        return json.dumps(result, ensure_ascii=False), 401

    if board_id is None:
        db_session.close()
        result: dict = {'result': False, 'error': f'{ERROR_RESPONSE[400]} (board_id).'}
        return json.dumps(result, ensure_ascii=False), 400

    if request.method == 'GET':
        page_cursor: int = get_query_strings_from_request(request, 'cursor', INITIAL_ASCENDING_PAGE_CURSOR)
        limit: int = get_query_strings_from_request(request, 'limit', INITIAL_PAGE_LIMIT)
        page: int = get_query_strings_from_request(request, 'page', INITIAL_PAGE)

        board_like_mappers()
        repo: BoardLikeRepository = BoardLikeRepository(db_session)
        liked_users: list = board_service.get_user_list_who_like_this_board(board_id, page_cursor, limit, repo)
        number_of_like: int = board_service.get_like_count_of_the_board(board_id, repo)
        clear_mappers()

        last_cursor: [str, None] = None if len(liked_users) <= 0 else liked_users[-1]['cursor']  # 배열 원소의 cursor string

        result: dict = {
            'result': True,
            'data': liked_users,
            'cursor': last_cursor,
            'totalCount': number_of_like,
        }
        db_session.close()
        return json.dumps(result, ensure_ascii=False), 200

    elif request.method == 'POST':
        board_like_mappers()
        board_like_repo: BoardLikeRepository = BoardLikeRepository(db_session)
        board_repo: BoardRepository = BoardRepository(db_session)
        user_repo: UserRepository = UserRepository(db_session)
        push_hisotry_repo: PushHistoryRepository = PushHistoryRepository(db_session)
        notification_repo: NotificationRepository = NotificationRepository(db_session)

        new_like: BoardLike = BoardLike(id=None, user_id=user_id, board_id=board_id)
        like: dict = board_service.increase_like(new_like, board_like_repo, board_repo, user_repo, push_hisotry_repo, notification_repo)
        clear_mappers()

        if like['result']:
            db_session.commit()
            db_session.close()
            return json.dumps(like, ensure_ascii=False), 200
        else:
            db_session.close()
            return json.dumps(like, ensure_ascii=False), 400

    elif request.method == 'DELETE':
        board_like_mappers()
        board_like_repo: BoardLikeRepository = BoardLikeRepository(db_session)
        board_repo: BoardRepository = BoardRepository(db_session)

        like_record: BoardLike = BoardLike(id=None, user_id=user_id, board_id=board_id)
        cancel_like: dict = board_service.decrease_like(like_record, board_like_repo, board_repo)
        clear_mappers()

        if cancel_like['result']:
            db_session.commit()
            db_session.close()
            return json.dumps(cancel_like, ensure_ascii=False), 200
        else:
            db_session.close()
            return json.dumps(cancel_like, ensure_ascii=False), 400

    else:
        db_session.close()
        result: dict = {
            'result': False,
            'error': f'{ERROR_RESPONSE[405]} ({request.method})'
        }
        return json.dumps(result), 405


@api.route('/board/<int:board_id>/comment', methods=['GET', 'POST'])
def board_comment(board_id: int):
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        result = {'result': False, 'error': ERROR_RESPONSE[401]}
        return json.dumps(result, ensure_ascii=False), 401

    if board_id is None:
        db_session.close()
        result = {'result': False, 'error': f'{ERROR_RESPONSE[400]} (board_id).'}
        return json.dumps(result, ensure_ascii=False), 400

    if request.method == 'GET':
        page_cursor: int = get_query_strings_from_request(request, 'cursor', INITIAL_DESCENDING_PAGE_CURSOR)
        limit: int = get_query_strings_from_request(request, 'limit', INITIAL_PAGE_LIMIT)
        page: int = get_query_strings_from_request(request, 'page', INITIAL_PAGE)

        board_comment_mappers()
        repo: BoardCommentRepository = BoardCommentRepository(db_session)
        comments: list = board_service.get_comments(board_id, page_cursor, limit, user_id, repo)
        number_of_comment: int = board_service.get_comment_count_of_the_board(board_id, repo)
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
        params: dict = json.loads(request.get_data())
        comment: [str, None] = params['comment']
        group: [int, None] = params['group']

        if comment is None or comment.strip() == '':
            db_session.close()
            result: dict = {
                'result': False,
                'error': f'{ERROR_RESPONSE[400]} (comment)'
            }
            return json.dumps(result, ensure_ascii=False), 400
        if group is None:
            db_session.close()
            result: dict = {
                'result': False,
                'error': f'{ERROR_RESPONSE[400]} (group)'
            }
            return json.dumps(result, ensure_ascii=False), 400

        board_comment_mappers()
        board_comment_repo: BoardCommentRepository = BoardCommentRepository(db_session)
        board_repo: BoardRepository = BoardRepository(db_session)
        user_repo: UserRepository = UserRepository(db_session)
        push_history_repo: PushHistoryRepository = PushHistoryRepository(db_session)
        notification_repo: NotificationRepository = NotificationRepository(db_session)

        new_board_comment: BoardComment = BoardComment(
            id=None,
            board_id=board_id,
            group=group,
            comment=comment,
            user_id=user_id,
            depth=0
        )

        add_comment: dict = board_service.add_comment(new_board_comment, board_comment_repo, board_repo, user_repo, push_history_repo, notification_repo)
        clear_mappers()

        if add_comment['result']:
            db_session.commit()
            db_session.close()
            return json.dumps(add_comment, ensure_ascii=False), 200
        else:
            db_session.close()
            return json.dumps({key: value for key, value in add_comment.items() if key != 'status_code'}, ensure_ascii=False), add_comment['status_code']

    else:
        db_session.close()
        result: dict = {
            'result': False,
            'error': f'{ERROR_RESPONSE[405]} ({request.method})'
        }
        return json.dumps(result), 405


@api.route('/board/<int:board_id>/comment/<int:board_comment_id>', methods=['PATCH', 'DELETE'])
def board_comment_manipulate(board_id: int, board_comment_id: int):
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        result: dict = {'result': False, 'error': ERROR_RESPONSE[401]}
        return json.dumps(result, ensure_ascii=False), 401

    if board_id is None:
        db_session.close()
        result: dict = {'result': False, 'error': f'{ERROR_RESPONSE[400]} (board_id).'}
        return json.dumps(result, ensure_ascii=False), 400

    if board_comment_id is None:
        db_session.close()
        result: dict = {'result': False, 'error': f'{ERROR_RESPONSE[400]} (comment_id).'}
        return json.dumps(result, ensure_ascii=False), 400

    if request.method == 'PATCH':
        new_comment: [str, None] = json.loads(request.get_data())['comment']

        if new_comment is None or new_comment.strip() == '':
            db_session.close()
            result: dict = {
                'result': False,
                'error': f'{ERROR_RESPONSE[400]} (comment)'
            }
            return json.dumps(result, ensure_ascii=False), 400

        board_comment_mappers()
        repo: BoardCommentRepository = BoardCommentRepository(db_session)
        new_comment_record: BoardComment = BoardComment(
            id=board_comment_id,
            user_id=user_id,
            board_id=board_id,
            comment=new_comment,
            depth=0,
            group=0
        )
        update_comment: dict = board_service.update_comment(new_comment_record, repo)
        clear_mappers()

        if update_comment['result']:
            db_session.commit()
            db_session.close()
            return json.dumps(update_comment, ensure_ascii=False), 200
        else:
            db_session.close()
            return json.dumps({key: value for key, value in update_comment.items() if key != 'status_code'}, ensure_ascii=False), update_comment['status_code']
    elif request.method == 'DELETE':
        board_comment_mappers()
        repo: BoardCommentRepository = BoardCommentRepository(db_session)
        comment_record: BoardComment = BoardComment(
            id=board_comment_id,
            user_id=user_id,
            board_id=board_id,
            comment='',
            depth=0,
            group=0
        )
        delete_comment: dict = board_service.delete_comment(comment_record, repo)
        clear_mappers()

        if delete_comment['result']:
            db_session.commit()
            db_session.close()
            return json.dumps(delete_comment, ensure_ascii=False), 200
        else:
            db_session.close()
            return json.dumps({key: value for key, value in delete_comment.items() if key != 'status_code'}, ensure_ascii=False), delete_comment['status_code']
    else:
        db_session.close()
        result: dict = {
            'result': False,
            'error': f'{ERROR_RESPONSE[405]} ({request.method})'
        }
        return json.dumps(result), 405
