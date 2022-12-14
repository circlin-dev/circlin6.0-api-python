from adapter.repository.feed import AbstractFeedRepository
from adapter.repository.feed_like import AbstractFeedCheckRepository
from adapter.repository.feed_comment import AbstractFeedCommentRepository
from adapter.repository.notification import AbstractNotificationRepository
from adapter.repository.point_history import AbstractPointHistoryRepository, PointHistoryRepository
from adapter.repository.push import AbstractPushHistoryRepository
from adapter.repository.user import AbstractUserRepository
from domain.feed import Feed, FeedCheck, FeedComment
from domain.notification import Notification
from domain.point_history import PointHistory
from domain.push import PushHistory
from domain.user import User
from helper.constant import BASIC_COMPENSATION_AMOUNT_PER_REASON, PUSH_TITLE_FEED, REASONS_HAVE_DAILY_REWARD_RESTRICTION
from helper.function import failed_response
from services import notification_service, point_service, push_service
from services.mission_service import check_if_user_is_carrying_out_this_mission

from datetime import datetime, timedelta
import json


def get_newsfeeds(user_id: int, page_cursor: int, limit: int, feed_repo: AbstractFeedRepository) -> list:
    newsfeeds: list = feed_repo.get_newsfeeds(user_id, page_cursor, limit)
    entries: list = [dict(
        id=feed.id,
        createdAt=feed.created_at,
        body=feed.body,
        distance=None if feed.distance is None
        else f'{str(round(feed.distance, 2))} L' if feed.laptime is None and feed.distance_origin is None and feed.laptime_origin is None
        else f'{round(feed.distance, 2)} km',
        images=json.loads(feed.images),
        user=dict(
            id=feed.user_id,
            nickname=feed.nickname,
            profile=feed.profile_image,
            followed=True if feed.followed == 1 else False,
            followers=feed.followers,
            area=feed.area,
            gender=feed.gender,
            isBlocked=True if feed.is_blocked == 1 else False,
            isChatBlocked=True if feed.is_chat_blocked == 1 else False
        ) if feed.user_id is not None else None,
        commentsCount=feed.comments_count,
        checkedUsers=[dict(
            id=user['id'],
            nickname=user['nickname'],
            profile=user['profile_image']
        ) for user in json.loads(feed.checked_users)] if feed.checked_users is not None else [],
        checked=True if feed.checked == 1 else False,
        missions=[dict(
            id=mission['id'],
            title=mission['title'] if mission['emoji'] is None else f"{mission['emoji']}{mission['title']}",
            isEvent=True if mission['is_event'] == 1 else False,
            isOldEvent=True if mission['is_old_event'] == 1 else False,
            isGround=True if mission['is_ground'] == 1 else False,
            eventType=mission['event_type'],
            thumbnail=mission['thumbnail'],
            bookmarked=True if mission['bookmarked'] == 1 else False
        ) for mission in json.loads(feed.mission)] if json.loads(feed.mission)[0]['id'] is not None else [],
        product=json.loads(feed.product) if json.loads(feed.product)['id'] is not None else None,
        food=json.loads(feed.food) if json.loads(feed.food)['id'] is not None else None,
        cursor=feed.cursor,
    ) for feed in newsfeeds]

    return entries


def get_count_of_newsfeeds(user_id: int, page_cursor, feed_repo: AbstractFeedRepository):
    total_count = feed_repo.count_number_of_newsfeed(user_id, page_cursor)
    return total_count


def check_if_user_is_the_owner_of_the_feed(feed_owner_id: int, request_user_id: int) -> bool:
    return feed_owner_id == request_user_id


def feed_is_undeleted(feed: Feed) -> bool:
    return True if feed.deleted_at is None else False


def feed_is_visible(feed: Feed) -> bool:
    return True if feed.is_hidden == 0 else False


def feed_is_available_to_other(feed: Feed) -> bool:
    return feed_is_visible(feed) is True and feed_is_undeleted(feed) is True


def get_like_count_of_the_feed(feed_id: int, repo: AbstractFeedCheckRepository) -> int:
    return repo.count_number_of_like(feed_id)


