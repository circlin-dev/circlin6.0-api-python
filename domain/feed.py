class Feed:
    def __init__(
            self,
            id: [int, None],
            user_id: int,
            content: str,
            is_hidden: [int, bool],
            deleted_at: [str, None],
            distance: [float, None],
            laptime: [int, None],
            distance_origin: [float, None],
            laptime_origin: [int, None]
    ):
        self.id = id
        self.user_id = user_id
        self.content = content
        self.is_hidden = is_hidden
        self.deleted_at = deleted_at
        self.distance = distance
        self.laptime = laptime
        self.distance_origin = distance_origin
        self.laptime_origin = laptime_origin


class FeedComment:
    def __init__(
            self,
            id: [int, None],
            feed_id: int,
            user_id: int,
            group: int,
            depth: int,
            comment: str,
            deleted_at: [str, None]
    ):
        self.id = id
        self.feed_id = feed_id
        self.user_id = user_id
        self.group = group
        self.depth = depth
        self.comment = comment
        self.deleted_at = deleted_at


class FeedImage:
    def __init__(self, feed_id: int, order: int, type: str, image: str):
        self.feed_id = feed_id
        self.order = order
        self.type = type
        self.image = image
