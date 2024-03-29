class Notice:
    def __init__(
            self,
            id: [int, None],
            title: str,
            content: str,
            link_text: str,
            link_url: [str, None],
            is_show: [int, bool],
            deleted_at: [str, None]
    ):
        self.id = id
        self.title = title
        self.content = content
        self.link_text = link_text
        self.link_url = link_url
        self.is_show = is_show
        self.deleted_at = deleted_at


class NoticeComment:
    def __init__(
            self,
            id: int or None,
            notice_id: int,
            user_id: int,
            group: int,
            depth: int,
            comment: str,
            deleted_at: [str, None]
    ):
        self.id = id
        self.notice_id = notice_id
        self.user_id = user_id
        self.group = group
        self.depth = depth
        self.comment = comment
        self.deleted_at = deleted_at


class NoticeImage:
    def __init__(self, notice_id: int, order: int, type: str, image: str):
        self.notice_id = notice_id
        self.order = order
        self.type = type
        self.image = image
