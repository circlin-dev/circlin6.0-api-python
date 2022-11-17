from dataclasses import dataclass


@dataclass(unsafe_hash=True)
class BoardWriter:
    id: int
    profile: str
    followed: bool
    nickname: str
    followers: int
    isBlocked: bool
    area: str


class Board:
    def __init__(
            self,
            id: int or None,
            body: str,
            # created_at: str,
            # images: list,
            user_id: int, #BoardWriter,
            # comments_count: int,
            # likes_count: int,
            # liked: bool,
            board_category_id: int,
            is_show: bool,
            deleted_at: str or None,
            # cursor: str
    ):
        self.id = id
        self.body = body
        # self.created_at = created_at
        # self.images = images
        self.user_id = user_id
        # self.comments_count = comments_count
        # self.likes_count = likes_count
        # self.liked = liked
        self.board_category_id = board_category_id
        self.is_show = is_show
        self.deleted_at = deleted_at
        # self.cursor = cursor


class BoardCategory:
    def __init__(self, id: int, title: str):
        self.id = id
        self.title = title


class BoardComment:
    def __init__(
            self,
            id: int or None,
            board_id: int,
            group: int,
            depth: int,
            comment: str,
            user_id: int,
    ):
        self.id = id
        self.board_id = board_id
        self.group = group
        self.depth = depth
        self.comment = comment
        self.user_id = user_id


class BoardLike:
    def __init__(self, id: int or None, user_id: int, board_id: int):
        self.id = id
        self.user_id = user_id
        self.board_id = board_id


class BoardFile:
    def __init__(self, id: int or None, board_id: int, order: int, type: str, file_id: int):
        self.id = id
        self.board_id = board_id
        self.order = order
        self.type = type
        self.file_id = file_id
