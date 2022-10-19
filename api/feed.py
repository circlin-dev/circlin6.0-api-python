from api import api
from global_configuration.helper import db_connection, get_dict_cursor, authenticate, get_query_strings_from_request
from global_configuration.constants import API_ROOT, INITIAL_DESCENDING_PAGE_CURSOR, INITIAL_PAGE_LIMIT, INITIAL_PAGE
from flask import request, url_for
import json


@api.route('/newsfeed', methods=['GET'])
def get_newsfeed():
	connection = db_connection()
	cursor = get_dict_cursor(connection)
	endpoint = API_ROOT + url_for('api.get_newsfeed')
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
		WITH followers AS (
			SELECT
				target_id AS follower_id
			FROM
				follows
			WHERE
				user_id = {user_id})
		SELECT
			f.id,
			DATE_FORMAT(f.created_at, '%Y/%m/%d %H:%i:%s') AS createdAt,
			f.content as body,
			(SELECT JSON_ARRAYAGG(
				JSON_OBJECT(
					'order', fi.order,
					'mimeType', fi.type,
					'pathname', fi.image,
					'resized', null
				)
			) FROM feed_images fi WHERE fi.feed_id = f.id) AS images,
			JSON_OBJECT(
				'id', u.id,
				'nickname', u.nickname,
				'profile', u.profile_image,
				'followed', CASE
								WHEN
									u.id in (SELECT target_id FROM follows WHERE user_id = {user_id})
								THEN 1
								ELSE 0
							END,
				'followers', (SELECT COUNT(*) FROM follows WHERE target_id = f.user_id),
				'isBlocked', CASE
								WHEN
									u.id in (SELECT target_id FROM blocks WHERE user_id = {user_id})
								THEN 1
								ELSE 0
								END,
				'isChatBlocked', IFNULL(
					(SELECT
						cu1.is_block
					FROM chat_users cu1,
						chat_users cu2
					WHERE cu1.chat_room_id = cu2.chat_room_id
					AND cu1.user_id = {user_id}
					AND cu2.user_id = u.id
					AND cu1.deleted_at IS NULL), 0),
				'gender', u.gender,
				'area', (SELECT a.name FROM areas a WHERE a.code = CONCAT(SUBSTRING(u.area_code, 1, 5), '00000') LIMIT 1)
			) AS user,
			(SELECT COUNT(*) FROM feed_comments WHERE feed_id = f.id AND deleted_at IS NULL) AS commentsCount,
			(SELECT COUNT(*) FROM feed_likes WHERE feed_id = f.id AND deleted_at IS NULL) AS checksCount,
			CASE
				WHEN
					(SELECT COUNT(*) FROM feed_likes WHERE feed_id = f.id AND user_id = {user_id} AND deleted_at IS NULL) > 0 
				THEN 1
				ELSE 0
			END AS checked,
			CONCAT(LPAD(f.id, 15, '0')) as `cursor`,
			JSON_ARRAYAGG(JSON_OBJECT(
				'id', m.id,
				'emoji', mc.emoji,
				'title', m.title,
				'isEvent', m.is_event,
				'isOldEvent', CASE
								WHEN
									m.id <= 1213 AND m.is_event = 1
								THEN 1
								ELSE 0
							END,
				'eventType', m.event_type,
				'startedAt', DATE_FORMAT(m.created_at, '%Y/%m/%d %H:%i:%s'),
				'endedAt', DATE_FORMAT(m.ended_at,  '%Y/%m/%d %H:%i:%s'),
				'thumbnail', m.thumbnail_image,
				'bookmarked', CASE
								WHEN
									(SELECT COUNT(*) FROM mission_stats WHERE mission_id = m.id AND user_id = {user_id} AND ended_at IS NULL) > 0
								THEN 1
								ELSE 0
							END
			)) AS missions,
			JSON_OBJECT(
				'type', fp.type,
				'id', fp.id,
				'brand', IF(fp.type = 'inside', b.name_ko, op.brand),
				'title', IF(fp.type = 'inside', p.name_ko, op.title),
				'image', IF(fp.type = 'inside', p.thumbnail_image, op.image),
				'url', IF(fp.type = 'inside', null, op.url),
				'price', IF(fp.type = 'inside', p.price, op.price)
			) AS product
		FROM
			feeds f
		INNER JOIN
			users u ON f.user_id = u.id
		INNER JOIN
			followers f3 ON f3.follower_id = u.id
		INNER JOIN
			feed_missions fm ON fm.feed_id = f.id
		INNER JOIN
			missions m ON fm.mission_id = m.id
		LEFT JOIN
			feed_products fp ON fp.feed_id = f.id
		LEFT JOIN
			products p ON fp.product_id = p.id
		LEFT JOIN
			brands b ON p.brand_id = b.id
		LEFT JOIN
			outside_products op ON fp.outside_product_id = op.id
		INNER JOIN
			mission_categories mc on m.mission_category_id = mc.id		
		WHERE ABS(TIMESTAMPDIFF(DAY, f.created_at, NOW())) <= 1
		AND f.deleted_at IS NULL
		AND f.is_hidden = 0
		AND f.id < {page_cursor}
		GROUP BY f.id
		ORDER BY f.id DESC
		LIMIT {limit}
	"""
	cursor.execute(sql)
	news_feeds = cursor.fetchall()

	sql = f"""
		WITH newsfeeds AS (
			WITH followers AS (
				SELECT 
					target_id AS follower_id
				FROM
					follows
				WHERE
					user_id = {user_id}
			)
			SELECT
				f.id,
				DATE_FORMAT(f.created_at, '%Y/%m/%d %H:%i:%s') AS createdAt,
				f.content as body,
				(SELECT JSON_ARRAYAGG(
					JSON_OBJECT(
						'order', fi.order,
						'mimeType', fi.type,
						'pathname', fi.image,
						'resized', null
					)
				) FROM feed_images fi WHERE fi.feed_id = f.id) AS images,
				JSON_OBJECT(
					'id', u.id,
					'nickname', u.nickname,
					'profile', u.profile_image,
					'followed', CASE
									WHEN
										u.id in (SELECT target_id FROM follows WHERE user_id = {user_id})
									THEN 1
									ELSE 0
								END,
					'followers', (SELECT COUNT(*) FROM follows WHERE target_id = f.user_id),
					'isBlocked', CASE
									WHEN
										u.id in (SELECT target_id FROM blocks WHERE user_id = {user_id})
									THEN 1
									ELSE 0
									END,
					'isChatBlocked', IFNULL(
						(SELECT
							cu1.is_block
						FROM chat_users cu1,
							chat_users cu2
						WHERE cu1.chat_room_id = cu2.chat_room_id
						AND cu1.user_id = {user_id}
						AND cu2.user_id = u.id
						AND cu1.deleted_at IS NULL), 0),
					'gender', u.gender,
					'area', (SELECT a.name FROM areas a WHERE a.code = CONCAT(SUBSTRING(u.area_code, 1, 5), '00000') LIMIT 1)
				) AS user,
				(SELECT COUNT(*) FROM feed_comments WHERE feed_id = f.id AND deleted_at IS NULL) AS commentsCount,
				(SELECT COUNT(*) FROM feed_likes WHERE feed_id = f.id AND deleted_at IS NULL) AS checksCount,
				CASE
					WHEN
						(SELECT COUNT(*) FROM feed_likes WHERE feed_id = f.id AND user_id = {user_id} AND deleted_at IS NULL) > 0 
					THEN 1
					ELSE 0
				END AS checked,
				JSON_ARRAYAGG(JSON_OBJECT(
					'id', m.id,
					'emoji', mc.emoji,
					'title', m.title,
					'isEvent', m.is_event,
					'isOldEvent', CASE
									WHEN
										m.id <= 1213 AND m.is_event = 1
									THEN 1
									ELSE 0
								END,
					'eventType', m.event_type,
					'startedAt', DATE_FORMAT(m.created_at, '%Y/%m/%d %H:%i:%s'),
					'endedAt', DATE_FORMAT(m.ended_at,  '%Y/%m/%d %H:%i:%s'),
					'thumbnail', m.thumbnail_image,
					'bookmarked', CASE
									WHEN
										(SELECT COUNT(*) FROM mission_stats WHERE mission_id = m.id AND user_id = {user_id} AND ended_at IS NULL) > 0
									THEN 1
									ELSE 0
								END
				)) AS missions,
				JSON_OBJECT(
					'type', fp.type,
					'id', fp.id,
					'brand', IF(fp.type = 'inside', b.name_ko, op.brand),
					'title', IF(fp.type = 'inside', p.name_ko, op.title),
					'image', IF(fp.type = 'inside', p.thumbnail_image, op.image),
					'url', IF(fp.type = 'inside', null, op.url),
					'price', IF(fp.type = 'inside', p.price, op.price)
				) AS product
			FROM
				feeds f
			INNER JOIN
				users u ON f.user_id = u.id
			INNER JOIN
				followers f3 ON f3.follower_id = u.id
			INNER JOIN
				feed_missions fm ON fm.feed_id = f.id
			INNER JOIN
				missions m ON fm.mission_id = m.id
			LEFT JOIN
				feed_products fp ON fp.feed_id = f.id
			LEFT JOIN
				products p ON fp.product_id = p.id
			LEFT JOIN
				brands b ON p.brand_id = b.id
			LEFT JOIN
				outside_products op ON fp.outside_product_id = op.id
			INNER JOIN
				mission_categories mc on m.mission_category_id = mc.id		
			WHERE ABS(TIMESTAMPDIFF(DAY, f.created_at, NOW())) <= 1
			AND f.deleted_at IS NULL
			AND f.is_hidden = 0
			GROUP BY f.id
			ORDER BY f.id DESC
		) SELECT COUNT(*) AS total_count FROM newsfeeds
	"""
	cursor.execute(sql)
	total_count = cursor.fetchone()['total_count']
	connection.close()

	last_cursor = None if len(news_feeds) == 0 else news_feeds[-1]['cursor']
	news_feeds = [  # using list comprehension, for better performance than for loop.
		{
			'id': feed['id'],
			'createdAt': feed['createdAt'],
			'body': feed['body'],
			'images': json.loads(feed['images']),
			'user': {
				'id': json.loads(feed['user'])['id'],
				'area': json.loads(feed['user'])['area'],
				'gender': json.loads(feed['user'])['gender'],
				'profile': json.loads(feed['user'])['profile'],
				'followed': True if json.loads(feed['user'])['followed'] == 1 else False,
				'nickname': json.loads(feed['user'])['nickname'],
				'followers': json.loads(feed['user'])['followers'],
				'isBlocked': True if json.loads(feed['user'])['isBlocked'] == 1 else False,
				'isChatBlocked': True if json.loads(feed['user'])['isChatBlocked'] == 1 else False
			},
			'commentsCount': feed['commentsCount'],
			'checksCount': feed['checksCount'],
			'checked': True if feed['checked'] == 1 else False,
			'missions': [{
				'id': mission['id'],
				'emoji': mission['emoji'],
				'title': mission['title'],
				'endedAt': mission['endedAt'],
				'isEvent': True if mission['isEvent'] == 1 else False,
				'eventType': mission['eventType'],
				'startedAt': mission['startedAt'],
				'thumbnail': mission['thumbnail'],
				'bookmarked': True if mission['bookmarked'] == 1 else False,
				'isOldEvent': True if mission['isOldEvent'] == 1 else False,
			} for mission in json.loads(feed['missions'])],
			'product': {
				'id': json.loads(feed['product'])['id'],
				'type': json.loads(feed['product'])['type'],
				'brand': json.loads(feed['product'])['brand'],
				'title': json.loads(feed['product'])['title'],
				'image': json.loads(feed['product'])['image'],
				'url': json.loads(feed['product'])['url'],
				'price': json.loads(feed['product'])['price'],
			}
		} for feed in news_feeds
	]

	response = {
		'result': True,
		'data': news_feeds,
		'cursor': last_cursor,
		'totalCount': total_count
	}

	return json.dumps(response, ensure_ascii=False), 200


@api.route('/feed/<feed_id>/comment', methods=['GET'])
def get_feed_comments(feed_id: int):
	connection = db_connection()
	cursor = get_dict_cursor(connection)
	endpoint = API_ROOT + url_for('api.get_boards', feed_id=feed_id)
	authentication = authenticate(request, cursor)

	if authentication is None:
		connection.close()
		result = {'result': False, 'error': '요청을 보낸 사용자는 알 수 없는 사용자입니다.'}
		return json.dumps(result, ensure_ascii=False), 401
	user_id = authentication['user_id']

	if feed_id is None:
		connection.close()
		result = {'result': False, 'error': '필수 데이터가 누락된 요청을 처리할 수 없습니다(feed_id).'}
		return json.dumps(result, ensure_ascii=False), 400

	page_cursor = get_query_strings_from_request(request, 'cursor', INITIAL_DESCENDING_PAGE_CURSOR)
	limit = get_query_strings_from_request(request, 'limit', INITIAL_PAGE_LIMIT)
	page = get_query_strings_from_request(request, 'page', INITIAL_PAGE)

	sql = f"""
		WITH grouped_comment_cursor AS (
			SELECT
				fc.id,
				DATE_FORMAT(fc.created_at, '%Y/%m/%d %H:%i:%s') AS createdAt,
				fc.`group`,
				fc.depth,
				fc.comment,
				fc.user_id AS userId,
				CASE
					WHEN
						fc.user_id IN (SELECT target_id FROM blocks WHERE user_id = {user_id}) 
					THEN 1
					ELSE 0
				END AS isBlocked,
				u.nickname,
				u.profile_image AS profile,
				u.gender,
				CONCAT(LPAD(fc.group, 15, '0')) as `cursor`
			FROM
				feed_comments fc
			INNER JOIN 
				users u ON u.id = fc.user_id
			WHERE fc.feed_id = {feed_id}
			AND fc.deleted_at IS NULL
			AND fc.`group` < {page_cursor}
			GROUP BY fc.`group`
			ORDER BY fc.`group` DESC, fc.depth, fc.created_at
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
				fc.id,
				DATE_FORMAT(fc.created_at, '%Y/%m/%d %H:%i:%s') AS createdAt,
				fc.`group`,
				fc.depth,
				fc.comment,
				fc.user_id AS userId,
				CASE
					WHEN 
						fc.user_id in (SELECT target_id FROM blocks WHERE user_id = {user_id}) 
					THEN 1
					ELSE 0
				END AS isBlocked,
				u.nickname,
				u.profile_image AS profile,
				u.gender,
				CONCAT(LPAD(fc.`group`, 15, '0')) as `cursor`
			FROM
				feed_comments fc
			INNER JOIN
				users u ON u.id = fc.user_id
			WHERE
			fc.`group` {'=' if len(grouped_comment_cursors) == 1 else 'IN'} {grouped_comment_cursors[0] if len(grouped_comment_cursors) == 1 else grouped_comment_cursors}
			AND fc.deleted_at IS NULL
			AND fc.feed_id = {feed_id}
			ORDER BY fc.`group` DESC, fc.depth, fc.created_at
		"""
		cursor.execute(sql)
		board_comments = cursor.fetchall()
	else:
		board_comments = []

	sql = f"""
		SELECT
			COUNT(*) AS total_count
		FROM
			feed_comments fc
		INNER JOIN users u ON u.id = fc.user_id
		WHERE fc.feed_id = {feed_id}
		AND fc.deleted_at IS NULL
		ORDER BY fc.`group`, fc.depth, fc.created_at
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
