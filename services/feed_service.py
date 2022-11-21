from adapter.repository.feed_comment import AbstractFeedCommentRepository


def get_comment_count_of_the_feed(board_id, repo: AbstractFeedCommentRepository) -> int:
    return repo.count_number_of_comment(board_id)


def get_comments(board_id: int, page_cursor: int, limit: int, user_id: int, repo: AbstractFeedCommentRepository) -> list:
    comments: list = repo.get_list(board_id, page_cursor, limit, user_id)
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