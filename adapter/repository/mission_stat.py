from adapter.orm import mission_stats
from domain.mission import MissionStat

import abc
from sqlalchemy import and_, exists, select


class AbstractMissionStatRepository(abc.ABC):
    @abc.abstractmethod
    def get_one_excluding_ended(self, user_id: int, mission_id: int) -> int:
        pass


class MissionStatRepository(AbstractMissionStatRepository):
    def __init__(self, session):
        self.session = session

    def get_one_excluding_ended(self, user_id: int, mission_id: int) -> int:
        sql = select(exists(
            select(
                mission_stats
            ).where(
                and_(
                    mission_stats.c.mission_id == mission_id,
                    mission_stats.c.user_id == user_id,
                    mission_stats.c.ended_at == None
                )
            ).limit(1)
        ))

        return self.session.execute(sql).scalar()
