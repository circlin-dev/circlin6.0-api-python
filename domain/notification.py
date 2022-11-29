class Notification:
    def __init__(
            self,
            id: [int, None],
            target_id: int,
            type: [str, None],
            user_id: int or None,
            read_at: [str, None],
            variables: dict or None,
            **kwargs
    ):
        self.id = id
        self.target_id = target_id
        self.type = type
        self.user_id = user_id
        self.read_at = read_at
        self.variables = variables
        self.feed_id = kwargs.get('feed_id')
        self.feed_comment_id = kwargs.get('feed_comment_id')
        self.mission_id = kwargs.get('mission_id')
        self.mission_comment_id = kwargs.get('mission_comment_id')
        self.mission_stat_id = kwargs.get('mission_stat_id')
        self.notice_id = kwargs.get('notice_id')
        self.notice_comment_id = kwargs.get('notice_comment_id')
        self.board_id = kwargs.get('board_id')
        self.board_comment_id = kwargs.get('board_comment_id')
