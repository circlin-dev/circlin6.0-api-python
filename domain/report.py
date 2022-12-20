class Report:
    def __init__(self, user_id: int, reason: str, **kwargs):
        self.user_id = user_id
        self.reason = reason
        self.target_feed_id = kwargs.get("target_feed_id")
        self.target_user_id = kwargs.get("target_user_id")
        self.target_mission_id = kwargs.get("target_mission_id")
        self.target_feed_comment_id = kwargs.get("target_feed_comment_id")
        self.target_notice_comment_id = kwargs.get("target_notice_comment_id")
        self.target_mission_comment_id = kwargs.get("target_mission_comment_id")