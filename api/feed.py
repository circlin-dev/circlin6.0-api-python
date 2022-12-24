from . import api
from adapter.database import db_session
from adapter.orm import feed_mappers, feed_check_mappers, feed_comment_mappers, point_history_mappers
from adapter.repository.feed import FeedRepository
from adapter.repository.feed_like import FeedCheckRepository
from adapter.repository.feed_comment import FeedCommentRepository
from adapter.repository.mission_stat import MissionStatRepository
from adapter.repository.notification import NotificationRepository
from adapter.repository.point_history import PointHistoryRepository
from adapter.repository.push import PushHistoryRepository
from adapter.repository.user import UserRepository
from domain.feed import Feed, FeedCheck, FeedComment
from helper.constant import ERROR_RESPONSE, INITIAL_ASCENDING_PAGE_CURSOR, INITIAL_DESCENDING_PAGE_CURSOR, INITIAL_PAGE, INITIAL_PAGE_LIMIT
from helper.function import authenticate, failed_response, get_query_strings_from_request
from services import feed_service, point_service

from flask import request
import json
from sqlalchemy.orm import clear_mappers


@api.route('/feed/<int:feed_id>', methods=['GET', 'PATCH', 'DELETE'])
def feed(feed_id: int):
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        return json.dumps(failed_response(ERROR_RESPONSE[401]), ensure_ascii=False), 401

    if feed_id is None:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[400]} (feed_id).'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 400

    if request.method == 'GET':
        feed_mappers()
        feed_repo: FeedRepository = FeedRepository(db_session)
        mission_stat_repo: MissionStatRepository = MissionStatRepository(db_session)
        data: dict = feed_service.get_a_feed(feed_id, user_id, feed_repo, mission_stat_repo)
        clear_mappers()
        db_session.close()

        if data['result']:
            return json.dumps(data, ensure_ascii=False), 200
        else:
            return json.dumps({key: value for key, value in data.items() if key != 'status_code'}, ensure_ascii=False), data['status_code']

    elif request.method == 'PATCH':
        data: dict = json.loads(request.get_data())

        if 'body' not in data.keys() or data['body'].strip() == '':
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (body).'
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        elif 'isHidden' not in data.keys():
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (isHidden).'
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        else:
            new_body: [str, None] = data['body']
            new_is_hidden: [int, None] = int(data['isHidden'])
            feed_mappers()
            feed_repo: FeedRepository = FeedRepository(db_session)
            new_feed = Feed(
                id=feed_id,
                user_id=user_id,
                content=new_body,
                is_hidden=True if new_is_hidden == 1 else False,
                deleted_at=None,
                distance=None,
                distance_origin=None,
                laptime=None,
                laptime_origin=None
            )
            update_feed: dict = feed_service.update_feed(new_feed, user_id, feed_repo)
            clear_mappers()

            if update_feed['result']:
                db_session.commit()
                db_session.close()
                return json.dumps(update_feed, ensure_ascii=False), 200
            else:
                db_session.close()
                return json.dumps({key: value for key, value in update_feed.items() if key != 'status_code'}, ensure_ascii=False), update_feed['status_code']
    elif request.method == 'DELETE':
        feed_mappers()
        feed_repo: FeedRepository = FeedRepository(db_session)
        target_feed = Feed(
            id=feed_id,
            user_id=user_id,
            content='',
            is_hidden=None,
            deleted_at=None,
            distance=None,
            distance_origin=None,
            laptime=None,
            laptime_origin=None
        )
        delete_feed: dict = feed_service.delete_feed(target_feed, user_id, feed_repo)
        clear_mappers()

        if delete_feed['result']:
            db_session.commit()
            db_session.close()
            return json.dumps(delete_feed, ensure_ascii=False), 200
        else:
            db_session.close()
            return json.dumps({key: value for key, value in delete_feed.items() if key != 'status_code'}, ensure_ascii=False), delete_feed['status_code']
    else:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[405]} ({request.method})'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 405


@api.route('/feed', methods=['POST'])
def post_a_feed():
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        return json.dumps(failed_response(ERROR_RESPONSE[401]), ensure_ascii=False), 401

    if request.method == 'POST':
        pass
    else:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[405]} ({request.method})'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 405


