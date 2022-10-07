from global_configuration.table import Boards, Files, BoardCategories, BoardFiles, BoardLikes, BoardComments, Users
from . import api
from global_configuration.constants import API_ROOT, INITIAL_DESCENDING_PAGE_CURSOR, INITIAL_ASCENDING_PAGE_CURSOR, \
    INITIAL_PAGE_LIMIT, INITIAL_PAGE, BOARD_PUSH_TITLE
from global_configuration.helper import db_connection, get_dict_cursor, authenticate, upload_single_file_to_s3, \
    get_query_strings_from_request, create_notification, send_fcm_push
from flask import request, url_for
import json
import os
import random
from pypika import MySQLQuery as Query, Criterion, functions as fn
# from flask_caching import Cache
# from app import cache, app
from global_configuration.cache import cache

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
        result = {'result': False, 'error': '요청을 보낸 사용자는 알 수 없는 사용자입니다.'}
        return json.dumps(result, ensure_ascii=False), 401
    user_id = authentication['user_id']

    page_cursor = get_query_strings_from_request(request, 'cursor', INITIAL_DESCENDING_PAGE_CURSOR)
    limit = get_query_strings_from_request(request, 'limit', INITIAL_PAGE_LIMIT)
    page = get_query_strings_from_request(request, 'page', INITIAL_PAGE)

    sql = f"""
        SELECT
            b.id,
            b.body,
            IFNULL(JSON_ARRAYAGG(
                JSON_OBJECT(
                    'order', bf.order,
                    'mimeType', f.mime_type,
                    'pathname', f.pathname,
                    'resized', (SELECT JSON_ARRAYAGG(JSON_OBJECT('mimeType', ff.mime_type,
                        'pathname', ff.pathname,
                        'width', ff.width)) FROM files ff WHERE f.id = ff.original_file_id)
                )
            ), JSON_ARRAY()) AS images,
            JSON_OBJECT(
                'id', u.id,
                'nickname', u.nickname,
                'profile', u.profile_image,
                'followed', CASE
                                WHEN {user_id} in (SELECT COUNT(*) FROM follows WHERE user_id = b.user_id) THEN 1
                                ELSE 0
                            END,
                'followers', (SELECT COUNT(*) FROM follows WHERE target_id = b.user_id)
            ) AS user,
            DATE_FORMAT(b.created_at, '%Y/%m/%d %H:%i:%s') AS createdAt,
            (SELECT COUNT(*) FROM board_likes bl WHERE bl.board_id = b.id) AS likesCount,
            (SELECT COUNT(*) FROM board_comments bcm WHERE bcm.board_id = b.id) AS commentsCount,
            CASE
                WHEN {user_id} in ((SELECT bl.user_id FROM board_likes bl WHERE bl.board_id = b.id)) THEN 1
                ELSE 0
            END AS liked,
            b.board_category_id as boardCategoryId,
            CONCAT(LPAD(b.id, 15, '0')) as `cursor`
        FROM
            boards b
        LEFT JOIN
                board_files bf
            ON
                b.id = bf.board_id
        INNER JOIN
                files f
            ON
                bf.file_id = f.id
        INNER JOIN
                users u
            ON
                u.id = b.user_id
        WHERE b.deleted_at IS NULL
        AND b.is_show = 1
        AND b.user_id != {user_id}        
        AND b.id < {page_cursor}
        GROUP BY b.id
        ORDER BY b.id DESC
        LIMIT {limit}
    """

    cursor.execute(sql)
    boards = cursor.fetchall()

    sql = f"""
        WITH board_list AS (
            SELECT
                b.id,
                b.body,
                IFNULL(JSON_ARRAYAGG(
                    JSON_OBJECT(
                        'order', bf.order,
                        'mimeType', f.mime_type,
                        'pathname', f.pathname,
                        'resized', (SELECT JSON_ARRAYAGG(JSON_OBJECT('mimeType', ff.mime_type,
                            'pathname', ff.pathname,
                            'width', ff.width)) FROM files ff WHERE f.id = ff.original_file_id)
                    )
                ), JSON_ARRAY()) AS images,
                JSON_OBJECT(
                    'id', u.id,
                    'nickname', u.nickname,
                    'profile', u.profile_image,
                    'followed', CASE
                                    WHEN {user_id} in (SELECT COUNT(*) FROM follows WHERE user_id = b.user_id) THEN 1
                                    ELSE 0
                                END,
                    'followers', (SELECT COUNT(*) FROM follows WHERE target_id = b.user_id)
                ) AS user,
                DATE_FORMAT(b.created_at, '%Y/%m/%d %H:%i:%s') AS createdAt,
                (SELECT COUNT(*) FROM board_likes bl WHERE bl.board_id = b.id) AS likesCount,
                (SELECT COUNT(*) FROM board_comments bcm WHERE bcm.board_id = b.id) AS commentsCount,
                CASE
                    WHEN {user_id} in ((SELECT bl.user_id FROM board_likes bl WHERE bl.board_id = b.id)) THEN 1
                    ELSE 0
                END AS liked,
                b.board_category_id as boardCategoryId
            FROM
                boards b
            LEFT JOIN
                    board_files bf
                ON
                    b.id = bf.board_id
            INNER JOIN
                    files f
                ON
                    bf.file_id = f.id
            INNER JOIN
                    users u
                ON
                    u.id = b.user_id
            WHERE b.deleted_at IS NULL
            AND b.is_show = 1
            AND b.user_id != {user_id}
            GROUP BY b.id)
        SELECT COUNT(*) AS total_count FROM board_list"""
    cursor.execute(sql)
    total_count = cursor.fetchone()['total_count']
    connection.close()

    for board in boards:
        board['user'] = json.loads(board['user'])
        board['user']['followed'] = True if board['user']['followed'] == 1 or board['user']['id'] == user_id else False
        board['images'] = json.loads(board['images']) if json.loads(board['images'])[0]['order'] is not None else []

    last_cursor = None if len(boards) <= 0 else boards[-1]['cursor']  # 배열 원소의 cursor string
    response = {
        'result': True,
        'data': boards,
        'cursor': last_cursor,
        'totalCount': total_count
    }
    return json.dumps(response, ensure_ascii=False), 200