def get_user_list_who_like_this_feed(feed_id: int, user_id: int, page_cursor: int, limit: int, repo: AbstractFeedCheckRepository) -> list:
    liked_users: list = repo.get_liked_user_list(feed_id, user_id, page_cursor, limit)
    entries: list = [dict(
        id=user.id,
        nickname=user.nickname,
        gender=user.gender,
        profile=user.profile_image,
        followed=True if user.followed == 1 else False,
        area=user.area,
        followers=user.followers,
        cursor=user.cursor
    ) for user in liked_users]

    return entries


def get_a_feed(feed_id: int, user_id: int, feed_repo: AbstractFeedRepository) -> dict:
    feed: Feed = feed_repo.get_one(feed_id, user_id)

    if feed.id is None or feed_is_undeleted(feed) is False:
        error_message = '이미 삭제한 피드이거나, 존재하지 않는 피드입니다.'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    else:
        feed_dict = dict(
            id=feed.id,
            createdAt=feed.created_at,
            body=feed.body,
            distance=None if feed.distance is None
            else f'{str(round(feed.distance, 2))} L' if feed.laptime is None and feed.distance_origin is None and feed.laptime_origin is None
            else f'{round(feed.distance, 2)} km',
            images=[] if feed.images is None else json.loads(feed.images),
            checked=feed.checked,
            commentsCount=feed.comments_count,
            checkedUsers=[dict(
                id=user['id'],
                nickname=user['nickname'],
                profile=user['profile_image']
            ) for user in json.loads(feed.checked_users)] if feed.checked_users is not None else [],
            isShow=True if feed.is_hidden == 0 else False,
            user=dict(
                id=feed.user_id,
                nickname=feed.nickname,
                profile=feed.profile_image,
                gender=feed.gender,
                followed=True if feed.followed == 1 else False,
                isBlocked=True if feed.is_blocked == 1 else False,
                isChatBlocked=True if feed.is_chat_blocked == 1 else False,
                area=feed.area,
                followers=feed.followers,
            ) if feed.user_id is not None else None,
            missions=[dict(
                id=mission['id'],
                title=mission['title'] if mission['emoji'] is None else f"{mission['emoji']}{mission['title']}",
                isEvent=True if mission['is_event'] == 1 else False,
                isOldEvent=True if mission['is_old_event'] == 1 else False,
                isGround=True if mission['is_ground'] == 1 else False,
                eventType=mission['event_type'],
                thumbnail=mission['thumbnail'],
                bookmarked=True if mission['bookmarked'] == 1 else False
            ) for mission in json.loads(feed.mission)] if json.loads(feed.mission)[0]['id'] is not None else [],
            product=json.loads(feed.product) if json.loads(feed.product)['id'] is not None else None,
            food=json.loads(feed.food) if json.loads(feed.food)['id'] is not None else None,
        ) if feed is not None else None

        return {'result': True, 'data': feed_dict}


def update_feed(new_feed: Feed, request_user_id: int, feed_repo: AbstractFeedRepository) -> dict:
    target_feed: Feed = feed_repo.get_simple_one(new_feed.id)

    if target_feed is None or feed_is_undeleted(target_feed) is False:
        error_message = '이미 삭제한 피드이거나, 존재하지 않는 피드입니다.'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    elif check_if_user_is_the_owner_of_the_feed(target_feed.user_id, request_user_id) is False:
        error_message = '타인이 쓴 피드이므로 수정할 권한이 없습니다.'
        result = failed_response(error_message)
        result['status_code'] = 403
        return result
    else:
        feed_repo.update(new_feed)
        return {'result': True}


def delete_feed(feed: Feed, request_user_id: int, feed_repo: AbstractFeedRepository) -> dict:
    target_feed: Feed = feed_repo.get_simple_one(feed.id)

    if target_feed is None or feed_is_undeleted(target_feed) is False:
        error_message = '이미 삭제한 피드이거나, 존재하지 않는 피드입니다.'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    elif check_if_user_is_the_owner_of_the_feed(target_feed.user_id, request_user_id) is False:
        error_message = '타인이 쓴 피드이므로 삭제할 권한이 없습니다.'
        result = failed_response(error_message)
        result['status_code'] = 403
        return result
    else:
        feed_repo.delete(target_feed)
        return {'result': True}


