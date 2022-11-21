class Mission:
    def __init__(
            self,
            id: [int, None],
            user_id: int,
            mission_category_id: int,
            title: str,
            description: [str, None],
            thumbnail_image: [str, None],
            reserve_started_at: [str, None],
            reserve_ended_at: [str, None],
            started_at: [str, None],
            ended_at: [str, None],
            mission_type: [str, None],
            is_show: [int, bool],
            is_event: [int, bool],
            is_ground: [int, bool],
            late_bookmarkable: [int, bool],
            subtitle: [str, None],
            is_refund: [int, bool],
            is_ocr: [int, bool],
            is_require_place: [int, bool],
            is_not_duplicate_place: [int, bool],
            is_tutorial: [int, bool],
            event_order: [int, None],
            deleted_at: [str, None],
            event_type: [int, None],
            reward_point: [int],
            success_count: [int],
            user_limit: [int],
            treasure_started_at: [str, None],
            treasure_ended_at: [str, None],
            week_duration: [int, None],
            week_min_count: [int, None]
    ):
        self.id = id
        self.user_id = user_id
        self.mission_category_id = mission_category_id
        self.title = title
        self.description = description
        self.thumbnail_image = thumbnail_image
        self.reserve_started_at = reserve_started_at
        self.reserve_ended_at = reserve_ended_at
        self.started_at = started_at
        self.ended_at = ended_at
        self.mission_type = mission_type
        self.is_show = is_show
        self.is_event = is_event
        self.is_ground = is_ground
        self.late_bookmarkable = late_bookmarkable
        self.subtitle = subtitle
        self.is_refund = is_refund
        self.is_ocr = is_ocr
        self.is_require_place = is_require_place
        self.is_not_duplicate_place = is_not_duplicate_place
        self.is_tutorial = is_tutorial
        self.event_order = event_order
        self.deleted_at = deleted_at
        self.event_type = event_type
        self.reward_point = reward_point
        self.success_count = success_count
        self.user_limit = user_limit
        self.treasure_started_at = treasure_started_at
        self.treasure_ended_at = treasure_ended_at
        self.week_duration = week_duration
        self.week_min_count = week_min_count


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
