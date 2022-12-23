import abc
from adapter.orm import mission_categories
from domain.mission import Mission, MissionCategory, MissionStat
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
        condition = and_(
            Mission.is_show == 1,
            Mission.deleted_at == None,
            Mission.mission_category_id == category_id,
            Mission.id < page_cursor,
            MissionStat.mission_id == Mission.id,
            case(
                (Mission.ended_at == None, MissionStat.ended_at == None),
                else_=case(
                    (Mission.ended_at <= func.now(), MissionStat.ended_at >= Mission.ended_at),  # 미션이 종료된 것
                    else_=MissionStat.ended_at == None  # 종료되지 않은 미션
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
                (Mission.ended_at <= func.now(), MissionStat.ended_at != None),  # 미션이 종료된 것
                else_=MissionStat.ended_at == None  # 종료되지 않은 미션
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
            Mission.mission_type,
            func.date_format(Mission.created_at, '%Y/%m/%d %H:%i:%s').label('created_at'),
            func.date_format(Mission.started_at, '%Y/%m/%d %H:%i:%s').label('started_at'),
            func.date_format(Mission.ended_at, '%Y/%m/%d %H:%i:%s').label('ended_at'),
            func.date_format(Mission.reserve_started_at, '%Y/%m/%d %H:%i:%s').label('reserve_started_at'),
            func.date_format(Mission.reserve_ended_at, '%Y/%m/%d %H:%i:%s').label('reserve_ended_at'),
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
