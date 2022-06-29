from global_configuration.table import Boards, Versions
from . import api
from global_configuration.constants import API_ROOT
from global_configuration.helper import db_connection, get_dict_cursor, authenticate, return_json, upload_single_image_to_s3
from flask import request, url_for
import json
import os
from pypika import MySQLQuery as Query, Criterion, functions as fn


@api.route('/board', methods=['GET'])
def board():
    connection = db_connection()
    cursor = get_dict_cursor(connection)
    endpoint = API_ROOT + url_for('api.food')

    sql =  Query.from_(
        Versions
    ).select(
        fn.Count(Versions.id).as_('total_count')
    ).get_sql()

    cursor.execute(sql)
    result = {'count: ', cursor.fetchall()}
    connection.close()

    return json.dumps(result, ensure_ascii=False), 200
