from adapter.repository.board import AbstractBoardRepository
from adapter.repository.board_comment import AbstractBoardCommentRepository
from adapter.repository.board_image import AbstractBoardImageRepository
from adapter.repository.board_like import AbstractBoardLikeRepository
from adapter.repository.notification import NotificationRepository
from adapter.repository.push import PushHistoryRepository
from adapter.repository.user import AbstractUserRepository

from domain.board import Board, BoardImage, BoardComment, BoardLike
from domain.notification import Notification
from domain.push import PushHistory
from domain.user import User

from helper.constant import PUSH_TITLE_BOARD
from helper.function import failed_response

from services import file_service, push_service, notification_service

import json


# region board
def get_count_of_boards(repo: AbstractBoardRepository) -> int:
    return repo.count_number_of_board()


def check_if_user_is_the_owner_of_the_board(board_owner_id: int, request_user_id: int) -> bool:
    return board_owner_id == request_user_id


def board_is_undeleted(board: Board) -> bool:
    return True if board.deleted_at is None else False


def board_is_visible(board: Board) -> bool:
    return True if board.is_show == 1 else False


def board_is_available_to_other(board: Board) -> bool:
    return board_is_visible(board) is True and board_is_undeleted(board) is True


def get_board_list(user_id: int, page_cursor: int, limit: int, repo: AbstractBoardRepository) -> list:
    board_list = repo.get_list(user_id, page_cursor, limit)
    entries = [
        dict(
            id=board.id,
            body=board.body,
            createdAt=board.created_at,
            images=json.loads(board.images) if json.loads(board.images)[0]['pathname'] is not None else [],
            user=dict(
                id=board.user_id,
                profile=board.profile_image,
                followed=True if (board.followed == 1 or board.user_id == user_id) else False,
                nickname=board.nickname,
                followers=board[-4],
                isBlocked=True if board.is_blocked == 1 else False,
                area=board[-3]
            ),
            boardCategoryId=board.board_category_id,
            likesCount=board[-2],
            liked=True if board.liked == 1 else False,
            commentsCount=board[-1],
            isShow=True if board.is_show == 1 else False,
            cursor=board.cursor
        ) for board in board_list
    ]
    return entries


def get_a_board(board_id: int, user_id: int, board_repo: AbstractBoardRepository) -> dict:
    board: Board = board_repo.get_one(board_id, user_id)

    if board is None or board_is_undeleted(board) is False:
        error_message = '이미 삭제한 게시글이거나, 존재하지 않는 게시글입니다.'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    else:
        board_dict = dict(
            id=board.id,
            body=board.body,
            createdAt=board.created_at,
            images=json.loads(board.images) if json.loads(board.images)[0]['pathname'] is not None else [],
            user=dict(
                id=board.user_id,
                profile=board.profile_image,
                followed=True if (board.followed == 1 or board.user_id == user_id) else False,
                nickname=board.nickname,
                followers=board[-4],
                isBlocked=True if board.is_blocked == 1 else False,
                area=board[-3]
            ),
            boardCategoryId=board.board_category_id,
            likesCount=board[-2],
            liked=True if board.liked == 1 else False,
            commentsCount=board[-1],
            isShow=True if board.is_show == 1 else False,
        ) if board is not None else None

        return {'result': True, 'data': board_dict}


def create_new_board(new_board: Board, board_repo: AbstractBoardRepository) -> int:
    new_board_id: int = board_repo.add(new_board)
    return new_board_id


def create_board_image(board_id: int, order: int, file, s3_object_path: str, board_image_repo: AbstractBoardImageRepository) -> bool:
    board_image_data: dict = file_service.upload_single_file_to_s3(file, s3_object_path)

    original_board_image: dict = board_image_data['original_file']
    resized_board_images: [dict, None] = board_image_data['resized_file']
    new_original_board_image: BoardImage = BoardImage(
        id=None,
        board_id=board_id,
        order=order,
        path=original_board_image['path'],
        file_name=original_board_image['file_name'],
        mime_type=original_board_image['mime_type'],
        size=original_board_image['size'],
        width=original_board_image['width'],
        height=original_board_image['height'],
        original_file_id=None
    )

    original_file_id = board_image_repo.add(order, new_original_board_image)

    if resized_board_images is []:
        pass
    else:
        for resized_file in resized_board_images:
            resized_board_image: BoardImage = BoardImage(
                id=None,
                board_id=board_id,
                order=order,
                path=resized_file['path'],
                file_name=resized_file['file_name'],
                mime_type=resized_file['mime_type'],
                size=resized_file['size'],
                width=resized_file['width'],
                height=resized_file['height'],
                original_file_id=original_file_id
            )
            board_image_repo.add(order, resized_board_image)

    return True


