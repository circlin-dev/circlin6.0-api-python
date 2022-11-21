class Board:
    def __init__(
            self,
            id: int or None,
            body: str,
            user_id: int,
            board_category_id: int,
            is_show: bool,
            deleted_at: str or None
    ):
        self.id = id
        self.body = body
        self.user_id = user_id
        self.board_category_id = board_category_id
        self.is_show = is_show
        self.deleted_at = deleted_at


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


class BoardImage:
    def __init__(
            self,
            id: int or None,
            board_id: int,
            order: int,
            path: str,
            file_name: str,
            mime_type: str,
            size: int,
            width: int,
            height: int,
            original_file_id: int or None
    ):
        self.id = id
        self.board_id = board_id
        self.order = order
        self.path = path
        self.file_name = file_name
        self.mime_type = mime_type
        self.size = size
        self.width = width
        self.height = height
        self.original_file_id = original_file_id


class BoardLike:
    def __init__(self, id: int or None, user_id: int, board_id: int):
        self.id = id
        self.user_id = user_id
        self.board_id = board_id