@api.route('/feed/<int:feed_id>/comment', methods=['GET', 'POST'])
def feed_comment(feed_id: int):
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        return json.dumps(failed_response(ERROR_RESPONSE[401]), ensure_ascii=False), 401

    if feed_id is None:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[400]} (feed_id).'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 400

    if request.method == 'GET':
        page_cursor: int = get_query_strings_from_request(request, 'cursor', INITIAL_DESCENDING_PAGE_CURSOR)
        limit: int = get_query_strings_from_request(request, 'limit', INITIAL_PAGE_LIMIT)
        page: int = get_query_strings_from_request(request, 'page', INITIAL_PAGE)

        feed_comment_mappers()
        feed_comment_repo: FeedCommentRepository = FeedCommentRepository(db_session)
        comments: list = feed_service.get_comments(feed_id, page_cursor, limit, user_id, feed_comment_repo)
        number_of_comment: int = feed_service.get_comment_count_of_the_feed(feed_id, feed_comment_repo)
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

        if 'comment' not in params.keys() or params['comment'].strip() == '':
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (comment).'
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        elif 'group' not in params.keys():
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (group).'
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        else:
            comment: [str, None] = params['comment']
            group: [int, None] = params['group']
            feed_mappers()
            feed_repo: FeedRepository = FeedRepository(db_session)
            feed_comment_repo: FeedCommentRepository = FeedCommentRepository(db_session)

            notification_repo: NotificationRepository = NotificationRepository(db_session)
            point_history_repo: PointHistoryRepository = PointHistoryRepository(db_session)
            push_history_repo: PushHistoryRepository = PushHistoryRepository(db_session)
            user_repo: UserRepository = UserRepository(db_session)

            new_feed_comment: FeedComment = FeedComment(
                id=None,
                comment=comment,
                feed_id=feed_id,
                user_id=user_id,
                group=group,
                depth=0,
                deleted_at=None
            )

            add_comment: dict = feed_service.add_comment(new_feed_comment, feed_comment_repo, feed_repo, notification_repo, point_history_repo, push_history_repo, user_repo)
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
        error_message = f'{ERROR_RESPONSE[405]} ({request.method})'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 405


@api.route('/feed/<int:feed_id>/point', methods=['GET'])
def test_feed_comment_point_calculate(feed_id: int):
    user_id: [int, None] = authenticate(request, db_session)
    point_history_mappers()
    point_history_repo = PointHistoryRepository(db_session)
    result = feed_service.can_the_user_get_feed_comment_point(feed_id, user_id, point_history_repo)
    clear_mappers()
    db_session.close()

    return json.dumps({'result': result}, ensure_ascii=False), 200


@api.route('/feed/<int:feed_id>/comment/<int:feed_comment_id>', methods=['PATCH', 'DELETE'])
def feed_comment_manipulate(feed_id: int, feed_comment_id: int):
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        return json.dumps(failed_response(ERROR_RESPONSE[401]), ensure_ascii=False), 401

    if feed_id is None:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[400]} (feed_id).'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 400

    if feed_comment_id is None:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[400]} (feed_comment_id).'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 400

    if request.method == 'PATCH':
        params = json.loads(request.get_data())
        if 'comment' not in params.keys() or params['comment'].strip() == '':
            db_session.close()
            error_message = f'{ERROR_RESPONSE[400]} (comment).'
            return json.dumps(failed_response(error_message), ensure_ascii=False), 400
        else:
            new_comment = params['comment']
            feed_comment_mappers()
            feed_comment_repo: FeedCommentRepository = FeedCommentRepository(db_session)
            new_feed_comment: FeedComment = FeedComment(
                id=feed_comment_id,
                user_id=user_id,
                feed_id=feed_id,
                comment=new_comment,
                depth=0,
                group=0,
                deleted_at=None
            )
            update_comment: dict = feed_service.update_comment(new_feed_comment, feed_comment_repo)
            clear_mappers()
            if update_comment['result']:
                db_session.commit()
                db_session.close()
                return json.dumps(update_comment, ensure_ascii=False), 200
            else:
                db_session.close()
                return json.dumps({key: value for key, value in update_comment.items() if key != 'status_code'}, ensure_ascii=False), update_comment['status_code']
    elif request.method == 'DELETE':
        feed_comment_mappers()
        # feed_mappers()
        feed_comment_repo: FeedCommentRepository = FeedCommentRepository(db_session)
        point_history_repo: PointHistoryRepository = PointHistoryRepository(db_session)
        user_repo: UserRepository = UserRepository(db_session)
        comment_record: FeedComment = FeedComment(
            id=feed_comment_id,
            user_id=user_id,
            feed_id=feed_id,
            comment='',
            depth=0,
            group=0,
            deleted_at=None
        )
        delete_comment: dict = feed_service.delete_comment(comment_record, feed_comment_repo, point_history_repo, user_repo)
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
        error_message = f'{ERROR_RESPONSE[405]} ({request.method})'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 405


