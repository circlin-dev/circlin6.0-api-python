from adapter.repository.notice import AbstractNoticeRepository
from adapter.repository.notice_comment import AbstractNoticeCommentRepository
from adapter.repository.notification import NotificationRepository
from adapter.repository.push import PushHistoryRepository
from adapter.repository.user import AbstractUserRepository
from domain.notice import Notice, NoticeComment
from domain.notification import Notification
from domain.push import PushHistory
from domain.user import User
from helper.constant import PUSH_TITLE_NOTICE
from services import notification_service, push_service
import json


def check_if_user_is_admin(user_id: int) -> bool:
    return user_id in [4087, 4090, 71334, 2, 64477, 4051, 4340, 4400, 4083, 7]


def notice_is_undeleted(notice: Notice) -> bool:
    return True if notice.deleted_at is None else False


def notice_is_visible(notice: Notice) -> bool:
    return True if notice.is_show == 1 else False


def notice_is_available_to_other(notice: Notice) -> bool:
    return notice_is_visible(notice) is True and notice_is_undeleted(notice) is True


def get_notices(page_cursor: int, limit: int, notice_repo: AbstractNoticeRepository) -> list:
    notices: list = notice_repo.get_list(page_cursor, limit)
    entries: list = [
        dict(
            id=notice.id,
            createdAt=notice.created_at,
            title=notice.title,
            isRecent=True if notice.is_recent == 1 else False,
            cursor=notice.cursor
        ) for notice in notices
    ]
    return entries


def get_count_of_notices(repo: AbstractNoticeRepository) -> int:
    return repo.count_number_of_notice()


def get_a_notice(notice_id: int, notice_repo: AbstractNoticeRepository) -> dict:
    notice: Notice = notice_repo.get_one(notice_id)

    notice_dict = dict(
        id=notice.id,
        createdAt=notice.created_at,
        title=notice.title,
        content=notice.content,
        linkText=notice.link_text,
        linkUrl=notice.link_url,
        isRecent=True if notice.is_recent == 1 else False,
        images=[] if notice.images is None else json.loads(notice.images)
    ) if notice is not None else None

    return notice_dict


# region notice comment
def check_if_user_is_the_owner_of_the_notice_comment(notice_comment_owner_id: int, request_user_id: int) -> bool:
    return notice_comment_owner_id == request_user_id


def notice_comment_is_undeleted(notice_comment: NoticeComment) -> bool:
    return True if notice_comment.deleted_at is None else False


def get_comment_count_of_the_notice(notice_id: int, notice_comment_repo: AbstractNoticeCommentRepository) -> int:
    return notice_comment_repo.count_number_of_comment(notice_id)


def get_comments(notice_id: int, page_cursor: int, limit: int, user_id: int, notice_comment_repo: AbstractNoticeCommentRepository) -> list:
    notice_comments: list = notice_comment_repo.get_list(notice_id, page_cursor, limit, user_id)
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
        ) for comment in notice_comments
    ]
    return entries


