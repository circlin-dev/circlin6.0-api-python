from adapter.orm import user_stats
from domain.user import User, UserStat

import abc
from sqlalchemy.sql import func
from sqlalchemy import and_, case, insert, select, text, update


class AbstractUserStatRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, user_stat: UserStat):
        pass


class UserStatRepository(AbstractUserStatRepository):
    def __init__(self, session):
        self.session = session

    def add(self, user_stat: UserStat):
        sql = insert(
            user_stats
        ).values(
            user_id=user_stat.user_id,
            birthday=user_stat.birthday,
            height=user_stat.height,
            weight=user_stat.weight,
            bmi=user_stat.bmi
        )
        result = self.session.execute(sql)
        return result.inserted_primary_key[0]