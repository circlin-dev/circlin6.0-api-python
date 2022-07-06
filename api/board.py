from global_configuration.table import Boards, Files, BoardCategories, BoardFiles, BoardLikes, BoardComments
from . import api
from global_configuration.constants import API_ROOT, INITIAL_DESCENDING_PAGE_CURSOR, INITIAL_ASCENDING_PAGE_CURSOR, \
    INITIAL_PAGE_LIMIT, INITIAL_PAGE
from global_configuration.helper import db_connection, get_dict_cursor, authenticate, upload_single_file_to_s3, \
    get_query_strings_from_request
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
            (SELECT COUNT(*) FROM board_likes bl WHERE bl.board_id = b.id) AS likeCount,
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
                (SELECT COUNT(*) FROM board_likes bl WHERE bl.board_id = b.id) AS likeCount,
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
        board['images'] = json.loads(board['images'])

    if len(boards) == 0:  # 좋아요 누른 사람이 없을 경우 return
        result = []
        response = {
            'data': result,
            'next': None,
            'total_count': total_count
        }
        return json.dumps(response, ensure_ascii=False), 200

    last_cursor = boards[-1]['cursor']  # 배열 원소의 cursor string
    response = {
        'data': boards,
        'next': last_cursor,
        'total_count': total_count
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
                                WHEN {user_id} in (SELECT COUNT(*) FROM follows WHERE user_id = b.user_id) THEN 1
                                ELSE 0
                            END,
                'followers', (SELECT COUNT(*) FROM follows WHERE target_id = b.user_id)
            ) AS user,
            DATE_FORMAT(b.created_at, '%Y/%m/%d %H:%i:%s') AS createdAt,
            (SELECT COUNT(*) FROM board_likes bl WHERE bl.board_id = b.id) AS likeCount,
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
        AND b.id = {board_id}
        GROUP BY b.id
    """

    cursor.execute(sql)
    board = cursor.fetchone()
    connection.close()

    if board is not None:
        board['user'] = json.loads(board['user'])
        board['user']['followed'] = True if board['user']['followed'] == 1 or board['user']['id'] == user_id else False
        board['images'] = json.loads(board['images'])
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

    sql = f"""
        WITH follower_recent_board AS (
            SELECT
                f.target_id,
                JSON_OBJECT('id', b.id, 'body', b.body) AS board_data,
                RANK() OVER (PARTITION BY f.target_id ORDER BY b.created_at DESC) AS ranking
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

    if len(liked_users) == 0:  # 좋아요 누른 사람이 없을 경우 return
        connection.close()
        result = []
        response = {
            'data': result,
            'next': None,
            'total_count': len(result)
        }
        return json.dumps(response, ensure_ascii=False), 200

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

    last_cursor = liked_users[-1]['cursor']  # 배열 원소의 cursor string

    response = {
        'data': liked_users,
        'next': last_cursor,
        'total_count': total_count
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


# region 댓글
# 댓글 조회
@api.route('/board/<board_id>/comment', methods=['GET'])
def get_commet(board_id: int):
    connection = db_connection()
    cursor = get_dict_cursor(connection)
    endpoint = API_ROOT + url_for('api.post_comment', board_id=board_id)
    authentication = authenticate(request, cursor)

    if authentication is None:
        connection.close()
        result = {'result': False, 'error': '요청을 보낸 사용자는 알 수 없는 사용자입니다.'}
        return json.dumps(result, ensure_ascii=False), 401
    user_id = authentication['user_id']

    sql = f"""
        WITH comment_list AS (
            SELECT
                bc.id,
                bc.created_at,
                bc.`group`,
                bc.depth,
                bc.comment,
                CASE
                    WHEN bc.deleted_at IS NULL THEN 0
                    ELSE 1
                END AS is_delete,
                bc.user_id,
                CASE
                    WHEN bc.user_id in (SELECT target_id FROM blocks WHERE user_id = {user_id}) THEN 1
                    ELSE 0
                END AS is_blocked,
                u.nickname,
                u.profile_image,
                u.gender
            FROM
                board_comments bc
            INNER JOIN
                    users u
                ON
                    u.id = bc.user_id
            WHERE
                bc.board_id = {board_id}
            ORDER BY bc.`group` DESC, bc.depth, bc.created_at)
        SELECT COUNT(*) AS total_count FROM comment_list;"""

    cursor.execute(sql)
    total = cursor.fetchone()['total_count']

    if total == 0:
        connection.close()
        result = {
            'result': True,
            'data': {
                'total': total,
                'comments': []
            }
        }
        return json.dumps(result, ensure_ascii=False), 200
    else:
        sql = f"""
            SELECT
                bc.id,
                DATE_FORMAT(bc.created_at, '%Y/%m/%d %H:%i:%s') as created_at,
                bc.`group`,
                bc.depth,
                bc.comment,
                CASE
                    WHEN bc.deleted_at IS NULL THEN 0
                    ELSE 1
                END AS is_delete,
                bc.user_id,
                CASE
                    WHEN bc.user_id in (SELECT target_id FROM blocks WHERE user_id = {user_id}) THEN 1
                    ELSE 0
                END AS is_blocked,
                u.nickname,
                u.profile_image,
                u.gender
            FROM
                board_comments bc
            INNER JOIN
                    users u
                ON
                    u.id = bc.user_id
            WHERE
                bc.board_id = {board_id}
            ORDER BY bc.`group` DESC, bc.depth, bc.created_at"""

        cursor.execute(sql)
        comments = cursor.fetchall()
        connection.close()
        result = {
            'result': True,
            'data': {
                'total': total,
                'comments': comments
            }
        }
        return json.dumps(result, ensure_ascii=False), 200


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
        Boards.id
    ).where(
        Boards.id == board_id
    ).get_sql()

    cursor.execute(sql)
    is_exists = cursor.fetchone()

    if is_exists is None:
        connection.close()
        result = {
            'result': False,
            'error': '해당 게시물은 존재하지 않습니다.'
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
            pass

        comment_body = params['comment']
        comment_group = params['group']

        sql = Query.from_(
            BoardComments
        ).select(
            fn.Max(BoardComments.group).as_('max_group')
        ).where(
            BoardComments.board_id == board_id
        ).get_sql()
        cursor.execute(sql)
        max_group = cursor.fetchone()['max_group']  # 현재 게시된 댓글 그룹 number 중 최대값

        if max_group is None:
            group = 0
            depth = 0
        else:
            group = comment_group if comment_group >= 0 else max_group + 1  # 새 댓글일 경우 else, 대댓글일 경우 target group의 값으로 들어감.
            depth = 0 if group >= max_group + 1 else 1  # comment_group 의 최초값이 -1 이라는 가정

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
    current_comment = cursor.fetchone()

    if current_comment is None:
        connection.close()
        result = {
            "result": False,
            "error": "존재하지 않는 댓글이므로 수정할 수 없습니다."
        }
        return json.dumps(result, ensure_ascii=False), 400
    elif current_comment['user_id'] != user_id:
        connection.close()
        result = {
            "result": False,
            "error": "해당 댓글의 작성자가 아니므로 댓글을 수정할 수 없습니다."
        }
        return json.dumps(result, ensure_ascii=False), 401
    elif current_comment['deleted_at'] is not None:
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
    comment = cursor.fetchone()

    if comment is None:
        connection.close()
        result = {
            "result": False,
            "error": "존재하지 않는 댓글이므로 삭제할 수 없습니다."
        }
        return json.dumps(result, ensure_ascii=False), 400
    elif comment['user_id'] != user_id:
        connection.close()
        result = {
            "result": False,
            "error": "해당 댓글의 작성자가 아니므로 댓글을 삭제할 수 없습니다."
        }
        return json.dumps(result, ensure_ascii=False), 401
    elif comment['deleted_at'] is not None:
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
