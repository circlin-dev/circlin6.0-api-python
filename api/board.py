from global_configuration.table import Boards, Files, BoardCategories, BoardFiles
from . import api
from global_configuration.constants import API_ROOT
from global_configuration.helper import db_connection, get_dict_cursor, authenticate, upload_single_file_to_s3
from flask import request, url_for
import json
import os
from pypika import MySQLQuery as Query, Criterion, functions as fn


# region 게시물
# 전체 조회
@api.route('/board', methods=['GET'])
def get_boards():
    connection = db_connection()
    cursor = get_dict_cursor(connection)
    endpoint = API_ROOT + url_for('api.get_boards')
    authentication = authenticate(request, cursor)

    if authentication is None:
        connection.close()
        result = {'result': False, 'error': '알 수 없는 사용자입니다.'}
        return json.dumps(result, ensure_ascii=False), 401

    connection.close()
    user_id = authentication['user_id']

    # 페이징

    return json.dumps({'user_id': user_id}, ensure_ascii=False), 200


# 단건 조회(상세 조회)
@api.route('/board/<board_id>', methods=['GET'])
def get_a_board(board_id: int):
    return 'GET_board', 200


# 등록
@api.route('/board', methods=['POST'])
def post_a_board():
    connection = db_connection()
    cursor = get_dict_cursor(connection)
    endpoint = API_ROOT + url_for('api.post_a_board')
    authentication = authenticate(request, cursor)

    if authentication is None:
        connection.close()
        result = {'result': False, 'error': '알 수 없는 사용자입니다.'}
        return json.dumps(result, ensure_ascii=False), 401
    user_id = authentication['user_id']

    # data = json.loads(request.get_data())
    data = request.form.to_dict()
    category_id = int(data['boardCategoryId'])
    body = data['body']
    is_show = data['isShow']

    if category_id is None:
        result = {'result': False, 'error': '게시글의 카테고리를 골라주세요.'}
        return json.dumps(result, ensure_ascii=False), 400
    if body is None or body.strip() == '':
        result = {'result': False, 'error': '게시글 내용을 입력해 주세요.'}
        return json.dumps(result, ensure_ascii=False), 400

    sql = Query.into(
        Boards
    ).columns(
        Boards.user_id,
        Boards.board_category_id,
        Boards.body,
        Boards.is_show
    ).insert(
        user_id,
        category_id,
        body,
        is_show
    ).get_sql()

    try:
        cursor.execute(sql)
        connection.commit()
        board_id = int(cursor.lastrowid)
        # return json.dumps(result, ensure_ascii=False), 200
    except Exception as e:
        connection.close()
        result = {'result': False, 'error': f'서버 오류로 게시글을 업로드하지 못했어요. 고객센터에 문의해 주세요.({e})'}
        return json.dumps(result, ensure_ascii=False), 500

    num_files = len(request.files.to_dict())
    if num_files < 1:
        connection.close()
        result = {'result': True, 'boardId': board_id}
        return json.dumps(result, ensure_ascii=False), 200
    else:
        files = request.files.getlist('files[]')

        for index, file in enumerate(files):
            upload_result = upload_single_file_to_s3(file, f'board/{str(user_id)}')

            if type(upload_result['result']) == str:
                connection.close()
                result = {'result': False, 'error': upload_result['result']}
                return json.dumps(result, ensure_ascii=False), 500

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
            #     connection.commit()

        connection.close()
        result = {'result': True, 'boardId': board_id}
        return json.dumps(result, ensure_ascii=False), 200

# 팔로워가 쓴 최신 글 조회
@api.route('/board/follower', methods=['GET'])
def get_followers_board():
    # 페이징
    return 'GET_follower\'s board', 200


# 게시글 수정
@api.route('/board/<board_id>', methods=['PATCH'])
def update_a_board(board_id: int):
    connection = db_connection()
    cursor = get_dict_cursor(connection)
    endpoint = API_ROOT + url_for('api.update_a_board', board_id=board_id)
    connection.close()
    return 'PATCH_board', 200


# 게시글 삭제
@api.route('/board/<board_id>', methods=['DELETE'])
def delete_a_board(board_id: int):
    connection = db_connection()
    cursor = get_dict_cursor(connection)
    endpoint = API_ROOT + url_for('api.delete_a_board', board_id=board_id)
    connection.close()
    return 'DELETE_board', 200
# endregion


# region 좋아요
# 좋아요 리스트 조회
@api.route('/board/<board_id>/like', methods=['GET'])
def get_board_likes(board_id: int):
    connection = db_connection()
    cursor = get_dict_cursor(connection)
    endpoint = API_ROOT + url_for('api.get_board_likes', board_id=board_id)
    connection.close()

    # 페이징
    return 'GET_board_likes', 200
# endregion


# region 댓글 남기기
# 댓글 조회

# 댓글 작성

# 댓글 삭제

# endregion


# region 카테고리
# 카테고리 조회
@api.route('/board/category', methods=['GET'])
def get_board_categories():
    connection = db_connection()
    cursor = get_dict_cursor(connection)
    endpoint = API_ROOT + url_for('api.get_board_categories')
    authentication = authenticate(request, cursor)

    if authentication is None:
        connection.close()
        result = {'result': False, 'error': '알 수 없는 사용자입니다.'}
        return json.dumps(result, ensure_ascii=False), 401

    sql = Query.from_(
        BoardCategories
    ).select(
        BoardCategories.id,
        BoardCategories.title.as_('label')
    ).get_sql()

    cursor.execute(sql)
    categories = cursor.fetchall()
    connection.close()

    result = {
        'result': True,
        'data': categories
    }
    return json.dumps(result, ensure_ascii=False), 200
# endregion
