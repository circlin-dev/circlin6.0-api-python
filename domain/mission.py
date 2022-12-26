from typing import List, Dict


class Mission:
    def __init__(
            self,
            id: [int, None],
            type: str,
            status: str,
            title: str,
            description: [str, None],
            thumbnail: str,
            started_at: [str, None],
            ended_at: [str, None],
            reserve_started_at: [str, None],
            reserve_ended_at: [str, None],
            producer: dict,
            participants: List[Dict],
            participated: bool,
            comments_count: int,
            category: dict,
            product: dict or None,
            is_show: [int, bool],
            ground: bool,
            late_bookmarkable: [int, bool],
            event_order: [int, None],
            user_limit: [int],
            deleted_at: [str, None],
    ):
        self.id = id
        self.type = type
        self.status = status
        self.title = title
        self.description = description
        self.thumbnail = thumbnail
        self.started_at = started_at
        self.ended_at = ended_at
        self.reserve_started_at = reserve_started_at
        self.reserve_ended_at = reserve_ended_at
        self.producer = producer
        self.participants = participants
        self.participated = participated
        self.comments_count = comments_count
        self.category = category
        self.product = product
        self.is_show = is_show
        self.ground = ground
        self.late_bookmarkable = late_bookmarkable
        self.event_order = event_order
        self.user_limit = user_limit
        self.deleted_at = deleted_at


class MissionCategory:
    def __init__(
            self,
            id: [int, None],
            mission_category_id: [int, None],
            title: str,
            emoji: [str, None],
            description: [str, None]
    ):
        self.id = id
        self.mission_category_id = mission_category_id
        self.title = title
        self.emoji = emoji
        self.description = description


class MissionComment:
    def __init__(
            self,
            id: [int, None],
            mission_id: int,
            user_id: int,
            group: int,
            depth: int,
            comment: str,
            deleted_at: [str, None]
    ):
        self.id = id
        self.mission_id = mission_id
        self.user_id = user_id
        self.group = group
        self.depth = depth
        self.comment = comment
        self.deleted_at = deleted_at


class MissionGround:
    def __init__(self):
        pass


class MissionIntro:
    def __init__(self):
        pass


class MissionProduct:
    def __init__(self, mission_id: int, type: str, product_id: int or None, outside_product_id: int or None, food_id: int):
        self.mission_id = mission_id
        self.type = type
        self.product_id = product_id
        self.outside_product_id = outside_product_id
        self.food_id = food_id


class MissionRank:
    def __init__(self):
        pass


class MissionRefundProduct:
    def __init__(self, mission_id: int, product_id: int, limit: int):
        self.mission_id = mission_id
        self.product_id = product_id
        self.limit = limit


class MissionStat:
    def __init__(
            self,
            id: [int, None],
            user_id: int,
            mission_id: int,
            ended_at: [str, None],
            completed_at: [str, None],
            code: [str, None],
            entry_no: [int, None],
            goal_distance: [float, None],
            certification_image: [str, None]
    ):
        self.id = id
        self.user_id = user_id
        self.mission_id = mission_id
        self.ended_at = ended_at
        self.completed_at = completed_at
        self.code = code
        self.entry_no = entry_no
        self.goal_distance = goal_distance
        self.certification_image = certification_image
