from adapter.orm import follows, mission_playgrounds, users
from domain.mission import MissionRank, MissionRankUser
from domain.user import User

import abc
from sqlalchemy import and_, case, desc, exists, func, select


class AbstractMissionRankRepository(abc.ABC):
    @abc.abstractmethod
    def get_latest_rank_id(self, mission_id: int):
        pass

    @abc.abstractmethod
    def get_list(self, mission_rank_id: int, page_cursor: int, limit: int) -> list:
        pass

    @abc.abstractmethod
    def count_number_of_rank(self, mission_rank_id: int):
        pass

    @abc.abstractmethod
    def get_my_rank(self, mission_rank_id: int, user_id: int):
        pass

    @abc.abstractmethod
    def get_rank_scale(self, mission_id: int):
        pass


class MissionRankRepository(AbstractMissionRankRepository):
    def __init__(self, session):
        self.session = session

    def get_latest_rank_id(self, mission_id: int):
        latest_mission_rank = select(
            func.max(MissionRank.id)
        ).where(
            MissionRank.mission_id == mission_id
        ).order_by(
            desc(MissionRank.id)
        ).limit(1)
        return self.session.execute(latest_mission_rank).scalar()

    def get_list(self, mission_rank_id: int, page_cursor: int, limit: int) -> list:
        follower_count = select(func.count(follows.c.id)).where(follows.c.target_id == users.c.id)
        sql = select(
            users.c.id.label('user_id'),
            users.c.nickname,
            users.c.gender,
            users.c.profile_image,
            MissionRankUser.rank,
            MissionRankUser.feeds_count,
            MissionRankUser.summation,
            follower_count.label('followers'),
            func.concat(func.lpad(MissionRankUser.rank, 15, '0')).label('cursor'),
        ).join(
            users, MissionRankUser.user_id == users.c.id
        ).where(
            and_(
                MissionRankUser.mission_rank_id == mission_rank_id,
                MissionRankUser.rank <= 100,
                users.c.deleted_at == None,
                MissionRankUser.rank > page_cursor
            )
        ).order_by(
            MissionRankUser.rank
        ).limit(limit)

        result = self.session.execute(sql).all()
        return result

    def count_number_of_rank(self, mission_rank_id: int):
        sql = select(
            func.count(MissionRankUser.id)
        ).join(
            users, MissionRankUser.user_id == users.c.id
        ).where(
            and_(
                MissionRankUser.mission_rank_id == mission_rank_id,
                MissionRankUser.rank <= 100,
                users.c.deleted_at == None,
            )
        )
        return self.session.execute(sql).scalar()

    def get_my_rank(self, mission_rank_id: int, user_id: int):
        follower_count = select(func.count(follows.c.id)).where(follows.c.target_id == users.c.id)
        sql = select(
            users.c.id.label('user_id'),
            users.c.nickname,
            users.c.gender,
            users.c.profile_image,
            MissionRankUser.rank,
            MissionRankUser.feeds_count,
            MissionRankUser.summation,
            # select(mission_playgrounds.c.rank_scale).where(mission_playgrounds.c.mission_id == mission_id).label("scale"),
            follower_count.label('followers'),
        ).join(
            users, MissionRankUser.user_id == users.c.id
        ).where(
            and_(
                MissionRankUser.mission_rank_id == mission_rank_id,
                # MissionRankUser.user_id == user_id,
                users.c.id == user_id,
                users.c.deleted_at == None,
            )
        ).order_by(
            MissionRankUser.rank
        )

        result = self.session.execute(sql).first()
        return result

    def get_rank_scale(self, mission_id: int):
        sql = select(mission_playgrounds.c.rank_scale).where(mission_playgrounds.c.mission_id == mission_id)
        return self.session.execute(sql).first()
