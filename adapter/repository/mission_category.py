import abc
from domain.mission import MissionCategory
from domain.user import UserFavoriteCategory
from sqlalchemy import select, delete, insert, join, desc, and_, case


class AbstractMissionCategoryRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, new_mission_category) -> MissionCategory:
        pass

    @abc.abstractmethod
    def get_list(self) -> MissionCategory:
        pass

    @abc.abstractmethod
    def delete(self, mission_category) -> MissionCategory:
        pass


class MissionCategoryRepository(AbstractMissionCategoryRepository):
    def __init__(self, session):
        self.session = session

    def add(self, new_mission_category):
        sql = insert(
            new_mission_category
        ).values(
            mission_category_id=new_mission_category.mission_category_id,
            title=new_mission_category.title,
            emoji=new_mission_category.emoji,
            description=new_mission_category.description
        )
        self.session.execute(sql)

    def get_list(self):
        # sql = select(
        #     MissionCategory.id,
        #     MissionCategory.title.label('name'),
        # ).where(
        #     and_(
        #         MissionCategory.id != 0,
        #         MissionCategory.mission_category_id != None
        #     )
        # ).order_by(
        #     desc(MissionCategory.id)
        # )
        # result = self.session.execute(sql)  # version2.x 스타일!
        # for data in result:
        #     print('id: ', data.id)
        #     print('name: ', data.name)
        # return result

        sql = select(
            MissionCategory
        ).where(
            and_(
                MissionCategory.id != 0,
                MissionCategory.mission_category_id != None
            )
        ).order_by(
            desc(MissionCategory.id)
        )
        result = self.session.execute(sql).scalars().all()   # version2.x 스타일!
        return result

    def delete(self, mission_category):
        sql = delete(
            MissionCategory
        ).where(
            MissionCategory.id == mission_category.id
        )
        self.session.execute(sql)