# 단건 조회(상세 조회)
@api.route('/board/<board_id>', methods=['GET'])
def get_a_board(board_id: int):
    connection = db_connection()
    cursor = get_dict_cursor(connection)
    endpoint = API_ROOT + url_for('api.post_a_board')
    authentication = authenticate(request, cursor)

    if authentication is None:
        connection.close()
        result = {'result': False, 'error': '요청을 보낸 사용자는 알 수 없는 사용자입니다.'}
        return json.dumps(result, ensure_ascii=False), 401
    user_id = authentication['user_id']

    sql = f"""
        SELECT
            b.id,
            b.body,
            IFNULL(JSON_ARRAYAGG(
                JSON_OBJECT(
                    'order', bf.order,
                    'mimeType', f.mime_type,
                    'pathname', f.pathname,
                    'resized', (SELECT JSON_ARRAYAGG(JSON_OBJECT('mimeType', ff.mime_type,
                        'pathname', ff.pathname,
                        'width', ff.width)) FROM files ff WHERE f.id = ff.original_file_id)
                )
            ), JSON_ARRAY()) AS images,
            JSON_OBJECT(
                'id', u.id,
                'nickname', u.nickname,
                'profile', u.profile_image,
                'followed', CASE
                                WHEN {user_id} in (SELECT target_id FROM follows WHERE user_id = b.user_id) THEN 1
                                ELSE 0
                            END,
                'followers', (SELECT COUNT(*) FROM follows WHERE target_id = b.user_id)
            ) AS user,
            DATE_FORMAT(b.created_at, '%Y/%m/%d %H:%i:%s') AS createdAt,
            (SELECT COUNT(*) FROM board_likes bl WHERE bl.board_id = b.id) AS likesCount,
            (SELECT COUNT(*) FROM board_comments bcm WHERE bcm.board_id = b.id AND bcm.deleted_at IS NULL) AS commentsCount,
            CASE
                WHEN {user_id} in ((SELECT bl.user_id FROM board_likes bl WHERE bl.board_id = b.id)) THEN 1
                ELSE 0
            END AS liked,
            b.board_category_id as boardCategoryId
        FROM
            boards b
        LEFT JOIN
                board_files bf
            ON
                b.id = bf.board_id
        LEFT JOIN
                files f
            ON
                bf.file_id = f.id
        INNER JOIN
                users u
            ON
                u.id = b.user_id
        WHERE b.deleted_at IS NULL
        AND b.is_show = 1
        AND b.id = {board_id}
        GROUP BY b.id
    """

    cursor.execute(sql)
    board = cursor.fetchone()
    connection.close()

    if board is not None:
        board['user'] = json.loads(board['user'])
        board['user']['followed'] = True if board['user']['followed'] == 1 or board['user']['id'] == user_id else False
        board['images'] = json.loads(board['images']) if json.loads(board['images'])[0]['order'] is not None else []
        result = {
            'result': True,
            'data': board
        }
        return json.dumps(result, ensure_ascii=False), 200
    else:
        result = {
            'result': False,
            'error': "존재하지 않거나, 삭제되었거나, 공개되지 않은 게시물입니다."
        }
        return json.dumps(result, ensure_ascii=False), 400


# 특정 유저의 게시글만 전체 조회(모아보기)
@api.route('/board/user/<target_user_id>', methods=['GET'])
def get_user_boards(target_user_id: int):
    connection = db_connection()
    cursor = get_dict_cursor(connection)
    endpoint = API_ROOT + url_for('api.get_user_boards', target_user_id=target_user_id)
    authentication = authenticate(request, cursor)

    if authentication is None:
        connection.close()
        result = {'result': False, 'error': '요청을 보낸 사용자는 알 수 없는 사용자입니다.'}
        return json.dumps(result, ensure_ascii=False), 401
    user_id = authentication['user_id']

    page_cursor = get_query_strings_from_request(request, 'cursor', INITIAL_DESCENDING_PAGE_CURSOR)
    limit = get_query_strings_from_request(request, 'limit', INITIAL_PAGE_LIMIT)
    page = get_query_strings_from_request(request, 'page', INITIAL_PAGE)

    sql = f"""
        SELECT
            b.id,
            b.body,
            IFNULL(JSON_ARRAYAGG(
                JSON_OBJECT(
                    'order', bf.order,
                    'mimeType', f.mime_type,
                    'pathname', f.pathname,
                    'resized', (SELECT JSON_ARRAYAGG(JSON_OBJECT('mimeType', ff.mime_type,
                        'pathname', ff.pathname,
                        'width', ff.width)) FROM files ff WHERE f.id = ff.original_file_id)
                )
            ), JSON_ARRAY()) AS images,
            JSON_OBJECT(
                'id', u.id,
                'nickname', u.nickname,
                'profile', u.profile_image,
                'followed', CASE
                                WHEN {user_id} in (SELECT COUNT(*) FROM follows WHERE user_id = b.user_id) THEN 1
                                ELSE 0
                            END,
                'followers', (SELECT COUNT(*) FROM follows WHERE target_id = b.user_id)
            ) AS user,
            DATE_FORMAT(b.created_at, '%Y/%m/%d %H:%i:%s') AS createdAt,
            (SELECT COUNT(*) FROM board_likes bl WHERE bl.board_id = b.id) AS likesCount,
            (SELECT COUNT(*) FROM board_comments bcm WHERE bcm.board_id = b.id) AS commentsCount,
            CASE
                WHEN {user_id} in ((SELECT bl.user_id FROM board_likes bl WHERE bl.board_id = b.id)) THEN 1
                ELSE 0
            END AS liked,
            b.board_category_id as boardCategoryId,
            CONCAT(LPAD(b.id, 15, '0')) as `cursor`
        FROM
            boards b
        LEFT JOIN
                board_files bf
            ON
                b.id = bf.board_id
        LEFT JOIN
                files f
            ON
                bf.file_id = f.id
        INNER JOIN
                users u
            ON
                u.id = b.user_id
        WHERE b.deleted_at IS NULL
        AND b.is_show = 1
        AND b.user_id = {target_user_id}        
        AND b.id < {page_cursor}
        GROUP BY b.id
        ORDER BY b.id DESC
        LIMIT {limit}
    """

    cursor.execute(sql)
    boards = cursor.fetchall()

    sql = f"""
        WITH board_list AS (
            SELECT
                b.id,
                b.body,
                IFNULL(JSON_ARRAYAGG(
                    JSON_OBJECT(
                        'order', bf.order,
                        'mimeType', f.mime_type,
                        'pathname', f.pathname,
                        'resized', (SELECT JSON_ARRAYAGG(JSON_OBJECT('mimeType', ff.mime_type,
                            'pathname', ff.pathname,
                            'width', ff.width)) FROM files ff WHERE f.id = ff.original_file_id)
                    )
                ), JSON_ARRAY()) AS images,
                JSON_OBJECT(
                    'id', u.id,
                    'nickname', u.nickname,
                    'profile', u.profile_image,
                    'followed', CASE
                                    WHEN {user_id} in (SELECT COUNT(*) FROM follows WHERE user_id = b.user_id) THEN 1
                                    ELSE 0
                                END,
                    'followers', (SELECT COUNT(*) FROM follows WHERE target_id = b.user_id)
                ) AS user,
                DATE_FORMAT(b.created_at, '%Y/%m/%d %H:%i:%s') AS createdAt,
                (SELECT COUNT(*) FROM board_likes bl WHERE bl.board_id = b.id) AS likesCount,
                (SELECT COUNT(*) FROM board_comments bcm WHERE bcm.board_id = b.id) AS commentsCount,
                CASE
                    WHEN {user_id} in ((SELECT bl.user_id FROM board_likes bl WHERE bl.board_id = b.id)) THEN 1
                    ELSE 0
                END AS liked,
                b.board_category_id as boardCategoryId
            FROM
                boards b
            LEFT JOIN
                    board_files bf
                ON
                    b.id = bf.board_id
            INNER JOIN
                    files f
                ON
                    bf.file_id = f.id
            INNER JOIN
                    users u
                ON
                    u.id = b.user_id
            WHERE b.deleted_at IS NULL
            AND b.is_show = 1
            AND b.user_id = {target_user_id}
            GROUP BY b.id)
        SELECT COUNT(*) AS total_count FROM board_list"""
    cursor.execute(sql)
    total_count = cursor.fetchone()['total_count']
    connection.close()

    for board in boards:
        board['user'] = json.loads(board['user'])
        board['user']['followed'] = True if board['user']['followed'] == 1 or board['user']['id'] == user_id else False
        board['images'] = json.loads(board['images']) if json.loads(board['images'])[0]['order'] is not None else []

    last_cursor = None if len(boards) <= 0 else boards[-1]['cursor']  # 배열 원소의 cursor string
    response = {
        'result': True,
        'data': boards,
        'cursor': last_cursor,
        'totalCount': total_count
    }
    return json.dumps(response, ensure_ascii=False), 200


