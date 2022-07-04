from global_configuration.table import Boards, Files, BoardCategories, BoardFiles, BoardLikes
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
--                     'resized', IFNULL(JSON_ARRAY(JSON_OBJECT('mimeType', ff.mime_type,
--                                             'pathname', ff.pathname,
--                                             'width', ff.width)), JSON_ARRAY())
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
            COUNT(bl.id) AS likeCount,
            COUNT(bcm.id) AS commentsCount,
            CASE
                WHEN {user_id} in (bl.user_id) THEN 1
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
        LEFT JOIN
                board_comments bcm
            ON
                b.id = bcm.board_id
        LEFT JOIN
                board_likes bl
            ON
                b.id = bl.board_id
        INNER JOIN
                users u
            ON
                u.id = b.user_id
        WHERE b.deleted_at IS NULL
        AND b.is_show = 1
        AND b.id < '90000000000000'
        GROUP BY b.id
    """

    cursor.execute(sql)
    boards = cursor.fetchall()
    connection.close()

    for board in boards:
        board['user'] = json.loads(board['user'])
        board['images'] = json.loads(board['images'])

    result = {
        'result': True,
        'data': boards
    }
    return json.dumps(result, ensure_ascii=False), 200


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
                                WHEN {user_id} in (SELECT COUNT(*) FROM follows WHERE user_id = b.user_id) THEN 1
                                ELSE 0
                            END,
                'followers', (SELECT COUNT(*) FROM follows WHERE target_id = b.user_id)
            ) AS user,
            DATE_FORMAT(b.created_at, '%Y/%m/%d %H:%i:%s') AS createdAt,
            COUNT(bl.id) AS likeCount,
            COUNT(bcm.id) AS commentsCount,
            CASE
                WHEN {user_id} in (bl.user_id) THEN 1
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
        LEFT JOIN
                board_comments bcm
            ON
                b.id = bcm.board_id
        LEFT JOIN
                board_likes bl
            ON
                b.id = bl.board_id
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
    board = cursor.fetchall()

    board['user'] = json.loads(board['user'])
    board['images'] = json.loads(board['images'])

    result = {
        'result': True,
        'data': board
    }
    return json.dumps(result, ensure_ascii=False), 200


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

    sql = f"""
        WITH follower_recent_board AS (
            SELECT
                f.target_id,
                JSON_OBJECT('id', b.id, 'body', b.body) AS board_data,
                RANK() OVER (PARTITION BY f.target_id ORDER BY b.id DESC) AS ranking
            FROM
                boards b
            INNER JOIN
                    follows f ON b.user_id = f.target_id
            WHERE
                f.user_id = {user_id}
            AND
                ABS(TIMESTAMPDIFF(DAY, b.created_at, NOW())) < 7
            AND b.is_show = 1
        )
        SELECT
            frb.target_id,
            frb.board_data
        FROM
            follower_recent_board frb
        WHERE frb.ranking < 2
    """

    cursor.execute(sql)
    follower_recent_board = cursor.fetchall()
    for data in follower_recent_board:
        data['board_data'] = json.loads(data['board_data'])
    connection.close()

    result = {
        'result': True,
        'data': follower_recent_board
    }
    return json.dumps(result, ensure_ascii=False), 200


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
    return 'PATCH_board', 200


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
        result = {'result': False, 'error': '존재하지 않는 게시물이거나, 이미 삭제된 게시물입니다.'}
        return json.dumps(result, ensure_ascii=False), 400
    elif data['user_id'] == user_id:
        connection.close()
        result = {'result': False, 'error': '해당 유저는 이 게시글에 대한 삭제 권한이 없습니다.'}
        return json.dumps(result, ensure_ascii=False), 403
    elif data['deleted_at'] is not None:
        connection.close()
        result = {'result': False, 'error': '이미 삭제된 게시물입니다.'}
        return json.dumps(result, ensure_ascii=False), 400
    else:
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
    is_exists = cursor.fetchone()

    if is_exists is None:
        connection.close()
        result = {
            'result': False,
            'error': '올바른 시도가 아닙니다(존재하지 않는 게시물).'
        }
        return json.dumps(result, ensure_ascii=False), 400
    elif is_exists['deleted_at'] is not None:
        connection.close()
        result = {
            'result': False,
            'error': '올바른 시도가 아닙니다(삭제된 게시물).'
        }
        return json.dumps(result, ensure_ascii=False), 400
    elif is_exists['is_show'] == 0 and is_exists['user_id'] != user_id:
        connection.close()
        result = {
            'result': False,
            'error': '올바른 시도가 아닙니다(숨겨진 게시물).'
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
    is_exists = cursor.fetchone()

    if is_exists is None:
        connection.close()
        result = {
            'result': False,
            'error': '올바른 시도가 아닙니다(존재하지 않는 게시물).'
        }
        return json.dumps(result, ensure_ascii=False), 400
    elif is_exists['deleted_at'] is not None:
        connection.close()
        result = {
            'result': False,
            'error': '올바른 시도가 아닙니다(삭제된 게시물).'
        }
        return json.dumps(result, ensure_ascii=False), 400
    elif is_exists['is_show'] == 0 and is_exists['user_id'] != user_id:
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
