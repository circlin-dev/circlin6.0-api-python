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


class MissionCondition:
    def __init__(
            self,
            mission_id: int,
            certification_criterion: str,
            amount_determining_daily_success: float or None,
            input_scale: str or None,
            minimum_input: float or None,
            maximum_input: int or None,
            input_placeholder: str or None
    ):
        self.mission_id = mission_id
        self.certification_criterion = certification_criterion
        self.amount_determining_daily_success = amount_determining_daily_success
        self.input_scale = input_scale
        self.minimum_input = minimum_input
        self.maximum_input = maximum_input
        self.input_placeholder = input_placeholder


class MissionGround:
    def __init__(self):
        pass


class MissionGroundText:
    def __init__(self):
        pass


class MissionImage:
    def __init__(self, id: int, mission_id: int, order: int, type: str, image: str):
        self.id = id
        self.mission_id = mission_id
        self.order = order
        self.type = type
        self.image = image


class MissionIntroduce:
    def __init__(
            self,
            mission_id: int,
            logo_image: str or None,
            intro_video: str or None,
            code: str or None,
            code_title: str or None,
            code_placeholder: str or None,
            code_image: str or None
    ):
        self.mission_id = mission_id
        self.logo_image = logo_image
        self.intro_video = intro_video
        self.code = code
        self.code_title = code_title
        self.code_placeholder = code_placeholder
        self.code_image = code_image


class MissionNotice:
    def __init__(self, id: int or None, mission_id: int, created_at: str, updated_at: str, title: str, body: str):
        self.id = id
        self.mission_id = mission_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.title = title
        self.body = body


class MissionNoticeImage:
    def __init__(self, id: int or None, mission_notice_id: int, order: int, type: str, image: str):
        self.id = id
        self.mission_notice_id = mission_notice_id
        self.order = order
        self.type = type
        self.image = image


class MissionPlayground:
    def __init__(self, mission_id: int, background_image: str or None, rank_title: str or None, rank_value: str or None, rank_scale: str or None):
        self.mission_id = mission_id
        self.background_image = background_image
        self.rank_title = rank_title
        self.rank_value = rank_value
        self.rank_scale = rank_scale


class MissionPlaygroundCertificate:
    def __init__(self, mission_playground_id: int):
        self.mission_playground_id = mission_playground_id


class MissionPlaygroundGround:
    def __init__(self, mission_playground_id: int):
        self.mission_playground_id = mission_playground_id


class MissionPlaygroundRecord:
    def __init__(self, mission_playground_id: int):
        self.mission_playground_id = mission_playground_id


class MissionProduct:
    def __init__(self, mission_id: int, type: str, product_id: int or None, outside_product_id: int or None, food_id: int):
        self.mission_id = mission_id
        self.type = type
        self.product_id = product_id
        self.outside_product_id = outside_product_id
        self.food_id = food_id


class MissionRank:
    def __init__(self, id: int or None, mission_id: int, created_at: str):
        self.id = id
        self.mission_id = mission_id
        self.created_at = created_at


class MissionRankUser:
    def __init__(self, id: int or None, mission_rank_id: int, user_id: int, rank: int, feeds_count: int, summation: int):
        self.id = id
        self.mission_rank_id = mission_rank_id
        self.user_id = user_id
        self.rank = rank
        self.feeds_count = feeds_count
        self.summation = summation


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