def update_board(board: Board, request_user_id: int, board_repo: AbstractBoardRepository) -> dict:
    target_board: Board = board_repo.get_one(board.id, request_user_id)

    if target_board is None or board_is_undeleted(target_board) is False:
        error_message = '이미 삭제한 게시글이거나, 존재하지 않는 게시글입니다.'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    elif check_if_user_is_the_owner_of_the_board(target_board.user_id, request_user_id) is False:
        error_message = '타인이 쓴 게시글이므로 수정할 권한이 없습니다.'
        result = failed_response(error_message)
        result['status_code'] = 403
        return result
    else:
        board_repo.update(board)
        return {'result': True}


def delete_board(board_id, request_user_id: int, board_repo: AbstractBoardRepository) -> dict:
    target_board = board_repo.get_one(board_id, request_user_id)

    if target_board is None or board_is_undeleted(target_board) is False:
        error_message = '이미 삭제한 게시글이거나, 존재하지 않는 게시글입니다.'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    elif check_if_user_is_the_owner_of_the_board(target_board.user_id, request_user_id) is False:
        error_message = '타인이 쓴 게시글이므로 삭제할 권한이 없습니다.'
        result = failed_response(error_message)
        result['status_code'] = 403
        return result
    else:
        board_repo.delete(target_board)
        return {'result': True}
# endregion


# region board comment
def check_if_user_is_the_owner_of_the_board_comment(board_comment_owner_id: int, request_user_id: int) -> bool:
    return board_comment_owner_id == request_user_id


def board_comment_is_undeleted(board_comment: BoardComment) -> bool:
    return True if board_comment.deleted_at is None else False


def get_comment_count_of_the_board(board_id, board_comment_repo: AbstractBoardCommentRepository) -> int:
    return board_comment_repo.count_number_of_comment(board_id)


def get_comments(board_id: int, page_cursor: int, limit: int, user_id: int, board_comment_repo: AbstractBoardCommentRepository) -> list:
    comments: list = board_comment_repo.get_list(board_id, page_cursor, limit, user_id)
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
            profileImage=comment.profile_image,
            gender=comment.gender,
            cursor=comment.cursor
        ) for comment in comments
    ]
    return entries


