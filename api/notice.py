from api import api
from global_configuration.helper import db_connection, get_dict_cursor, authenticate, get_query_strings_from_request
from global_configuration.constants import API_ROOT, INITIAL_DESCENDING_PAGE_CURSOR, INITIAL_PAGE_LIMIT, INITIAL_PAGE
from flask import request, url_for
import json


@api.route('/notice/<notice_id>/comment', methods=['GET'])
def get_notice_comments(notice_id: int):
	connection = db_connection()
	cursor = get_dict_cursor(connection)
	endpoint = API_ROOT + url_for('api.get_boards', notice_id=notice_id)
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
		WITH grouped_comment_cursor AS (
			SELECT
				nc.id,
				DATE_FORMAT(nc.created_at, '%Y/%m/%d %H:%i:%s') AS createdAt,
				nc.`group`,
				nc.depth,
				nc.comment,
				nc.user_id AS userId,
				CASE
					WHEN
						nc.user_id IN (SELECT target_id FROM blocks WHERE user_id = {user_id}) 
					THEN 1
					ELSE 0
				END AS isBlocked,
				u.nickname,
				u.profile_image AS profile,
				u.gender,
				CONCAT(LPAD(nc.group, 15, '0')) as `cursor`
			FROM
				notice_comments nc
			INNER JOIN 
				users u ON u.id = nc.user_id
			WHERE nc.notice_id = {notice_id}
			AND nc.deleted_at IS NULL
			AND nc.`group` < {page_cursor}
			GROUP BY nc.`group`
			ORDER BY nc.`group` DESC, nc.depth, nc.created_at
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
				nc.id,
				DATE_FORMAT(nc.created_at, '%Y/%m/%d %H:%i:%s') AS createdAt,
				nc.`group`,
				nc.depth,
				nc.comment,
				nc.user_id AS userId,
				CASE
					WHEN 
						nc.user_id in (SELECT target_id FROM blocks WHERE user_id = {user_id}) 
					THEN 1
					ELSE 0
				END AS isBlocked,
				u.nickname,
				u.profile_image AS profile,
				u.gender,
				CONCAT(LPAD(nc.`group`, 15, '0')) as `cursor`
			FROM
				notice_comments nc
			INNER JOIN
				users u ON u.id = nc.user_id
			WHERE
			nc.`group` {'=' if len(grouped_comment_cursors) == 1 else 'IN'} {grouped_comment_cursors[0] if len(grouped_comment_cursors) == 1 else grouped_comment_cursors}
			AND nc.deleted_at IS NULL
			AND nc.notice_id = {notice_id}
			ORDER BY nc.`group` DESC, nc.depth, nc.created_at
		"""
		cursor.execute(sql)
		board_comments = cursor.fetchall()
	else:
		board_comments = []

	sql = f"""
		SELECT
			COUNT(*) AS total_count
		FROM
			notice_comments nc
		INNER JOIN users u ON u.id = nc.user_id
		WHERE nc.notice_id = {notice_id}
		AND nc.deleted_at IS NULL
		ORDER BY nc.`group`, nc.depth, nc.created_at
	"""
	cursor.execute(sql)
	total_count = cursor.fetchone()['total_count']
	connection.close()

	for comment in board_comments:
		comment['isBlocked'] = True if comment['isBlocked'] == 1 else False

	response = {
		'result': True,
		'data': board_comments,
		'cursor': last_cursor,
		'totalCount': total_count
	}
	return json.dumps(response, ensure_ascii=False), 200
