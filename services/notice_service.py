from adapter.repository.notice import AbstractNoticeRepository
from adapter.repository.notice_comment import AbstractNoticeCommentRepository
from domain.notice import Notice

import json


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


def get_comment_count_of_the_notice(board_id, notice_comment_repo: AbstractNoticeCommentRepository) -> int:
    return notice_comment_repo.count_number_of_comment(board_id)


def get_comments(notice_id: int, page_cursor: int, limit: int, user_id: int, notice_comment_repo: AbstractNoticeCommentRepository) -> list:
    comments: list = notice_comment_repo.get_list(notice_id, page_cursor, limit, user_id)
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