def add_comment(new_board_comment: BoardComment,
                board_comment_repo: AbstractBoardCommentRepository,
                board_repo: AbstractBoardRepository,
                notification_repo: NotificationRepository,
                push_history_repo: PushHistoryRepository,
                user_repo: AbstractUserRepository
                ) -> dict:
    target_board: Board = board_repo.get_one(new_board_comment.board_id, new_board_comment.user_id)

    # 1. 게시물에 댓글을 작성할할 수 있는 상태인지 확인한다.
    if target_board is None:
        error_message = '존재하지 않는 게시글입니다.'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    elif target_board is not None and not board_is_available_to_other(target_board) and not check_if_user_is_the_owner_of_the_board(target_board.user_id, new_board_comment.user_id):
        # 1-1. 숨김 처리되었거나, 삭제된 게시물에는 게시글 주인 외에는 댓글 작성 불가능
        error_message = '작성자가 숨김 처리 했거나, 삭제하여 접근할 수 없는 게시글에는 댓글을 작성할 수 없습니다.'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    elif target_board is not None and not board_is_available_to_other(target_board) and check_if_user_is_the_owner_of_the_board(target_board.user_id, new_board_comment.user_id):
        # 작성 가능
        pass
    else:
        # 작성 가능
        pass

    # 2. 댓글 혹은 답글을 판단하여 등록한다.
    # 2-1.해당 게시글의 댓글 comment_group값 중 최대값을 가져온다(max_group).
    max_comment_group_value: [int, None] = board_comment_repo.get_maximum_comment_group_value(new_board_comment.board_id)
    if max_comment_group_value is None:
        # 2-2. max_comment_group_value가 Null인 경우, 첫 댓글이므로 group, depth에 초기값을 적용한다(각각 1, 0).
        comment_group = 1
        depth = 0
    else:
        # 2-3. max_comment_group_value이 Null이 아닌 경우, group으로 새 댓글인지 대댓글인지 판단하고 comment_group값과 max_comment_group_value이 + 1을 비교하여 depth를 결정한다.
        comment_group = new_board_comment.group if new_board_comment.group >= 1 else max_comment_group_value + 1  # 인자로 전달된 group value가 -1보다 크다면 답글이다. 댓글이라면, 현재의 comment group 최대값보다 1만큼 큰 새로운 댓글을 단다.
        depth = 0 if comment_group >= max_comment_group_value + 1 else 1
    new_board_comment.group = comment_group
    new_board_comment.depth = depth

    inserted_board_comment_id: int = board_comment_repo.add(new_board_comment)
    commented_user: User = user_repo.get_one(new_board_comment.user_id)
    commented_user_nickname: str = commented_user.nickname

    # 3. 알림, 푸쉬
    # depth 로 댓글 인지, 대댓글 인지 판단.
    # 댓글: 게시글 주인이 나일 경우는 아무 것도 하지 않고, 아닐 경우만 게시글 주인에 "댓글" 알림, 푸쉬를 보낸다.
    # 답글: 같은 댓글 group 에 속한 댓글/답글 작성자 리스트 를 구하고, 그 중 본인을 제외 하고 "답글" 알림, 푸쉬를 보낸다. 단, 중복은 제거.
    # 답글: 같은 댓글 group 에 속한 댓글/답글 작성자 리스트 에 게시글 작성자 가 속해 있지 않는 한, 게시글 작성자 에게 보내지 않는다(To Be Determined).
    ##################################################################################################################
    # (1) Push 발송 함수
    # (2) Notification 생성 함수
    if depth <= 0:
        push_type: str = f"board_comment.{str(new_board_comment.board_id)}"
        push_body = f'{commented_user_nickname}님이 내 게시글에 댓글을 남겼습니다.\r\n\\"{new_board_comment.comment}\\"'
        notification_type: str = 'board_comment'
        if not check_if_user_is_the_owner_of_the_board(target_board.user_id, new_board_comment.user_id):
            push_target: list = user_repo.get_push_target([target_board.user_id])
        else:
            push_target: list = []
    else:
        push_type = f"board_reply.{str(new_board_comment.board_id)}"
        push_body = f'{commented_user_nickname}님이 게시판의 내 댓글에 답글을 남겼습니다.\r\n\\"{new_board_comment.comment}\\"'
        notification_type: str = 'board_reply'

        users_who_belonged_to_same_comment_group: list = list(set(board_comment_repo.get_users_who_belonged_to_same_comment_group(new_board_comment.board_id, comment_group)))
        users_who_belonged_to_same_comment_group.remove(new_board_comment.user_id) if new_board_comment.user_id in users_who_belonged_to_same_comment_group else None
        push_target: list = user_repo.get_push_target(users_who_belonged_to_same_comment_group)

    for index, target_user in enumerate(push_target):
        device_token = target_user.device_token
        device_type = target_user.device_type

        link_data: dict = {
            "route": "Sub",
            "screen": "BoardDetail",
            "params": {
                "id": new_board_comment.board_id,
                "comment_id": inserted_board_comment_id
            }
        }
        push_message: PushHistory = PushHistory(
            id=None,
            target_id=target_user.id,
            device_token=device_token,
            title=PUSH_TITLE_BOARD,
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
            user_id=new_board_comment.user_id,
            read_at=None,
            variables={f'{notification_type}': new_board_comment.comment},
            board_id=new_board_comment.board_id,
            board_comment_id=inserted_board_comment_id
        )
        notification_service.create_notification(notification, notification_repo)

    return {'result': True}


def update_comment(board_comment: BoardComment, board_comment_repo: AbstractBoardCommentRepository) -> dict:
    target_comment: BoardComment = board_comment_repo.get_one(board_comment.id)

    if target_comment is None or board_comment_is_undeleted(target_comment) is False:
        error_message = '이미 삭제한 댓글이거나, 존재하지 않는 댓글입니다.'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    elif check_if_user_is_the_owner_of_the_board_comment(target_comment.user_id, board_comment.user_id) is False:
        error_message = '타인이 쓴 댓글이므로 수정할 권한이 없습니다.'
        result = failed_response(error_message)
        result['status_code'] = 403
        return result
    else:
        board_comment_repo.update(board_comment)
        return {'result': True}