@api.route('/feed/<int:feed_id>/like', methods=['GET', 'POST', 'DELETE'])
def feed_check(feed_id: int):
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        return json.dumps(failed_response(ERROR_RESPONSE[401]), ensure_ascii=False), 401

    if feed_id is None:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[400]} (feed_id).'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 400

    if request.method == 'GET':
        page_cursor: int = get_query_strings_from_request(request, 'cursor', INITIAL_ASCENDING_PAGE_CURSOR)
        limit: int = get_query_strings_from_request(request, 'limit', INITIAL_PAGE_LIMIT)
        page: int = get_query_strings_from_request(request, 'page', INITIAL_PAGE)

        feed_check_mappers()
        feed_check_repo: FeedCheckRepository = FeedCheckRepository(db_session)
        liked_users: list = feed_service.get_user_list_who_like_this_feed(feed_id, user_id, page_cursor, limit, feed_check_repo)
        number_of_liked_users: int = feed_service.get_like_count_of_the_feed(feed_id, feed_check_repo)
        clear_mappers()

        last_cursor: [str, None] = None if len(liked_users) <= 0 else liked_users[-1]['cursor']  # 배열 원소의 cursor string

        result: dict = {
            'result': True,
            'data': liked_users,
            'cursor': last_cursor,
            'totalCount': number_of_liked_users,
        }
        db_session.close()
        return json.dumps(result, ensure_ascii=False), 200
    elif request.method == 'POST':
        # feed_check_mappers()
        feed_mappers()
        feed_like_repo: FeedCheckRepository = FeedCheckRepository(db_session)
        feed_repo: FeedRepository = FeedRepository(db_session)
        notification_repo: NotificationRepository = NotificationRepository(db_session)
        point_history_repo: PointHistoryRepository = PointHistoryRepository(db_session)
        push_history_repo: PushHistoryRepository = PushHistoryRepository(db_session)
        user_repo: UserRepository = UserRepository(db_session)

        new_feed_check: FeedCheck = FeedCheck(user_id=user_id, feed_id=feed_id, point=0, deleted_at=None)
        like_feed = feed_service.increase_like(
            new_feed_check,
            feed_like_repo,
            feed_repo,
            notification_repo,
            point_history_repo,
            push_history_repo,
            user_repo
        )
        clear_mappers()

        if like_feed['result']:
            db_session.commit()
            db_session.close()
            return json.dumps(like_feed, ensure_ascii=False), 200
        else:
            db_session.close()
            return json.dumps({key: value for key, value in like_feed.items() if key != 'status_code'}, ensure_ascii=False), like_feed['status_code']
    elif request.method == 'DELETE':
        feed_mappers()
        feed_like_repo: FeedCheckRepository = FeedCheckRepository(db_session)
        feed_repo: FeedRepository = FeedRepository(db_session)
        feed_like: FeedCheck = FeedCheck(user_id=user_id, feed_id=feed_id, point=0, deleted_at=None)

        cancel_like = feed_service.decrease_like(feed_like, feed_like_repo, feed_repo)
        clear_mappers()

        if cancel_like['result']:
            db_session.commit()
            db_session.close()
            return json.dumps(cancel_like, ensure_ascii=False), 200
        else:
            db_session.close()
            return json.dumps({key: value for key, value in cancel_like.items() if key != 'status_code'}, ensure_ascii=False), cancel_like['status_code']

    else:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[405]} ({request.method})'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 405


@api.route("/newsfeed", methods=['GET'])
def get_newsfeed():
    user_id: [int, None] = authenticate(request, db_session)
    if user_id is None:
        db_session.close()
        return json.dumps(failed_response(ERROR_RESPONSE[401]), ensure_ascii=False), 401

    if request.method == 'GET':
        page_cursor: int = get_query_strings_from_request(request, 'cursor', INITIAL_DESCENDING_PAGE_CURSOR)
        limit: int = get_query_strings_from_request(request, 'limit', INITIAL_PAGE_LIMIT)
        page: int = get_query_strings_from_request(request, 'page', INITIAL_PAGE)

        feed_mappers()
        feed_repo: FeedRepository = FeedRepository(db_session)
        mission_stat_repo: MissionStatRepository = MissionStatRepository(db_session)
        newsfeeds: list = feed_service.get_newsfeeds(user_id, page_cursor, limit, feed_repo, mission_stat_repo)  # 여기서 캐시를 한 번에 clear하기 때문에, number_of_newsfeeds는 반드시 이보다 밑에 호출되어야 한다.
        number_of_newsfeeds: int = feed_service.get_count_of_newsfeeds(user_id, page_cursor, feed_repo)
        clear_mappers()

        last_cursor: [str, None] = None if len(newsfeeds) <= 0 else newsfeeds[-1]['cursor']  # 배열 원소의 cursor string

        result: dict = {
            'result': True,
            'data': newsfeeds,
            'cursor': last_cursor,
            'totalCount': number_of_newsfeeds,
        }
        db_session.close()
        return json.dumps(result, ensure_ascii=False), 200
    else:
        db_session.close()
        error_message = f'{ERROR_RESPONSE[405]} ({request.method})'
        return json.dumps(failed_response(error_message), ensure_ascii=False), 405
