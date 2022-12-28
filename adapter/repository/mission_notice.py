from domain.mission import MissionNotice, MissionNoticeImage

import abc
from sqlalchemy import select, delete, insert, update, join, desc, and_, case, func, text


class AbstractMissionNoticeRepository(abc.ABC):
    @abc.abstractmethod
    def get_list(self,  mission_id: int, page_cursor: int, limit: int) -> list:
        pass

    @abc.abstractmethod
    def count_number_of_notice(self, mission_id: int) -> int:
        pass


class MissionNoticeRepository(AbstractMissionNoticeRepository):
    def __init__(self, session):
        self.session = session

    def get_list(self, mission_id: int, page_cursor: int, limit: int) -> list:
        sql = select(
            MissionNotice.id,
            func.date_format(MissionNotice.created_at, '%Y/%m/%d %H:%i:%s').label('created_at'),
            MissionNotice.title,
            MissionNotice.body,
            func.json_arrayagg(
                func.json_object(
                    "id", MissionNoticeImage.id,
                    "order", MissionNoticeImage.order,
                    "type", MissionNoticeImage.type,
                    "pathname", MissionNoticeImage.image
                )
            ).label('images'),
            func.concat(func.lpad(MissionNotice.id, 15, '0')).label('cursor'),
        ).join(
            MissionNoticeImage, MissionNoticeImage.mission_notice_id == MissionNotice.id
        ).where(
            MissionNotice.mission_id == mission_id,
            MissionNotice.deleted_at == None,
            MissionNotice.id < page_cursor
        ).group_by(
            MissionNotice.id,
        ).order_by(
            desc(MissionNotice.id),
        ).limit(limit)

        result = self.session.execute(sql).all()
        return result

    def count_number_of_notice(self, mission_id: int) -> int:
        sql = select(
            func.count(MissionNotice.id)
        ).where(
            MissionNotice.mission_id == mission_id,
            MissionNotice.deleted_at == None,
        )
        total_count = self.session.execute(sql).scalar()
        return total_count