# 등록
@api.route('/board', methods=['POST'])
def post_a_board():
    connection = db_connection()
    cursor = get_dict_cursor(connection)
    endpoint = API_ROOT + url_for('api.post_a_board')
    authentication = authenticate(request, cursor)

    if authentication is None:
        connection.close()
        result = {'result': False, 'error': '요청을 보낸 사용자는 알 수 없는 사용자입니다.'}
        return json.dumps(result, ensure_ascii=False), 401
    user_id = authentication['user_id']

    # data = json.loads(request.get_data())
    data = request.form.to_dict()

    if data['boardCategoryId'] is None or data['boardCategoryId'].strip() == '':
        result = {'result': False, 'error': '게시글의 카테고리가 입력되지 않았습니다.'}
        return json.dumps(result, ensure_ascii=False), 400
    if data['body'] is None or data['body'].strip() == '':
        result = {'result': False, 'error': '게시글 내용을 입력해 주세요.'}
        return json.dumps(result, ensure_ascii=False), 400

    category_id = int(data['boardCategoryId'])
    body = data['body']
    is_show = data['isShow']

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

            if upload_result['result'] is True:
                sql = Query.into(
                    BoardFiles
                ).columns(
                    BoardFiles.board_id,
                    BoardFiles.order,
                    BoardFiles.file_id
                ).insert(
                    board_id,
                    index,
                    upload_result['original_file_id']
                ).get_sql()
                cursor.execute(sql)
                connection.commit()

        connection.close()
        result = {'result': True, 'boardId': board_id}
        return json.dumps(result, ensure_ascii=False), 200


# 팔로워가 쓴 최신 글 조회
@api.route('/board/follower', methods=['GET'])
def get_followers_board():
    connection = db_connection()
    cursor = get_dict_cursor(connection)
    endpoint = API_ROOT + url_for('api.get_followers_board')
    authentication = authenticate(request, cursor)

    if authentication is None:
        connection.close()
        result = {'result': False, 'error': '요청을 보낸 사용자는 알 수 없는 사용자입니다.'}
        return json.dumps(result, ensure_ascii=False), 401
    user_id = authentication['user_id']

    page_cursor = get_query_strings_from_request(request, 'cursor', INITIAL_DESCENDING_PAGE_CURSOR)
    limit = get_query_strings_from_request(request, 'limit', INITIAL_PAGE_LIMIT)
    page = get_query_strings_from_request(request, 'page', INITIAL_PAGE)

    sql = f"""
        SELECT
            JSON_OBJECT(
                'id', b.id,
                'createdAt', DATE_FORMAT(b.created_at, '%Y/%m/%d %H:%i:%s'),
                'updatedAt', DATE_FORMAT(b.updated_at, '%Y/%m/%d %H:%i:%s'),
                'userId', b.user_id,
                'boardCategoryId', b.board_category_id,
                'body', b.body,
                'isShow', b.is_show
            ) AS board_data,
            CONCAT(LPAD(b.id, 15, '0')) as `cursor`
        FROM
            boards b
        INNER JOIN
                follows f ON b.user_id = f.target_id
        WHERE
            f.user_id = {user_id}
        AND
            ABS(TIMESTAMPDIFF(DAY, b.created_at, NOW())) <= 100
        AND b.deleted_at IS NULL
        AND b.is_show = 1
        AND b.id < {page_cursor} 
        ORDER BY b.id DESC, b.created_at DESC
        LIMIT {limit}
    """
    cursor.execute(sql)

    follower_recent_board = cursor.fetchall()
    last_cursor = None if len(follower_recent_board) == 0 else follower_recent_board[-1]['cursor']  # 배열 원소의 cursor string
    follower_recent_board = [json.loads(x['board_data']) for x in follower_recent_board]

    sql = f"""
        SELECT
            COUNT(JSON_OBJECT(
                'id', b.id,
                'createdAt', DATE_FORMAT(b.created_at, '%Y/%m/%d %H:%i:%s'),
                'updatedAt', DATE_FORMAT(b.updated_at, '%Y/%m/%d %H:%i:%s'),
                'userId', b.user_id,
                'boardCategoryId', b.board_category_id,
                'body', b.body,
                'isShow', b.is_show
            )) AS total_count
        FROM
            boards b
        INNER JOIN
                follows f ON b.user_id = f.target_id
        WHERE
            f.user_id = {user_id}
        AND
            ABS(TIMESTAMPDIFF(DAY, b.created_at, NOW())) <= 1000
        AND b.deleted_at IS NULL
        AND b.is_show = 1
    """
    cursor.execute(sql)
    total_count = cursor.fetchone()['total_count']
    connection.close()

    response = {
        'result': True,
        'data': follower_recent_board,
        'cursor': last_cursor,
        'totalCount': total_count
    }
    return json.dumps(response, ensure_ascii=False), 200
    # if len(follower_recent_board) == 0:
    #     connection.close()
    #     response = {
    #         'result': True,
    #         'data': follower_recent_board,
    #         'cursor': last_cursor,
    #         'totalCount': len(follower_recent_board)
    #     }
    #     return json.dumps(response, ensure_ascii=False), 200
    # else:
    #     sql = f"""
    #         SELECT
    #             COUNT(JSON_OBJECT(
    #                 'id', b.id,
    #                 'createdAt', DATE_FORMAT(b.created_at, '%Y/%m/%d %H:%i:%s'),
    #                 'updatedAt', DATE_FORMAT(b.updated_at, '%Y/%m/%d %H:%i:%s'),
    #                 'userId', b.user_id,
    #                 'boardCategoryId', b.board_category_id,
    #                 'body', b.body,
    #                 'isShow', b.is_show
    #             )) AS total_count
    #         FROM
    #             boards b
    #         INNER JOIN
    #                 follows f ON b.user_id = f.target_id
    #         WHERE
    #             f.user_id = {user_id}
    #         AND
    #             ABS(TIMESTAMPDIFF(DAY, b.created_at, NOW())) < 1000
    #         AND b.deleted_at IS NULL
    #         AND b.is_show = 1
    #     """
    #     cursor.execute(sql)
    #     total_count = cursor.fetchone()['total_count']
    #     connection.close()


