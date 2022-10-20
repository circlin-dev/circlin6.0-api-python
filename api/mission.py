from api import api
from global_configuration.helper import db_connection, get_dict_cursor, authenticate, get_query_strings_from_request
from global_configuration.constants import API_ROOT, INITIAL_DESCENDING_PAGE_CURSOR, INITIAL_PAGE_LIMIT, INITIAL_PAGE
from flask import request, url_for
import json


@api.route('/mission/<mission_id>/comment', methods=['GET'])
def get_mission_comments(mission_id: int):
	connection = db_connection()
	cursor = get_dict_cursor(connection)
	endpoint = API_ROOT + url_for('api.get_mission_comments', mission_id=mission_id)
	authentication = authenticate(request, cursor)

	if authentication is None:
		connection.close()
		result = {'result': False, 'error': '요청을 보낸 사용자는 알 수 없는 사용자입니다.'}
		return json.dumps(result, ensure_ascii=False), 401
	user_id = authentication['user_id']

	if mission_id is None:
		connection.close()
		result = {'result': False, 'error': '필수 데이터가 누락된 요청을 처리할 수 없습니다(mission_id).'}
		return json.dumps(result, ensure_ascii=False), 400

	page_cursor = get_query_strings_from_request(request, 'cursor', INITIAL_DESCENDING_PAGE_CURSOR)
	limit = get_query_strings_from_request(request, 'limit', INITIAL_PAGE_LIMIT)
	page = get_query_strings_from_request(request, 'page', INITIAL_PAGE)

	sql = f"""
		WITH grouped_comment_cursor AS (
			SELECT
				mc.id,
				DATE_FORMAT(mc.created_at, '%Y/%m/%d %H:%i:%s') AS createdAt,
				mc.`group`,
				mc.depth,
				mc.comment,
				mc.user_id AS userId,
				CASE
					WHEN
						mc.user_id IN (SELECT target_id FROM blocks WHERE user_id = {user_id}) 
					THEN 1
					ELSE 0
				END AS isBlocked,
				u.nickname,
				u.profile_image AS profile,
				u.gender,
				CONCAT(LPAD(mc.group, 15, '0')) as `cursor`
			FROM
				mission_comments mc
			INNER JOIN 
				users u ON u.id = mc.user_id
			WHERE mc.mission_id = {mission_id}
			AND mc.deleted_at IS NULL
			AND mc.`group` < {page_cursor}
			GROUP BY mc.`group`
			ORDER BY mc.`group` DESC, mc.depth, mc.created_at
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
				mc.id,
				DATE_FORMAT(mc.created_at, '%Y/%m/%d %H:%i:%s') AS createdAt,
				mc.`group`,
				mc.depth,
				mc.comment,
				mc.user_id AS userId,
				CASE
					WHEN 
						mc.user_id in (SELECT target_id FROM blocks WHERE user_id = {user_id}) 
					THEN 1
					ELSE 0
				END AS isBlocked,
				u.nickname,
				u.profile_image AS profile,
				u.gender,
				CONCAT(LPAD(mc.`group`, 15, '0')) as `cursor`
			FROM
				mission_comments mc
			INNER JOIN
				users u ON u.id = mc.user_id
			WHERE
			mc.`group` {'=' if len(grouped_comment_cursors) == 1 else 'IN'} {grouped_comment_cursors[0] if len(grouped_comment_cursors) == 1 else grouped_comment_cursors}
			AND mc.deleted_at IS NULL
			AND mc.mission_id = {mission_id}
			ORDER BY mc.`group` DESC, mc.depth, mc.created_at
		"""
		cursor.execute(sql)
		mission_comments = cursor.fetchall()
	else:
		mission_comments = []

	sql = f"""
		SELECT
			COUNT(*) AS total_count
		FROM
			mission_comments mc
		INNER JOIN users u ON u.id = mc.user_id
		WHERE mc.mission_id = {mission_id}
		AND mc.deleted_at IS NULL
		ORDER BY mc.`group`, mc.depth, mc.created_at
	"""
	cursor.execute(sql)
	total_count = cursor.fetchone()['total_count']
	connection.close()

	mission_comments = [
		{
			'id': comment['id'],
			"createdAt": comment['createdAt'],
			"group": comment['group'],
			"depth": comment['depth'],
			"comment": comment['comment'],
			"userId": comment['userId'],
			"isBlocked": True if comment['isBlocked'] == 1 else False,
			"nickname": comment['nickname'],
			"profile": comment['profile'],
			"gender": comment['gender'],
			"cursor": comment['cursor'],
		} for comment in mission_comments
	]

	response = {
		'result': True,
		'data': mission_comments,
		'cursor': last_cursor,
		'totalCount': total_count
	}
	return json.dumps(response, ensure_ascii=False), 200