# region feed comment
def can_the_user_get_feed_comment_point(feed_id: int, user_id: int, point_history_repo: AbstractPointHistoryRepository) -> int:
    amount = point_history_repo.calculate_feed_comment_point_by_feed_id_and_user_id(feed_id, user_id)
    return True if int(amount) <= 0 else False


def is_this_comment_a_reply_to_other_user(target_comment_writer_id: int, new_feed_comment: FeedComment) -> bool:
    is_reply = new_feed_comment.depth > 0
    new_comment_writer_is_not_the_target_comment_writer = new_feed_comment.user_id != target_comment_writer_id
    return is_reply is True and new_comment_writer_is_not_the_target_comment_writer is True


def check_if_user_is_the_owner_of_the_feed_comment(feed_comment_owner_id: int, request_user_id: int) -> bool:
    return feed_comment_owner_id == request_user_id


def feed_comment_is_undeleted(feed_comment: FeedComment) -> bool:
    return True if feed_comment.deleted_at is None else False


def get_comment_count_of_the_feed(feed_id: int, repo: AbstractFeedCommentRepository) -> int:
    return repo.count_number_of_comment(feed_id)


def get_comments(feed_id: int, page_cursor: int, limit: int, user_id: int, repo: AbstractFeedCommentRepository) -> list:
    comments: list = repo.get_list(feed_id, page_cursor, limit, user_id)
    entries: list = [
        dict(
            id=comment.id,
            createdAt=comment.created_at,
            group=comment.group,
            depth=comment.depth,
            comment=comment.comment,
            userId=comment.user_id,
            isBlocked=True if comment.is_blocked == 1 else False,
            nickname=comment.nickname,
            profile=comment.profile_image,
            gender=comment.gender,
            cursor=comment.cursor
        ) for comment in comments
    ]
    return entries


