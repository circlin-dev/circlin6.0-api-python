from domain.mission import MissionComment
from domain.user import User
import abc
from sqlalchemy import select, delete, insert, update, join, desc, and_, case, func, text


class AbstractMissionCommentRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, new_comment: MissionComment) -> int:
        pass

    @abc.abstractmethod
    def get_list(self,  mission_id: int, page_cursor: int, limit: int, user_id: int) -> list:
        pass

    @abc.abstractmethod
    def update(self, comment: MissionComment):
        pass

    @abc.abstractmethod
    def delete(self, comment: MissionComment):
        pass

    @abc.abstractmethod
    def count_number_of_comment(self, mission_id: int) -> int:
        pass

    @abc.abstractmethod
    def get_maximum_comment_group_value(self, mission_id: int) -> int or None:
        pass

    @abc.abstractmethod
    def get_users_who_belonged_to_same_comment_group(self, mission_id: int, group: int) -> int or None:
        pass


class MissionCommentRepository(AbstractMissionCommentRepository):
    def __init__(self, session):
        self.session = session

    def add(self, new_comment: MissionComment) -> int:
        sql = insert(
            MissionComment
        ).values(
            mission_id=new_comment.mission_id,
            user_id=new_comment.user_id,
            group=new_comment.group,
            depth=new_comment.depth,
            comment=new_comment.comment
        )
        result = self.session.execute(sql)  # =====> inserted row의 id값을 반환해야 한다.

        return result.inserted_primary_key[0]

    def get_list(self, mission_id: int, page_cursor: int, limit: int, user_id: int) -> list:
        sql = select(
            MissionComment.id,
            func.date_format(MissionComment.created_at, '%Y/%m/%d %H:%i:%s').label('created_at'),
            MissionComment.group,
            MissionComment.depth,
            MissionComment.comment,
            MissionComment.user_id,
            case(
                (text(f"mission_comments.user_id IN (SELECT target_id FROM blocks WHERE user_id = {user_id})"), 1),
                else_=0
            ).label('is_blocked'),
            User.nickname,
            User.gender,
            User.profile_image,
            func.concat(func.lpad(MissionComment.group, 15, '0')).label('cursor')
        ).select_from(
            MissionComment
        ).join(
            User, MissionComment.user_id == User.id
        ).where(
            and_(
                MissionComment.mission_id == mission_id,
                MissionComment.deleted_at == None,
                MissionComment.group < page_cursor
            )
        ).order_by(desc(MissionComment.group), MissionComment.depth, MissionComment.created_at).limit(limit)
        result = self.session.execute(sql)
        return result

    def update(self, comment: MissionComment):
        sql = update(MissionComment).where(MissionComment.id == comment.id).values(comment=comment.comment)
        return self.session.execute(sql)

    def delete(self, comment: MissionComment):
        sql = update(MissionComment).where(MissionComment.id == comment.id).values(deleted_at=func.now())
        return self.session.execute(sql)

    def count_number_of_comment(self, mission_id: int) -> int:
        sql = select(
            func.count(MissionComment.id)
        ).where(
            and_(
                MissionComment.mission_id == mission_id,
                MissionComment.deleted_at == None
            )
        )
        total_count = self.session.execute(sql).scalar()
        return total_count

    def get_maximum_comment_group_value(self, mission_id: int) -> int or None:
        sql = select(
            func.max(MissionComment.group).label('max_group')
        ).where(
            and_(
                MissionComment.mission_id == mission_id,
                MissionComment.deleted_at == None
            )
        )
        maximum_comment_group_value: [int, None] = self.session.execute(sql).scalar()
        return maximum_comment_group_value

    def get_users_who_belonged_to_same_comment_group(self, mission_id: int, group: int) -> list:
        sql = select(
            MissionComment.user_id
        ).where(
            and_(
                MissionComment.mission_id == mission_id,
                MissionComment.group == group
            )
        )
        commented_users: list = self.session.execute(sql).scalars().all()
        return commented_users
