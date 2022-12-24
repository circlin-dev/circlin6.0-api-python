from adapter.orm import missions, mission_stats, users
from domain.mission import MissionStat

import abc
from sqlalchemy import and_, case, exists, func, select


class AbstractMissionStatRepository(abc.ABC):
    @abc.abstractmethod
    def get_one_excluding_ended(self, user_id: int, mission_id: int) -> int:
        pass


class MissionStatRepository(AbstractMissionStatRepository):
    def __init__(self, session):
        self.session = session

    def get_one_excluding_ended(self, user_id: int, mission_id: int) -> int:
        sql = select(exists(
            mission_stats
        )).join(
            users, mission_stats.c.user_id == users.c.id, isouter=True
        ).join(
            missions, mission_stats.c.mission_id == missions.c.id
        ).where(
            mission_stats.c.mission_id == mission_id,
            mission_stats.c.user_id == user_id,
            case(
                (missions.c.ended_at == None, mission_stats.c.ended_at == None),  # 종료기한(Mission.ended_at)이 없는 미션은 단순히 중도포기 여부만 체크한다.
                else_=case(
                    (missions.c.ended_at <= func.now(), mission_stats.c.ended_at >= missions.c.ended_at),
                    # 종료 시점이 현재보다 과거라면 종료된 미션. Mission 종료 시점과 유저의 해당 미션 종료 시점(MissionStat)을 비교한다.
                    else_=mission_stats.c.ended_at == None  # 종료되지 않은 미션은 단순히 중도포기 여부만 체크한다.
                )
            ),
            users.c.deleted_at == None
        ).limit(1)

        return True if self.session.execute(sql).scalar() else False