def delete_comment(board_comment: BoardComment, board_comment_repo: AbstractBoardCommentRepository) -> dict:
    target_comment: BoardComment = board_comment_repo.get_one(board_comment.id)

    if target_comment is None or board_comment_is_undeleted(target_comment) is False:
        error_message = '이미 삭제한 댓글이거나, 존재하지 않는 댓글입니다.'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    elif check_if_user_is_the_owner_of_the_board_comment(target_comment.user_id, board_comment.user_id) is False:
        error_message = '타인이 쓴 댓글이므로 수정할 권한이 없습니다.'
        result = failed_response(error_message)
        result['status_code'] = 403
        return result
    else:
        board_comment_repo.delete(target_comment)
        return {'result': True}
# endregion


# region board like
def get_like_count_of_the_board(board_id, board_like_repo: AbstractBoardLikeRepository) -> int:
    return board_like_repo.count_number_of_like(board_id)


def get_user_list_who_like_this_board(board_id: int, user_id: int, page_cursor: int, limit: int, board_like_repo: AbstractBoardLikeRepository) -> list:
    liked_users: list = board_like_repo.get_liked_user_list(board_id, user_id, page_cursor, limit)
    entries: list = [dict(
        id=user.id,
        nickname=user.nickname,
        gender=user.gender,
        profile=user.profile_image,
        followers=user.followers,
        area=user.area,
        followed=True if user.followed == 1 else False,
        cursor=user.cursor
    ) for user in liked_users]

    return entries


def increase_like(
        board_like: BoardLike,
        board_like_repo: AbstractBoardLikeRepository,
        board_repo: AbstractBoardRepository,
        user_repo: AbstractUserRepository,
        push_history_repo: PushHistoryRepository,
        notification_repo: NotificationRepository
) -> dict:

    target_board: Board = board_repo.get_one(board_like.board_id, board_like.user_id)
    if target_board is None or board_is_available_to_other(target_board) is False:
        error_message = '존재하지 않거나, 숨김처리 되었거나, 삭제된 게시글입니다.'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    else:
        liked_record: BoardLike = board_like_repo.get_liked_record(board_like)
        if liked_record is not None:
            error_message = '이미 좋아한 게시글에 중복하여 좋아요를 누를 수 없습니다.'
            result = failed_response(error_message)
            result['status_code'] = 400
            return result
        else:
            board_like_repo.add(board_like)

            # 푸시, 알림
            if not check_if_user_is_the_owner_of_the_board(target_board.user_id, board_like.user_id):

                push_target: list = user_repo.get_push_target([target_board.user_id])
                nickname_of_liked_user: str = user_repo.get_one(board_like.user_id).nickname

                for index, target_user in enumerate(push_target):
                    push_type: str = f"board_like.{str(board_like.board_id)}"
                    push_body = f'{nickname_of_liked_user}님이 내 게시글을 좋아합니다.'

                    device_token = target_user.device_token
                    device_type = target_user.device_type

                    link_data: dict = {
                        "route": "Sub",
                        "screen": "BoardDetail",
                        "params": {
                            "id": int(board_like.board_id),
                        }
                    }
                    push_message: PushHistory = PushHistory(
                        id=None,
                        target_id=target_user.id,
                        device_token=device_token,
                        title=PUSH_TITLE_BOARD,
                        message=push_body,
                        type=push_type,
                        result=0,
                        json=link_data,
                        result_json=dict()
                    )
                    push_service.send_fcm_push(device_type, push_message, push_history_repo)

                    # 알림: 좋아요, 취소, 좋아요, 취소 시 반복적으로 알림 생성되는 것을 방지하기 위해 이전에 좋아요 누른 기록 있으면 다시  알림 생성하지 않음.
                    new_notification: Notification = Notification(
                        id=None,
                        target_id=target_user.id,
                        type='board_like',
                        user_id=board_like.user_id,
                        read_at=None,
                        variables=None,
                        board_id=board_like.board_id
                    )
                    notification_service.create_notification(new_notification, notification_repo)
            else:
                pass
            return {'result': True}


def decrease_like(board_like: BoardLike, board_like_repo: AbstractBoardLikeRepository, board_repo: AbstractBoardRepository) -> dict:
    target_board: Board = board_repo.get_one(board_like.board_id, board_like.user_id)

    if target_board is None or board_is_available_to_other(target_board) is False:
        error_message = '존재하지 않거나, 숨김처리 되었거나, 삭제된 게시글입니다.'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    else:
        liked_record: BoardLike = board_like_repo.get_liked_record(board_like)
        if liked_record is None:
            error_message = '해당 게시글에 좋아요를 누른 기록이 없습니다.'
            result = failed_response(error_message)
            result['status_code'] = 400
            return result
        else:
            board_like_repo.delete(board_like)
            return {'result': True}
# endregion
