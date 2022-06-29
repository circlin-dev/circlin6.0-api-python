from global_configuration.table import Boards, Files
from . import api
from global_configuration.constants import API_ROOT
from global_configuration.helper import db_connection, get_dict_cursor, authenticate, return_json, upload_single_image_to_s3
from flask import request, url_for
import json
import os
from pypika import MySQLQuery as Query, Criterion, functions as fn


# region 게시물
# 전체 조회, 등록
@api.route('/board', methods=['GET'])
def get_boards():
    connection = db_connection()
    cursor = get_dict_cursor(connection)
    endpoint = API_ROOT + url_for('api.board')

    # result = {}
    # return json.dumps(result, ensure_ascii=False), 200
    return 'GET_boards', 200


@api.route('/board', methods=['POST'])
def get_boards():
    connection = db_connection()
    cursor = get_dict_cursor(connection)
    endpoint = API_ROOT + url_for('api.board')
    return 'POST_board', 200
    # result = {}
    # return json.dumps(result, ensure_ascii=False), 200



# 단건 조회(상세 조회)
@api.rotue('/board/<board_id>', methos=['GET'])
def get_a_board():
    return 'GET_board', 200


# 팔로워가 쓴 최신 글 조회


# 게시글 수정
@api.rotue('/board/<board_id>', methos=['PATCH'])
def update_a_board():
    return 'PATCH_board', 200


# 게시글 삭제
@api.rotue('/board/<board_id>', methos=['DELETE'])
def update_a_board():
    return 'DELETE_board', 200
# endregion


# region 좋아요

# endregion


# region 댓글 남기기
# 댓글 조회

# 댓글 작성

# 댓글 삭제

# endregion


# region 좋아요
# 좋아요 누른 사람 리스트

# endregion


# region 카테고리
# 카테고리 조회
@api.rotue('/board/category', methos=['GET'])
def get_board_categories():
    return 'GET_categories', 200

# endregion