def add_comment(new_feed_comment: FeedComment,
                feed_comment_repo: AbstractFeedCommentRepository,
                feed_repo: AbstractFeedRepository,
                notification_repo: AbstractNotificationRepository,
                point_history_repo: AbstractPointHistoryRepository,
                push_history_repo: AbstractPushHistoryRepository,
                user_repo: AbstractUserRepository
                ) -> dict:
    target_feed: Feed = feed_repo.get_one(new_feed_comment.feed_id, new_feed_comment.user_id)

    # 1. 게시물에 댓글을 작성할할 수 있는 상태인지 확인한다.
    if target_feed is None:
        error_message = '존재하지 않는 피드입니다.'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    elif target_feed is not None \
            and not feed_is_available_to_other(target_feed) \
            and not check_if_user_is_the_owner_of_the_feed(target_feed.user_id, new_feed_comment.user_id):
        # 1-1. 숨김 처리되었거나, 삭제된 게시물에는 게시글 주인 외에는 댓글 작성 불가능
        error_message = '작성자가 숨김 처리 했거나, 삭제하여 접근할 수 없는 게시글에는 댓글을 작성할 수 없습니다.'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    elif target_feed is not None \
            and not feed_is_available_to_other(target_feed) \
            and check_if_user_is_the_owner_of_the_feed(target_feed.user_id, new_feed_comment.user_id):
        # 작성 가능
        pass
    else:
        # 작성 가능
        pass

    # 2. 댓글 혹은 답글을 판단하여 등록한다.
    # 2-1.해당 게시글의 댓글 comment_group값 중 최대값을 가져온다(max_group).
    max_comment_group_value: [int, None] = feed_comment_repo.get_maximum_comment_group_value(new_feed_comment.feed_id)
    if max_comment_group_value is None:
        # 2-2. max_comment_group_value가 Null인 경우, 첫 댓글이므로 group, depth에 초기값을 적용한다(각각 1, 0).
        comment_group = 1
        depth = 0
    else:
        # 2-3. max_comment_group_value이 Null이 아닌 경우, group으로 새 댓글인지 대댓글인지 판단하고 comment_group값과 max_comment_group_value이 + 1을 비교하여 depth를 결정한다.
        comment_group = new_feed_comment.group if new_feed_comment.group >= 1 else max_comment_group_value + 1  # 인자로 전달된 group value가 -1보다 크다면 답글이다. 댓글이라면, 현재의 comment group 최대값보다 1만큼 큰 새로운 댓글을 단다.
        depth = 0 if comment_group >= max_comment_group_value + 1 else 1
    new_feed_comment.group = comment_group
    new_feed_comment.depth = depth

    inserted_feed_comment_id: int = feed_comment_repo.add(new_feed_comment)
    commented_user: User = user_repo.get_one(new_feed_comment.user_id)
    commented_user_nickname: str = commented_user.nickname

    # 3. 알림, 푸쉬
    # depth로 댓글이인지, 대댓글인지 판단한다.
    # 댓글: 게시글 주인이 나일 경우는 아무것도 하지 않고, 아닐 경우에만 게시글 주인에게 "댓글" 알림, 푸쉬를 보낸다.
    # 답글: 같은 댓글 group에 속한 댓글/답글 작성자 리스트를 구하고, 그 중 본인을 제외하고 "답글" 알림, 푸쉬를 보낸다. 단, 중복을 제거한다.
    # 답글: 같은 댓글 group에 속한 댓글/답글 작성자 리스트에 게시글 작성자가 속해있지 않는 한, 게시글 작성자에게 보내지 않는다(To Be Determined).
    ##################################################################################################################
    # (1) Push 발송 함수
    # (2) Notification 생성 함수
    if depth <= 0:
        push_type: str = f"feed_comment.{str(new_feed_comment.feed_id)}"
        push_body = f'{commented_user_nickname}님이 내 피드에 댓글을 남겼습니다.\r\n\\"{new_feed_comment.comment}\\"'
        notification_type: str = 'feed_comment'
        if not check_if_user_is_the_owner_of_the_feed(target_feed.user_id, new_feed_comment.user_id):
            push_target: list = user_repo.get_push_target([target_feed.user_id])
        else:
            push_target: list = []
    else:
        push_type = f"feed_reply.{str(new_feed_comment.feed_id)}"
        push_body = f'{commented_user_nickname}님이 피드의 내 댓글에 답글을 남겼습니다.\r\n\\"{new_feed_comment.comment}\\"'
        notification_type: str = 'feed_reply'

        users_who_belonged_to_same_comment_group: list = list(set(feed_comment_repo.get_users_who_belonged_to_same_comment_group(new_feed_comment.feed_id, comment_group)))
        users_who_belonged_to_same_comment_group.remove(new_feed_comment.user_id) if new_feed_comment.user_id in users_who_belonged_to_same_comment_group else None
        push_target: list = user_repo.get_push_target(users_who_belonged_to_same_comment_group)

    for index, target_user in enumerate(push_target):
        device_token = target_user.device_token
        device_type = target_user.device_type

        link_data: dict = {
            "route": "Sub",
            "screen": "Feed",
            "params": {
                "id": new_feed_comment.feed_id,
                "comment_id": inserted_feed_comment_id
            }
        }
        push_message: PushHistory = PushHistory(
            id=None,
            target_id=target_user.id,
            device_token=device_token,
            title=PUSH_TITLE_FEED,
            message=push_body,
            type=push_type,
            result=0,
            json=link_data,
            result_json=dict()
        )
        push_service.send_fcm_push(device_type, push_message, push_history_repo)

        # 알림: 좋아요, 취소, 좋아요, 취소 시 반복적으로 알림 생성되는 것을 방지하기 위해 이전에 좋아요 누른 기록 있으면 다시  알림 생성하지 않음.
        notification: Notification = Notification(
            id=None,
            target_id=target_user.id,
            type=notification_type,
            user_id=new_feed_comment.user_id,
            read_at=None,
            variables={f'{notification_type}': new_feed_comment.comment},
            feed_id=new_feed_comment.feed_id,
            feed_comment_id=inserted_feed_comment_id
        )
        notification_service.create_notification(notification, notification_repo)

    # 포인트 지급 로직 구현
    reason_for_point = "feed_comment_reward"
    foreign_key_value_of_point_history = {'feed_comment_id': inserted_feed_comment_id, 'feed_id': target_feed.id}
    if check_if_user_is_the_owner_of_the_feed(target_feed.user_id, new_feed_comment.user_id):
        user_of_comment_root = feed_comment_repo.get_a_root_comment_by_feed_and_comment_group(target_feed.id, comment_group)
        if is_this_comment_a_reply_to_other_user(user_of_comment_root, new_feed_comment):
            if can_the_user_get_feed_comment_point(target_feed.id, new_feed_comment.user_id, point_history_repo):
                point_service.give_point(
                    commented_user,
                    reason_for_point,
                    BASIC_COMPENSATION_AMOUNT_PER_REASON[reason_for_point],
                    foreign_key_value_of_point_history,
                    point_history_repo,
                    user_repo
                )
    else:
        if can_the_user_get_feed_comment_point(target_feed.id, new_feed_comment.user_id, point_history_repo):
            point_service.give_point(
                commented_user,
                reason_for_point,
                BASIC_COMPENSATION_AMOUNT_PER_REASON[reason_for_point],
                foreign_key_value_of_point_history,
                point_history_repo,
                user_repo
            )

    return {'result': True}


