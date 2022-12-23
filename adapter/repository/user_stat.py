from adapter.orm import user_stats
from domain.user import User, UserStat

import abc
from sqlalchemy.sql import func
from sqlalchemy import and_, case, insert, select, text, update


class AbstractUserStatRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, user_stat: UserStat):
        pass

    @abc.abstractmethod
    def get_one(self, user_id: int):
        pass

    @abc.abstractmethod
    def update(self, user_stat: UserStat):
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
            bmi=user_stat.bmi,
            yesterday_feeds_count=0 if user_stat.yesterday_feeds_count is None else user_stat.yesterday_feeds_count
        )
        result = self.session.execute(sql)
        return result.inserted_primary_key[0]

    def get_one(self, user_id: int):
        sql = select(
            user_stats
        ).where(user_stats.c.user_id == user_id)
        result = self.session.execute(sql).first()
        return result

    def update(self, new_user_stat: UserStat):
        return self.session.query(user_stats).filter_by(user_id=new_user_stat.user_id).update(
            {
                "birthday": func.date_format(new_user_stat.birthday, '%Y-%m-%d 00:00:00'),
                "height": new_user_stat.height,
                "weight": new_user_stat.weight,
                "bmi": new_user_stat.bmi,
                "yesterday_feeds_count": new_user_stat.yesterday_feeds_count
            },
            synchronize_session="fetch"
        )