# 게시글 수정
@api.route('/board/<board_id>', methods=['PATCH'])
def update_a_board(board_id: int):
    connection = db_connection()
    cursor = get_dict_cursor(connection)
    endpoint = API_ROOT + url_for('api.update_a_board', board_id=board_id)
    authentication = authenticate(request, cursor)

    if authentication is None:
        connection.close()
        result = {'result': False, 'error': '요청을 보낸 사용자는 알 수 없는 사용자입니다.'}
        return json.dumps(result, ensure_ascii=False), 401
    user_id = authentication['user_id']

    data = json.loads(request.get_data())

    sql = Query.from_(
        Boards
    ).select(
        Boards.user_id,
        Boards.deleted_at
    ).where(Boards.id == board_id).get_sql()
    cursor.execute(sql)
    target_board = cursor.fetchone()
    target_board_user_id = target_board['user_id']
    target_board_deleted_time = target_board['deleted_at']

    if target_board_user_id != user_id:
        connection.close()
        result = {'result': False, 'error': '해당 유저는 이 게시글에 대한 수정 권한이 없습니다.'}
        return json.dumps(result, ensure_ascii=False), 403
    elif target_board_deleted_time:
        connection.close()
        result = {'result': False, 'error': '이미 삭제된 게시글은 수정할 수 없습니다.'}
        return json.dumps(result, ensure_ascii=False), 400
    else:
        new_body = data['body'] if data['body'] is not None or data['body'].strip() != '' else None
        new_is_show = int(data['isShow']) if data['isShow'] is not None else None
        new_board_category_id = int(data['boardCategoryId']) if data['boardCategoryId'] is not None else None
        if new_body is None or new_body.strip() == '':
            connection.close()
            result = {
                'result': False,
                'error': '누락된 필수 데이터가 있어 댓글을 입력할 수 없습니다(body).'
            }
            return json.dumps(result, ensure_ascii=False), 400
        elif new_is_show is None:
            connection.close()
            result = {
                'result': False,
                'error': '누락된 필수 데이터가 있어 댓글을 입력할 수 없습니다(isShow).'
            }
            return json.dumps(result, ensure_ascii=False), 400
        elif new_board_category_id is None:
            connection.close()
            result = {
                'result': False,
                'error': '누락된 필수 데이터가 있어 댓글을 입력할 수 없습니다(boardCategoryId).'
            }
            return json.dumps(result, ensure_ascii=False), 400
        else:
            sql = Query.update(
                Boards
            ).set(
                Boards.body, new_body
            ).set(
                Boards.is_show, new_is_show
            ).set(
                Boards.board_category_id, new_board_category_id
            ).where(
                Boards.id == board_id
            ).get_sql()

            cursor.execute(sql)
            connection.commit()
            connection.close()

            result = {'result': True}
            return json.dumps(result, ensure_ascii=False), 200


# 게시글 삭제
@api.route('/board/<board_id>', methods=['DELETE'])
def delete_a_board(board_id: int):
    connection = db_connection()
    cursor = get_dict_cursor(connection)
    endpoint = API_ROOT + url_for('api.delete_a_board', board_id=board_id)
    authentication = authenticate(request, cursor)

    if authentication is None:
        connection.close()
        result = {'result': False, 'error': '요청을 보낸 사용자는 알 수 없는 사용자입니다.'}
        return json.dumps(result, ensure_ascii=False), 401
    user_id = authentication['user_id']

    sql = Query.from_(
        Boards
    ).select(
        Boards.id,
        Boards.user_id,
        Boards.deleted_at
    ).where(
        Boards.id == board_id
    ).get_sql()

    cursor.execute(sql)
    data = cursor.fetchone()

    if data is None:
        connection.close()
        result = {'result': False, 'error': '존재하지 않는 게시물입니다.'}
        return json.dumps(result, ensure_ascii=False), 400
    elif data['user_id'] != user_id:
        connection.close()
        result = {'result': False, 'error': '해당 유저는 이 게시글에 대한 삭제 권한이 없습니다.'}
        return json.dumps(result, ensure_ascii=False), 403
    elif data['deleted_at'] is not None:
        connection.close()
        result = {'result': False, 'error': '이미 삭제된 게시물입니다.'}
        return json.dumps(result, ensure_ascii=False), 400
    else:
        sql = Query.update(
            Boards
        ).set(
            Boards.deleted_at, fn.Now()
        ).where(
            Boards.id == board_id
        ).get_sql()

        cursor.execute(sql)
        connection.commit()
        connection.close()

        result = {'result': True}
        return json.dumps(result, ensure_ascii=False), 200