def update_comment(feed_comment: FeedComment, feed_comment_repo: AbstractFeedCommentRepository) -> dict:
    target_comment: FeedComment = feed_comment_repo.get_one(feed_comment.id)

    if target_comment is None or feed_comment_is_undeleted(target_comment) is False:
        error_message = '이미 삭제한 댓글이거나, 존재하지 않는 댓글입니다.'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    elif check_if_user_is_the_owner_of_the_feed_comment(target_comment.user_id, feed_comment.user_id) is False:
        error_message = '타인이 쓴 댓글이므로 수정할 권한이 없습니다.'
        result = failed_response(error_message)
        result['status_code'] = 403
        return result
    else:
        feed_comment_repo.update(feed_comment)
        return {'result': True}


def delete_comment(feed_comment: FeedComment, feed_comment_repo: AbstractFeedCommentRepository, point_history_repo: AbstractPointHistoryRepository, user_repo: AbstractUserRepository) -> dict:
    target_comment: FeedComment = feed_comment_repo.get_one(feed_comment.id)

    if target_comment is None or feed_comment_is_undeleted(target_comment) is False:
        error_message = '이미 삭제한 댓글이거나, 존재하지 않는 댓글입니다.'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    elif check_if_user_is_the_owner_of_the_feed_comment(target_comment.user_id, feed_comment.user_id) is False:
        error_message = '타인이 쓴 댓글이므로 삭제할 권한이 없습니다.'
        result = failed_response(error_message)
        result['status_code'] = 403
        return result
    else:
        point_history: PointHistory = PointHistory(
            id=None,
            user_id=feed_comment.user_id,
            feed_id=feed_comment.feed_id,
            feed_comment_id=feed_comment.id,
            reason='feed_comment_reward',
            result=0,
            point=0
        )
        point_reward_history = point_service.get_a_point_history(point_history, point_history_repo)

        if point_reward_history is None:
            pass
        else:
            # 포인트 차감 로직 구현
            reason_for_point = "feed_comment_delete"
            foreign_key_value_of_point_history = {
                'feed_comment_id': point_reward_history.feed_comment_id,
                'feed_id': point_reward_history.feed_id
            }
            point_service.deduct_point(
                user_repo.get_one(feed_comment.user_id),
                reason_for_point,
                BASIC_COMPENSATION_AMOUNT_PER_REASON[reason_for_point],
                foreign_key_value_of_point_history,
                point_history_repo,
                user_repo
            )

        feed_comment_repo.delete(target_comment)
        return {'result': True}


# region feed check(like)
def no_check_record_for_this_feed(checked_history: FeedCheck) -> bool:
    print('here0-1: ', True if checked_history is None else False)
    return True if checked_history is None else False


