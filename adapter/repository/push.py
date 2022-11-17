from adapter.orm import push_histories
from domain.push import PushHistory
from sqlalchemy import select, update, delete, insert, desc, and_, case, text, func

import abc
import json


class AbstractPushHistoryRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, new_push_history: PushHistory) -> PushHistory:
        pass


class PushHistoryRepository(AbstractPushHistoryRepository):
    def __init__(self, session):
        self.session = session

    def add(self, new_push_history: PushHistory) -> PushHistory:
        sql = insert(
            push_histories
        ).values(
            target_id=new_push_history.target_id,
            device_token=new_push_history.device_token,
            title=new_push_history.title,
            message=new_push_history.message,
            type=new_push_history.type,
            result=new_push_history.result,
            json=new_push_history.json,
            result_json=new_push_history.result_json
        )

        return self.session.execute(sql)