# endregion


# region 좋아요
# 좋아요 리스트 조회
@api.route('/board/<board_id>/like', methods=['GET'])
def get_board_likes(board_id: int):
    connection = db_connection()
    cursor = get_dict_cursor(connection)
    endpoint = API_ROOT + url_for('api.get_board_likes', board_id=board_id)

    authentication = authenticate(request, cursor)
    if authentication is None:
        connection.close()
        result = {'result': False, 'error': '요청을 보낸 사용자는 알 수 없는 사용자입니다.'}
        return json.dumps(result, ensure_ascii=False), 401

    page_cursor = get_query_strings_from_request(request, 'cursor', INITIAL_ASCENDING_PAGE_CURSOR)
    limit = get_query_strings_from_request(request, 'limit', INITIAL_PAGE_LIMIT)
    page = get_query_strings_from_request(request, 'page', INITIAL_PAGE)

    sql = f"""
        SELECT 
            u.id,
            u.nickname,
            u.greeting,
            u.profile_image,
            CONCAT(LPAD(bl.id, 15, '0')) as `cursor`
        FROM
            board_likes bl
        INNER JOIN
                users u ON u.id = bl.user_id
        WHERE
            board_id = {board_id}
        AND
            bl.id > {page_cursor}
        LIMIT {limit}
    """
    cursor.execute(sql)
    liked_users = cursor.fetchall()

    # if len(liked_users) == 0:  # 좋아요 누른 사람이 없을 경우 return
    #     connection.close()
    #     result = []
    #     response = {
    #         'result': True,
    #         'data': result,
    #         'cursor': None,
    #         'totalCount': len(result)
    #     }
    #     return json.dumps(response, ensure_ascii=False), 200
    sql = Query.from_(
        BoardLikes
    ).select(
        fn.Count(BoardLikes.id).distinct().as_('total_count')
    ).where(
        Criterion.all([
            BoardLikes.board_id == board_id
        ])
    ).get_sql()
    cursor.execute(sql)
    total_count = cursor.fetchone()['total_count']
    connection.close()

    last_cursor = None if len(liked_users) <= 0 else liked_users[-1]['cursor']  # 배열 원소의 cursor string

    response = {
        'result': True,
        'data': liked_users,
        'cursor': last_cursor,
        'totalCount': total_count
    }

    # 페이징
    return json.dumps(response), 200


# 좋아요
@api.route('/board/<board_id>/like', methods=['POST'])
def post_like(board_id: int):
    connection = db_connection()
    cursor = get_dict_cursor(connection)
    endpoint = API_ROOT + url_for('api.post_like',  board_id=board_id)

    authentication = authenticate(request, cursor)
    if authentication is None:
        connection.close()
        result = {'result': False, 'error': '요청을 보낸 사용자는 알 수 없는 사용자입니다.'}
        return json.dumps(result, ensure_ascii=False), 401
    user_id = authentication['user_id']

    sql = Query.from_(
        Boards
    ).select(
        Boards.id,
        Boards.user_id,
        Boards.is_show,
        Boards.deleted_at
    ).where(
        Criterion.all([
            Boards.id == board_id
        ])
    ).get_sql()
    cursor.execute(sql)
    target_board = cursor.fetchone()

    if target_board is None:
        connection.close()
        result = {
            'result': False,
            'error': '올바른 시도가 아닙니다(존재하지 않는 게시물).'
        }
        return json.dumps(result, ensure_ascii=False), 400
    elif target_board['deleted_at'] is not None:
        connection.close()
        result = {
            'result': False,
            'error': '올바른 시도가 아닙니다(삭제된 게시물).'
        }
        return json.dumps(result, ensure_ascii=False), 400
    elif target_board['is_show'] == 0 and target_board['user_id'] != user_id:
        connection.close()
        result = {
            'result': False,
            'error': '올바른 시도가 아닙니다(숨겨진 게시물).'
        }
        return json.dumps(result, ensure_ascii=False), 400
    else:
        sql = Query.from_(
            BoardLikes
        ).select(
            BoardLikes.id
        ).where(
            Criterion.all([
                BoardLikes.user_id == user_id,
                BoardLikes.board_id == board_id
            ])
        ).get_sql()

        cursor.execute(sql)
        like_record = cursor.fetchone()

        if like_record is not None:
            connection.close()
            result = {
                'result': False,
                'error': '이미 좋아요를 한 게시물입니다.'
            }
            return json.dumps(result, ensure_ascii=False), 400
        else:
            sql = Query.into(
                BoardLikes
            ).columns(
                BoardLikes.board_id,
                BoardLikes.user_id
            ).insert(
                board_id,
                user_id,
            ).get_sql()

            cursor.execute(sql)
            connection.commit()

            # 알림, 푸시
            # 좋아요 누른 유저의 닉네임
            sql = Query.from_(
                Users
            ).select(
                Users.nickname
            ).where(
                Users.id == user_id
            ).get_sql()
            cursor.execute(sql)
            user_nickname = cursor.fetchone()['nickname']

            if target_board['user_id'] != user_id:
                create_notification(int(target_board['user_id']), 'board_like', user_id, 'board', board_id, None, None)

                push_target = list()
                push_target.append(int(target_board['user_id']))
                push_type = f"board_like.{str(board_id)}"
                push_body = f'{user_nickname}님이 내 게시글을 좋아합니다.'
                send_fcm_push(push_target, push_type, user_id, int(board_id), None, BOARD_PUSH_TITLE, push_body)

            connection.close()
            result = {'result': True}
            return json.dumps(result, ensure_ascii=False), 200