def feed_was_written_within_latest_24_hour(created_at: str):
    date = created_at.split(' ')[0]
    time = created_at.split(' ')[1]

    year = int(date.split('/')[0])
    month = int(date.split('/')[1])
    day = int(date.split('/')[2])

    hour = int(time.split(':')[0])
    minute = int(time.split(':')[1])
    second = int(time.split(':')[2])

    created_datetime: datetime = datetime(year, month, day, hour, minute, second)
    datetime_before_24hours_than_now: datetime = datetime.now() - timedelta(1)  # 1일 뺀 시간
    print('here0-2: ', True if created_datetime >= datetime_before_24hours_than_now else False)
    return True if created_datetime >= datetime_before_24hours_than_now else False


def never_gave_point_to_feed_writer_by_feed_check_today(feed: Feed, user_who_likes_the_feed: User, feed_like_repo: AbstractFeedCheckRepository):
    exists = feed_like_repo.record_of_like_with_points_that_were_awarded_to_writer_exists(feed, user_who_likes_the_feed)
    print('here0-3: ', False if exists else True)
    return False if exists else True


def increase_like(
        feed_like: FeedCheck,
        feed_like_repo: AbstractFeedCheckRepository,
        feed_repo: AbstractFeedRepository,
        notification_repo: AbstractNotificationRepository,
        point_history_repo: AbstractPointHistoryRepository,
        push_history_repo: AbstractPushHistoryRepository,
        user_repo: AbstractUserRepository
) -> dict:
    target_feed: Feed = feed_repo.get_one(feed_like.feed_id, feed_like.user_id)
    paid_point: bool = False  # 대상 에게 포인트 지급 여부

    feed_writer: User = user_repo.get_one(target_feed.user_id)
    user_who_likes_this_feed: User = user_repo.get_one(feed_like.user_id)
    checked_status: FeedCheck = feed_like_repo.get_one_excluding_deleted_record(feed_like)
    my_current_like_count: int = feed_like_repo.get_current_like_count_of_user(user_who_likes_this_feed)

    if target_feed is None or feed_is_available_to_other(target_feed) is False:
        error_message = '존재하지 않거나, 숨김처리 되었거나, 삭제된 피드입니다.'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    elif checked_status is not None:  # 현재 이 피드를 내가 좋아요 눌러 둔 '상태' 인지, 아닌지 확인
        # 이미 좋아요 한 상태인 피드
        error_message = '이미 좋아한 피드에 중복하여 좋아요를 누를 수 없습니다.'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    else:
        if check_if_user_is_the_owner_of_the_feed(target_feed.user_id, feed_like.user_id):
            pass
        else:
            # 알림, 푸시, 포인트 지급 로직
            # 좋아요 한 유저에게 규칙에 따라 feed_check 포인트를 지급
            available_point_for_me, current_gathered_point_for_me = point_service.points_available_to_receive_for_the_rest_of_the_day(
                user_who_likes_this_feed.id,
                REASONS_HAVE_DAILY_REWARD_RESTRICTION,
                point_history_repo
            )
            available_point_for_feed_writer, current_gathered_point_for_feed_writer = point_service.points_available_to_receive_for_the_rest_of_the_day(
                target_feed.user_id,
                REASONS_HAVE_DAILY_REWARD_RESTRICTION,
                point_history_repo
            )

            checked_history = feed_like_repo.get_one_including_deleted_record(feed_like)
            print('here0-4: ', available_point_for_feed_writer > 0)
            if no_check_record_for_this_feed(checked_history) \
                    and feed_was_written_within_latest_24_hour(target_feed.created_at) \
                    and never_gave_point_to_feed_writer_by_feed_check_today(target_feed, user_who_likes_this_feed, feed_like_repo) \
                    and available_point_for_feed_writer > 0:
                print('here1')
                # 피드 작성자에게 규칙에 따라 feed_check 포인트를 지급 => feed_like.point 수정
                reason_for_point = "feed_check"
                foreign_key_value_of_point_history = {'feed_id': target_feed.id}
                amount_of_point_given_to_feed_writer = point_service.give_point(
                    feed_writer,
                    reason_for_point,
                    BASIC_COMPENSATION_AMOUNT_PER_REASON[reason_for_point],
                    foreign_key_value_of_point_history,
                    point_history_repo,
                    user_repo
                )
                # feed_like에 데이터 저장 전 FeedCheck 객체의 데이터 초기값 변경하기
                feed_like.point = amount_of_point_given_to_feed_writer
                paid_point = True if amount_of_point_given_to_feed_writer > 0 else False

                # 알림 내역 생성
                notification: Notification = Notification(
                    id=None,
                    target_id=feed_writer.id,
                    type=reason_for_point,
                    user_id=user_who_likes_this_feed.id,
                    read_at=None,
                    variables={'point': amount_of_point_given_to_feed_writer},
                    feed_id=feed_like.feed_id
                )
                notification_service.create_notification(notification, notification_repo)

                # 푸시 발송
                push_type = f"feed_check.{str(feed_like.feed_id)}"
                push_body = f'{user_who_likes_this_feed.nickname}님이 내 피드를 체크해 {feed_like.point} 포인트를 받았습니다.'
                push_target: list = user_repo.get_push_target([feed_writer.id])

                for index, target_user in enumerate(push_target):
                    device_token = target_user.device_token
                    device_type = target_user.device_type

                    link_data: dict = {
                        "route": "Sub",
                        "screen": "Feed",
                        "params": {"id": feed_like.feed_id, "comment_id": None}
                    }

                    push_message: PushHistory = PushHistory(
                        id=None,
                        target_id=target_user.id,
                        device_token=device_token,
                        title=PUSH_TITLE_FEED,
                        message=push_body,
                        type=push_type,
                        result=0,
                        json=link_data,
                        result_json=dict()
                    )
                    push_service.send_fcm_push(device_type, push_message, push_history_repo)

                    # 나의 기록
                    if my_current_like_count % 10 == 9 and available_point_for_me > 0:
                        reason_for_point = "feed_check_reward"
                        foreign_key_value_of_point_history = {'feed_id': target_feed.id}

                        amount_of_point_given_to_me = point_service.give_point(
                            user_who_likes_this_feed,
                            reason_for_point,
                            BASIC_COMPENSATION_AMOUNT_PER_REASON[reason_for_point],
                            foreign_key_value_of_point_history,
                            point_history_repo,
                            user_repo
                        )

                        notification: Notification = Notification(
                            id=None,
                            target_id=user_who_likes_this_feed.id,
                            type=reason_for_point,
                            user_id=None,
                            read_at=None,
                            variables={'point': amount_of_point_given_to_me, 'point2': available_point_for_me - amount_of_point_given_to_me},
                        )
                        notification_service.create_notification(notification, notification_repo)
                    else:
                        pass
                    my_current_like_count += 1
            else:
                print('here2')
                # 이미 좋아요 했다가 해제했다가 다시 좋아요 한 경우. 재지급 되지 말아야 하며, 알림 및 푸시도 중복 실행되지 않아야 함.
                pass

        feed_like_repo.add(feed_like)

        available_point, current_gathered_point = point_service.points_available_to_receive_for_the_rest_of_the_day(
            user_who_likes_this_feed.id, REASONS_HAVE_DAILY_REWARD_RESTRICTION, point_history_repo)

        result = {
            'result': True,
            'paidCount': 0 if my_current_like_count is None else my_current_like_count,
            'paidPoint': paid_point,
            'todayGatheredPoint': 0 if current_gathered_point is None else current_gathered_point
        }
        return result


def decrease_like(feed_like: FeedCheck, feed_like_repo: AbstractFeedCheckRepository, feed_repo: AbstractFeedRepository) -> dict:
    target_feed: Feed = feed_repo.get_one(feed_like.feed_id, feed_like.user_id)

    if target_feed is None or feed_is_available_to_other(target_feed) is False:
        error_message = '존재하지 않거나, 숨김처리 되었거나, 삭제된 피드입니다.'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    else:
        liked_record: FeedCheck = feed_like_repo.get_one_excluding_deleted_record(feed_like)
        if liked_record is None:
            error_message = '해당 피드에 좋아요 한 기록이 없습니다.'
            result = failed_response(error_message)
            result['status_code'] = 400
            return result
        else:
            feed_like_repo.delete(feed_like)
            return {'result': True}
# endregion
