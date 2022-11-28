class PointHistory:
    def __init__(
            self,
            user_id: int,
            point: int,
            reason: str,
            result: int,
            **kwargs
    ):
        self.user_id = user_id
        self.point = point
        self.reason = reason
        self.result = result
        self.feed_id = kwargs.get("feed_id")
        self.feed_comment_id = kwargs.get("feed_comment_id")
        self.order_id = kwargs.get("order_id")
        self.mission_id = kwargs.get("mission_id")
        self.food_rating_id = kwargs.get("food_rating_id")