# 좋아요 해제
@api.route('/board/<board_id>/like', methods=['DELETE'])
def delete_like(board_id: int):
    connection = db_connection()
    cursor = get_dict_cursor(connection)
    endpoint = API_ROOT + url_for('api.delete_like', board_id=board_id)

    authentication = authenticate(request, cursor)
    if authentication is None:
        connection.close()
        result = {'result': False, 'error': '요청을 보낸 사용자는 알 수 없는 사용자입니다.'}
        return json.dumps(result, ensure_ascii=False), 401
    user_id = authentication['user_id']

    sql = Query.from_(
        Boards
    ).select(
        Boards.id,
        Boards.user_id,
        Boards.is_show,
        Boards.deleted_at
    ).where(
        Criterion.all([
            Boards.id == board_id
        ])
    ).get_sql()
    cursor.execute(sql)
    target_board = cursor.fetchone()

    if target_board is None:
        connection.close()
        result = {
            'result': False,
            'error': '올바른 시도가 아닙니다(존재하지 않는 게시물).'
        }
        return json.dumps(result, ensure_ascii=False), 400
    elif target_board['deleted_at'] is not None:
        connection.close()
        result = {
            'result': False,
            'error': '올바른 시도가 아닙니다(삭제된 게시물).'
        }
        return json.dumps(result, ensure_ascii=False), 400
    elif target_board['is_show'] == 0 and target_board['user_id'] != user_id:
        connection.close()
        result = {
            'result': False,
            'error': '올바른 시도가 아닙니다(숨겨진 게시물).'
        }
        return json.dumps(result, ensure_ascii=False), 400
    else:
        sql = Query.from_(
            BoardLikes
        ).select(
            BoardLikes.id
        ).where(
            Criterion.all([
                BoardLikes.user_id == user_id,
                BoardLikes.board_id == board_id
            ])
        ).get_sql()
        cursor.execute(sql)
        data = cursor.fetchone()

        if data is None:
            connection.close()
            result = {
                'result': False,
                'error': '올바른 시도가 아닙니다(좋아요하지 않은 게시물이거나, 이미 좋아요 취소된 게시물).'
            }
            return json.dumps(result, ensure_ascii=False), 400
        else:
            sql = Query.from_(
                BoardLikes
            ).delete(
            ).where(
                Criterion.all([
                    BoardLikes.board_id == int(board_id),
                    BoardLikes.user_id == user_id
                ])
            ).get_sql()

            cursor.execute(sql)
            connection.commit()
            connection.close()

            result = {'result': True}
            return json.dumps(result, ensure_ascii=False), 200
# endregion


# region 댓글
# 댓글 조회
@api.route('/board/<board_id>/comment', methods=['GET'])
def get_comment(board_id: int):
    connection = db_connection()
    cursor = get_dict_cursor(connection)
    endpoint = API_ROOT + url_for('api.get_comment', board_id=board_id)
    authentication = authenticate(request, cursor)

    if authentication is None:
        connection.close()
        result = {'result': False, 'error': '요청을 보낸 사용자는 알 수 없는 사용자입니다.'}
        return json.dumps(result, ensure_ascii=False), 401
    user_id = authentication['user_id']

    page_cursor = get_query_strings_from_request(request, 'cursor', INITIAL_ASCENDING_PAGE_CURSOR)
    limit = get_query_strings_from_request(request, 'limit', INITIAL_PAGE_LIMIT)
    page = get_query_strings_from_request(request, 'page', INITIAL_PAGE)

    sql = f"""
        WITH grouped_comment_cursor AS (
            SELECT
                bc.id,
                DATE_FORMAT(bc.created_at, '%Y/%m/%d %H:%i:%s') AS createdAt,
                bc.`group`,
                bc.depth,
                bc.comment,
                bc.user_id AS userId,
                CASE
                    WHEN bc.user_id in (SELECT target_id FROM blocks WHERE user_id = 64477) THEN 1
                    ELSE 0
                END AS isBlocked,
                u.nickname,
                u.profile_image AS profileImage,
                u.gender,
                CONCAT(LPAD(bc.group, 15, '0')) as `cursor`
            FROM
                board_comments bc
            INNER JOIN 
                users u ON u.id = bc.user_id
            WHERE bc.board_id = 2
            AND bc.deleted_at IS NULL
            AND bc.`group` > {page_cursor}
            GROUP BY bc.`group`
            ORDER BY bc.`group`, bc.depth, bc.created_at
            LIMIT {limit}
        )
        SELECT `cursor` FROM grouped_comment_cursor
    """
    cursor.execute(sql)
    grouped_comment_cursors = cursor.fetchall()

    last_cursor = grouped_comment_cursors[-1]['cursor'] if len(grouped_comment_cursors) > 0 else None

    grouped_comment_cursors = tuple([
        grouped_comment_cursors[i]['cursor']
        for i in range(0, len(grouped_comment_cursors))
    ])

    if len(grouped_comment_cursors) > 0:
        sql = f"""
            SELECT
                bc.id,
                DATE_FORMAT(bc.created_at, '%Y/%m/%d %H:%i:%s') AS createdAt,
                bc.`group`,
                bc.depth,
                bc.comment,
                bc.user_id AS userId,
                CASE
                    WHEN bc.user_id in (SELECT target_id FROM blocks WHERE user_id = {user_id}) THEN 1
                    ELSE 0
                END AS isBlocked,
                u.nickname,
                u.profile_image AS profileImage,
                u.gender,
                CONCAT(LPAD(bc.`group`, 15, '0')) as `cursor`
            FROM
                board_comments bc
            INNER JOIN
                    users u
                ON
                    u.id = bc.user_id
            WHERE
                bc.`group` 
                {'=' 
                if len(grouped_comment_cursors) == 1 
                else 
                'IN'} 
                {grouped_comment_cursors[0] 
                if len(grouped_comment_cursors) == 1 
                else 
                grouped_comment_cursors}
            AND
                bc.deleted_at IS NULL
            AND
                bc.board_id = {board_id}
            ORDER BY bc.`group`, bc.depth, bc.created_at
        """
        try:
            cursor.execute(sql)
        except Exception as e:
            return json.dumps({'sql': sql})
        board_comments = cursor.fetchall()
    else:
        board_comments = []

    sql = f"""
        SELECT
            COUNT(*) AS total_count
        FROM
            board_comments bc
        INNER JOIN
                users u
            ON
                u.id = bc.user_id
        WHERE bc.board_id = {board_id}
            AND bc.deleted_at IS NULL
        ORDER BY bc.`group`, bc.depth, bc.created_at
    """
    cursor.execute(sql)
    total_count = cursor.fetchone()['total_count']
    connection.close()

    # last_cursor = None if len(board_comments) <= 0 else board_comments[-1]['cursor']  # 배열 원소의 cursor string
    response = {
        'result': True,
        'data': board_comments,
        'cursor': last_cursor,
        'totalCount': total_count
    }
    return json.dumps(response, ensure_ascii=False), 200


