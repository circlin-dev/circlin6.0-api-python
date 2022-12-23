import abc
from adapter.orm import mission_categories
from domain.mission import Mission, MissionCategory, MissionComment, MissionStat
from domain.user import User

import abc
from sqlalchemy import and_, case, desc, distinct, func, select
from sqlalchemy.orm import aliased


class AbstractMissionRepository(abc.ABC):
    def get_list_by_category(self, user_id: int, category_id: int, page_cursor: int, limit: int):
        pass

    def count_number_of_mission_by_category(self, category_id: int):
        pass


class MissionRepository(AbstractMissionRepository):
    def __init__(self, session):
        self.session = session

    def get_list_by_category(self, user_id: int, category_id: int or None, page_cursor: int, limit: int):
        user_alias_participants = aliased(User)
        comments_count = select(func.count(MissionComment.id)).where(and_(MissionComment.mission_id == Mission.id, MissionComment.deleted_at == None))
        condition = and_(
            Mission.mission_category_id == category_id,
            Mission.is_show == 1,
            Mission.deleted_at == None,
            Mission.id < page_cursor,
            MissionStat.mission_id == Mission.id,
            case(
                (Mission.ended_at == None, MissionStat.ended_at == None),  # 종료기한(Mission.ended_at)이 없는 미션은 단순히 중도포기 여부만 체크한다.
                else_=case(
                    (Mission.ended_at <= func.now(), MissionStat.ended_at >= Mission.ended_at),  # 종료 시점이 현재보다 과거라면 종료된 미션. Mission 종료 시점과 유저의 해당 미션 종료 시점(MissionStat)을 비교한다.
                    else_=MissionStat.ended_at == None  # 종료되지 않은 미션은 단순히 중도포기 여부만 체크한다.
                )
            ),
            user_alias_participants.deleted_at == None
        ) if category_id is not None else \
            and_(
                Mission.is_show == 1,
                Mission.deleted_at == None,
                Mission.id < page_cursor,
                MissionStat.mission_id == Mission.id,
                case(
                    (Mission.ended_at == None, MissionStat.ended_at == None),  # 종료기한(Mission.ended_at)이 없는 미션은 단순히 중도포기 여부만 체크한다.
                    else_=case(
                        (Mission.ended_at <= func.now(), MissionStat.ended_at >= Mission.ended_at),  # 종료 시점이 현재보다 과거라면 종료된 미션. Mission 종료 시점과 유저의 해당 미션 종료 시점(MissionStat)을 비교한다.
                        else_=MissionStat.ended_at == None  # 종료되지 않은 미션은 단순히 중도포기 여부만 체크한다.
                    )
                ),
                user_alias_participants.deleted_at == None
        )

        sql = select(
            Mission.id,
            Mission.title,
            func.json_object(
                "id", MissionCategory.id,
                "title", MissionCategory.title,
                "emoji", MissionCategory.emoji,
            ).label("category"),
            Mission.description,
            Mission.thumbnail_image,
            func.date_format(Mission.created_at, '%Y/%m/%d %H:%i:%s').label('created_at'),
            func.date_format(Mission.started_at, '%Y/%m/%d %H:%i:%s').label('started_at'),
            func.date_format(Mission.ended_at, '%Y/%m/%d %H:%i:%s').label('ended_at'),
            func.date_format(Mission.reserve_started_at, '%Y/%m/%d %H:%i:%s').label('reserve_started_at'),
            func.date_format(Mission.reserve_ended_at, '%Y/%m/%d %H:%i:%s').label('reserve_ended_at'),
            case(
                (
                    and_(
                        Mission.reserve_started_at == None,
                        Mission.reserve_ended_at == None,
                    ),
                    case(
                        (
                            and_(
                                Mission.started_at == None,
                                Mission.ended_at == None,
                            ),
                            'ongoing'
                        ),
                        (Mission.started_at > func.now(), 'before_ongoing'),
                        (
                            and_(
                                Mission.started_at <= func.now(),
                                Mission.ended_at > func.now()
                            ),
                            'ongoing'
                        ),
                        else_='end'
                    ),
                ),
                else_=case(
                    (Mission.reserve_started_at > func.now(), 'before_reserve'),
                    (
                        and_(
                            Mission.reserve_started_at < Mission.reserve_ended_at,
                            Mission.reserve_ended_at <= Mission.started_at,
                            Mission.reserve_started_at <= func.now(),
                            func.now() < Mission.reserve_ended_at
                        ),
                        'reserve'
                    ),
                    (
                        and_(
                            Mission.reserve_started_at < Mission.reserve_ended_at,
                            Mission.started_at <= Mission.reserve_ended_at,
                            Mission.reserve_started_at <= func.now(),
                            func.now() < Mission.started_at
                        ),
                        'reserve'
                    ),
                    (
                        and_(
                            Mission.reserve_started_at < Mission.reserve_ended_at,
                            Mission.reserve_ended_at <= Mission.started_at,
                            Mission.reserve_ended_at <= func.now(),
                            func.now() < Mission.started_at
                        ),
                        'before_ongoing'
                    ),
                    (
                        and_(
                            Mission.reserve_started_at < Mission.reserve_ended_at,
                            Mission.reserve_ended_at <= Mission.started_at,
                            Mission.started_at <= func.now(),
                            func.now() < Mission.ended_at
                        ),
                        'ongoing'
                    ),
                    (
                        and_(
                            Mission.reserve_started_at < Mission.reserve_ended_at,
                            Mission.started_at <= Mission.reserve_ended_at,
                            Mission.started_at <= func.now(),
                            func.now() < Mission.ended_at
                        ),
                        'ongoing'
                    ),
                    else_='end'
                )
            ).label('status'),
            Mission.mission_type,
            func.json_object(
                'id', Mission.user_id,
                'nickname', User.nickname,
                'profile', User.profile_image,
            ).label('producer'),
            func.json_arrayagg(
                func.json_object(
                    'id', user_alias_participants.id,
                    'nickname', user_alias_participants.nickname,
                    'profile', user_alias_participants.profile_image,
                )
            ).label('participants'),
            comments_count.label('comments_count'),
            func.concat(func.lpad(Mission.id, 15, '0')).label('cursor'),
        ).join(
            User, User.id == Mission.user_id
        ).join(
            MissionCategory, MissionCategory.id == Mission.mission_category_id
        ).join(
            MissionStat, MissionStat.mission_id == Mission.id
        ).join(
            user_alias_participants, user_alias_participants.id == MissionStat.user_id
        ).where(
            condition
        ).group_by(Mission.id).order_by(desc(Mission.id)).limit(limit)
        result = self.session.execute(sql).all()
        return result

    def count_number_of_mission_by_category(self, category_id: int):
        condition = and_(
                Mission.mission_category_id == category_id,
                Mission.is_show == 1,
                Mission.deleted_at == None,
            ) if category_id is not None else \
            and_(
            Mission.is_show == 1,
            Mission.deleted_at == None,
        )
        sql = select(func.count(Mission.id)).where(condition)
        total_count = self.session.execute(sql).scalar()
        return total_count