def add_comment(new_notice_comment: NoticeComment,
                notice_comment_repo: AbstractNoticeCommentRepository,
                notice_repo: AbstractNoticeRepository,
                user_repo: AbstractUserRepository,
                push_history_repo: PushHistoryRepository,
                notification_repo: NotificationRepository
                ) -> dict:
    target_notice: Notice = notice_repo.get_one(new_notice_comment.notice_id)

    # 1. 공지사항에 댓글을 작성할 수 있는 상태인지 확인한다.
    if target_notice is None:
        return {'result': False, 'error': '존재하지 않는 공지사항입니다.', 'status_code': 400}
    elif not notice_is_available_to_other(target_notice):
        # 숨김 처리 되었거나, 삭제된 게시물 은 댓글 작성 불가능
        return {'result': False, 'error': '운영자가 숨김 처리 했거나, 삭제하여 접근할 수 없는 공지사항에는 댓글을 작성할 수 없습니다.', 'status_code': 400}
    else:
        # 작성 가능
        pass

    # 2. 댓글 혹은 답글을 판단하여 등록한다.
    # 2-1.해당 게시글의 댓글 comment_group값 중 최대값을 가져온다(max_group).
    max_comment_group_value: [int, None] = notice_comment_repo.get_maximum_comment_group_value(
        new_notice_comment.notice_id)
    if max_comment_group_value is None:
        # 2-2. max_comment_group_value가 Null인 경우, 첫 댓글이므로 group, depth에 초기값을 적용한다(각각 1, 0).
        comment_group = 1
        depth = 0
    else:
        # 2-3. max_comment_group_value이 Null이 아닌 경우, group으로 새 댓글인지 대댓글인지 판단하고 comment_group값과 max_comment_group_value이 + 1을 비교하여 depth를 결정한다.
        comment_group = new_notice_comment.group if new_notice_comment.group >= 1 else max_comment_group_value + 1  # 인자로 전달된 group value가 -1보다 크다면 답글이다. 댓글이라면, 현재의 comment group 최대값보다 1만큼 큰 새로운 댓글을 단다.
        depth = 0 if comment_group >= max_comment_group_value + 1 else 1  # comment_group과
    new_notice_comment.group = comment_group
    new_notice_comment.depth = depth

    inserted_notice_comment_id: int = notice_comment_repo.add(new_notice_comment)
    commented_user: User = user_repo.get_one(new_notice_comment.user_id)
    commented_user_nickname: str = commented_user.nickname

    # 3. 알림, 푸쉬
    # depth로 댓글이인지, 대댓글인지 판단한다.
    # 댓글: 공지시항 작성자(= admin)는 댓글 알림을 받을 필요가 없으므로, 아무 것도 하지 않는다.
    # 답글: 같은 댓글 group에 속한 댓글/답글 작성자 리스트를 구하고, 그 중 본인을 제외하고 "답글" 알림, 푸쉬를 보낸다. 단, 중복을 제거한다.
    # 답글: 같은 댓글 group에 속한 댓글/답글 작성자 리스트에 게시글 작성자가 속해있지 않는 한, 게시글 작성자에게 보내지 않는다(To Be Determined).
    ##############################################################################################################
    if depth >= 1:
        # 답글인 경우에는 알림, 푸시
        push_type = f"notice_reply.{str(new_notice_comment.notice_id)}"
        push_body = f'{commented_user_nickname}님이 공지사항의 내 댓글에 답글을 남겼습니다.\r\n\\"{new_notice_comment.comment}\\"'
        notification_type: str = 'notice_reply'

        users_who_belonged_to_same_comment_group: list = list(
            set(notice_comment_repo.get_users_who_belonged_to_same_comment_group(new_notice_comment.notice_id, comment_group))
        )
        users_who_belonged_to_same_comment_group.remove(new_notice_comment.user_id) if new_notice_comment.user_id in users_who_belonged_to_same_comment_group else None
        push_target: list = user_repo.get_push_target(users_who_belonged_to_same_comment_group)

        for index, target_user in enumerate(push_target):
            device_token = target_user.device_token
            device_type = target_user.device_type

            link_data: dict = {
                "route": "Option",
                "screen": "NoticeRoom",
                "params": {
                    "id": new_notice_comment.notice_id,
                    "comment_id": inserted_notice_comment_id
                }
            }

            push_message: PushHistory = PushHistory(
                id=None,
                target_id=target_user.id,
                device_token=device_token,
                title=PUSH_TITLE_NOTICE,
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
                user_id=new_notice_comment.user_id,
                read_at=None,
                variables={f'{notification_type}': new_notice_comment.comment},
                notice_id=new_notice_comment.notice_id,
                notice_comment_id=inserted_notice_comment_id
            )
            notification_service.create_notification(notification, notification_repo)
    else:
        # 댓글일 때는 아무 것도 하지 않음.
        pass

    return {'result': True}


def update_comment(notice_comment: NoticeComment, notice_comment_repo: AbstractNoticeCommentRepository) -> dict:
    target_comment: NoticeComment = notice_comment_repo.get_one(notice_comment.id)

    if check_if_user_is_the_owner_of_the_notice_comment(target_comment.user_id, notice_comment.user_id) is False:
        return {'result': False, 'error': '타인이 쓴 댓글이므로 수정할 권한이 없습니다.', 'status_code': 403}
    elif target_comment is None or notice_comment_is_undeleted(target_comment) is False:
        return {'result': False, 'error': '이미 삭제한 댓글이거나, 존재하지 않는 댓글입니다.', 'status_code': 400}
    else:
        notice_comment_repo.update(notice_comment)
        return {'result': True}


def delete_comment(notice_comment: NoticeComment, notice_comment_repo: AbstractNoticeCommentRepository) -> dict:
    target_comment: NoticeComment = notice_comment_repo.get_one(notice_comment.id)

    if check_if_user_is_the_owner_of_the_notice_comment(target_comment.user_id, notice_comment.user_id) is False:
        return {'result': False, 'error': '타인이 쓴 댓글이므로 삭제할 권한이 없습니다.', 'status_code': 403}
    elif target_comment is None or notice_comment_is_undeleted(target_comment) is False:
        return {'result': False, 'error': '이미 삭제한 댓글이거나, 존재하지 않는 댓글입니다.', 'status_code': 400}
    else:
        notice_comment_repo.delete(target_comment)
        return {'result': True}