# 댓글 작성
@api.route('/board/<board_id>/comment', methods=['POST'])
def post_comment(board_id: int):
    connection = db_connection()
    cursor = get_dict_cursor(connection)
    endpoint = API_ROOT + url_for('api.post_comment', board_id=board_id)
    authentication = authenticate(request, cursor)

    if authentication is None:
        connection.close()
        result = {'result': False, 'error': '요청을 보낸 사용자는 알 수 없는 사용자입니다.'}
        return json.dumps(result, ensure_ascii=False), 401
    user_id = authentication['user_id']

    sql = Query.from_(
        Boards
    ).select(
        Boards.id,
        Boards.user_id,
        Boards.deleted_at,
        Boards.is_show
    ).where(
        Boards.id == board_id
    ).get_sql()

    cursor.execute(sql)
    target_board = cursor.fetchone()

    if target_board is None:
        connection.close()
        result = {
            'result': False,
            'error': '해당 게시물은 존재하지 않습니다.'
        }
        return json.dumps(result, ensure_ascii=False), 400
    elif target_board['is_show'] == 0 and target_board['user_id'] != user_id:
        connection.close()
        result = {
            'result': False,
            'error': '올바른 시도가 아닙니다(숨겨진 게시물).'
        }
        return json.dumps(result, ensure_ascii=False), 400
    elif target_board['deleted_at'] is not None:
        connection.close()
        result = {
            'result': False,
            'error': '올바른 시도가 아닙니다(삭제된 게시물).'
        }
        return json.dumps(result, ensure_ascii=False), 400
    else:
        params = json.loads(request.get_data())

        if params['comment'] is None or params['comment'].strip() == '':
            connection.close()
            result = {
                'result': False,
                'error': '내용이 없어 댓글을 저장할 수 없습니다.'
            }
            return json.dumps(result, ensure_ascii=False), 400
        elif params['group'] is None:
            connection.close()
            result = {
                'result': False,
                'error': '누락된 필수 데이터가 있어 댓글을 입력할 수 없습니다(group).'
            }
            return json.dumps(result, ensure_ascii=False), 400
        else:
            comment_body = params['comment']
            comment_group = params['group']

            # 게시글의 댓글 group값 중 가장 큰 값 가져오기
            sql = Query.from_(
                BoardComments
            ).select(
                fn.Max(BoardComments.group).as_('max_group')
            ).where(Criterion.all([
                BoardComments.board_id == board_id,
                BoardComments.deleted_at.isnull()
            ])).get_sql()
            cursor.execute(sql)
            max_group = cursor.fetchone()['max_group']  # 현재 게시된 댓글 그룹 number 중 최대값

            if max_group is None:
                # 첫 댓글이 달릴 시에는 group, depth 모두 0으로 시작
                group = 1  # 0
                depth = 0
            else:
                group = comment_group if comment_group >= 1 else max_group + 1  # 새 댓글일 경우 else, 대댓글일 경우 comment_group의 값으로 들어감.
                depth = 0 if group >= max_group + 1 else 1  # comment_group 의 최초값이 -1 이라는 가정

            # 게시글의 댓글 저장
            sql = Query.into(
                BoardComments
            ).columns(
                BoardComments.board_id,
                BoardComments.user_id,
                BoardComments.group,
                BoardComments.depth,
                BoardComments.comment
            ).insert(
                board_id,
                user_id,
                group,
                depth,
                comment_body
            ).get_sql()

            cursor.execute(sql)
            connection.commit()
            board_comment_id = cursor.lastrowid  # 저장한 후 id값 기억해 두기

            # 방금 올린 답글의 원 댓글 작성자 확인
            sql = Query.from_(
                BoardComments
            ).select(
                BoardComments.id,
                BoardComments.user_id
            ).where(
                Criterion.all([
                    BoardComments.board_id == board_id,
                    BoardComments.group == group,
                    BoardComments.depth == 0,
                ])
            ).get_sql()
            cursor.execute(sql)
            target_comment_user = cursor.fetchone()
            target_comment_id = target_comment_user['id']
            target_comment_user_id = int(target_comment_user['user_id'])

            # 알림, 푸시
            sql = Query.from_(
                Users
            ).select(
                Users.nickname
            ).where(
                Users.id == user_id
            ).get_sql()
            cursor.execute(sql)
            user_nickname = cursor.fetchone()['nickname']

            if depth > 0 and target_comment_user_id != user_id:
                # 댓글에 답글을 남기는 경우 and 답글 작성자와 댓글 작성자가 다른 경우 => 댓글 작성자에게 알림
                # 게시글 작성자와 답글 작성자가 다르다면 => 게시글 작성자에게도 알림.
                # 단 본인의 댓글에 본인이 답글을 남기는 경우 알림 불필요
                create_notification(target_comment_user_id, 'board_reply', user_id, 'board', board_id, board_comment_id, json.dumps({"board_reply": comment_body}, ensure_ascii=False))
                push_type = f"board_reply.{str(board_id)}"
                push_target = list()
                push_target.append(target_comment_user_id)
                push_body = f'{user_nickname}님이 게시판의 내 댓글에 답글을 남겼습니다.\r\n\n\\"{comment_body}\\"'
                send_fcm_push(push_target, push_type, user_id, int(board_id), target_comment_id, BOARD_PUSH_TITLE, push_body)

                if target_board['user_id'] != user_id:
                    create_notification(int(target_board['user_id']), 'board_comment', user_id, 'board', board_id, board_comment_id, json.dumps({"board_comment": comment_body}, ensure_ascii=False))
                    push_type = f"board_comment.{str(board_comment_id)}"
                    push_target = list()
                    push_target.append(int(target_board['user_id']))
                    push_body = f'{user_nickname}님이 내 게시글에 댓글을 남겼습니다.\r\n\n\\"{comment_body}\\"'
                    send_fcm_push(push_target, push_type, user_id, int(board_id), target_comment_id, BOARD_PUSH_TITLE, push_body)
            elif depth > 0 and target_comment_user_id == user_id:
                # 댓글에 답글을 남기는 경우 and 답글 작성자와 댓글 작성자가 같은 경우 => 게시글 작성자에게 알림
                create_notification(int(target_board['user_id']), 'board_comment', user_id, 'board', board_id, board_comment_id, json.dumps({"board_comment": comment_body}, ensure_ascii=False))
                push_type = f"board_comment.{str(board_id)}"
                push_target = list()
                push_target.append(int(target_board['user_id']))
                push_body = f'{user_nickname}님이 내 게시글에 댓글을 남겼습니다.\r\n\n\\"{comment_body}\\"'
                send_fcm_push(push_target, push_type, user_id, int(board_id), target_comment_id, BOARD_PUSH_TITLE, push_body)
            elif depth <= 0 and target_board['user_id'] != user_id:
                # 게시글에 댓글을 남기는 경우 => 게시글 작성자에게 알림
                # 단 본인의 게시글에 본인이 댓글을 남기는 경우 알림 불필요
                create_notification(int(target_board['user_id']), 'board_comment', user_id, 'board', board_id, board_comment_id, json.dumps({"board_comment": comment_body}, ensure_ascii=False))
                push_type = f"board_comment.{str(board_id)}"
                push_target = list()
                push_target.append(int(target_board['user_id']))
                push_body = f'{user_nickname}님이 내 게시글에 댓글을 남겼습니다.\r\n\n\\"{comment_body}\\"'
                send_fcm_push(push_target, push_type, user_id, int(board_id), None, BOARD_PUSH_TITLE, push_body)
            else:
                # 자신의 게시글에 새 댓글을 남기는 경우 => 아무것도 하지 않음.
                pass

            connection.close()
            result = {'result': True}

            return json.dumps(result, ensure_ascii=False), 200


# 댓글 수정
@api.route('/board/<board_id>/comment/<comment_id>', methods=['PATCH'])
def update_comment(board_id: int, comment_id: int):
    connection = db_connection()
    cursor = get_dict_cursor(connection)
    endpoint = API_ROOT + url_for('api.update_comment', board_id=board_id, comment_id=comment_id)
    authentication = authenticate(request, cursor)

    if authentication is None:
        connection.close()
        result = {'result': False, 'error': '요청을 보낸 사용자는 알 수 없는 사용자입니다.'}
        return json.dumps(result, ensure_ascii=False), 401
    user_id = authentication['user_id']

    params = json.loads(request.get_data())
    if params['comment'] is None or params['comment'].strip() == '':
        connection.close()
        result = {
            'result': False,
            'error': '변경하고자 하는 내용이 서버로 전송되지 않았습니다.'
        }
        return json.dumps(result, ensure_ascii=False), 400

    sql = Query.from_(
        BoardComments
    ).select(
        BoardComments.id,
        BoardComments.user_id,
        BoardComments.deleted_at
    ).where(
        BoardComments.id == comment_id
    ).get_sql()
    cursor.execute(sql)
    target_comment = cursor.fetchone()

    if target_comment is None:
        connection.close()
        result = {
            "result": False,
            "error": "존재하지 않는 댓글이므로 수정할 수 없습니다."
        }
        return json.dumps(result, ensure_ascii=False), 400
    elif target_comment['user_id'] != user_id:
        connection.close()
        result = {
            "result": False,
            "error": "해당 댓글의 작성자가 아니므로 댓글을 수정할 수 없습니다."
        }
        return json.dumps(result, ensure_ascii=False), 401
    elif target_comment['deleted_at'] is not None:
        connection.close()
        result = {
            "result": False,
            "error": "삭제된 댓글은 수정할 수 없습니다."
        }
        return json.dumps(result, ensure_ascii=False), 400
    else:
        modified_comment = params['comment']
        sql = Query.update(
            BoardComments
        ).set(
            BoardComments.comment, modified_comment
        ).where(
            BoardComments.id == comment_id
        ).get_sql()

        cursor.execute(sql)
        connection.commit()
        connection.close()

        result = {'result': True}
        return json.dumps(result, ensure_ascii=False), 200


# 댓글 삭제
@api.route('/board/<board_id>/comment/<comment_id>', methods=['DELETE'])
def delete_comment(board_id: int, comment_id: int):
    connection = db_connection()
    cursor = get_dict_cursor(connection)
    endpoint = API_ROOT + url_for('api.delete_comment', board_id=board_id, comment_id=comment_id)
    authentication = authenticate(request, cursor)

    if authentication is None:
        connection.close()
        result = {'result': False, 'error': '요청을 보낸 사용자는 알 수 없는 사용자입니다.'}
        return json.dumps(result, ensure_ascii=False), 401
    user_id = authentication['user_id']

    sql = Query.from_(
        BoardComments
    ).select(
        BoardComments.id,
        BoardComments.user_id,
        BoardComments.deleted_at
    ).where(
        BoardComments.id == comment_id
    ).get_sql()
    cursor.execute(sql)
    target_comment = cursor.fetchone()

    if target_comment is None:
        connection.close()
        result = {
            "result": False,
            "error": "존재하지 않는 댓글이므로 삭제할 수 없습니다."
        }
        return json.dumps(result, ensure_ascii=False), 400
    elif target_comment['user_id'] != user_id:
        connection.close()
        result = {
            "result": False,
            "error": "해당 댓글의 작성자가 아니므로 댓글을 삭제할 수 없습니다."
        }
        return json.dumps(result, ensure_ascii=False), 401
    elif target_comment['deleted_at'] is not None:
        connection.close()
        result = {
            "result": False,
            "error": "이미 삭제된 댓글입니다."
        }
        return json.dumps(result, ensure_ascii=False), 400
    else:
        sql = Query.update(
            BoardComments
        ).set(
            BoardComments.deleted_at, fn.Now()
        ).where(
            BoardComments.id == comment_id
        ).get_sql()

        cursor.execute(sql)
        connection.commit()
        connection.close()

        result = {'result': True}
        return json.dumps(result, ensure_ascii=False), 200
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
        result = {'result': False, 'error': '요청을 보낸 사용자는 알 수 없는 사용자입니다.'}
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


# region cache test
# @cache.cached(timeout=50, key_prefix='cache_test')
@api.route('/cache')
def cache_test():
    cached_data = cache.get('random_addition')

    if cached_data is not None:
        result = {'result!!!!!!!!!': cached_data, 'cached_data': cached_data}
        return json.dumps(result, ensure_ascii=False)
    else:
        a = random.randrange(0, 1000)
        b = random.randrange(1001, 2000)
        cache.set('random_addition', a+b, 120)
        result = {'result': a + b, 'cached_data': cached_data}

        return json.dumps(result, ensure_ascii=False)
# endregion
