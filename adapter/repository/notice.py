from adapter.orm import notice_images
from domain.notice import Notice, NoticeImage
from domain.user import User
import abc
from sqlalchemy import select, delete, insert, update, join, desc, and_, case, func, text


class AbstractNoticeRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, new_notice: Notice) -> int:
        pass

    @abc.abstractmethod
    def get_one(self, notice_id: int) -> Notice:
        pass

    @abc.abstractmethod
    def get_list(self,  page_cursor: int, limit: int) -> list:
        pass

    @abc.abstractmethod
    def count_number_of_notice(self) -> int:
        pass

    @abc.abstractmethod
    def update(self, notice: Notice):
        pass

    @abc.abstractmethod
    def delete(self, notice: Notice):
        pass


class NoticeRepository(AbstractNoticeRepository):
    def __init__(self, session):
        self.session = session

    def add(self, new_notice: Notice) -> int:
        sql = insert(
            Notice
        ).values(

        )
        result = self.session.execute(sql)  # =====> inserted row의 id값을 반환해야 한다.

        return result.inserted_primary_key[0]

    def get_one(self, notice_id: int) -> Notice:
        sql = select(
            Notice.id,
            func.date_format(Notice.created_at, '%Y/%m/%d %H:%i:%s').label('created_at'),
            Notice.title,
            Notice.content,
            Notice.link_text,
            Notice.link_url,
            Notice.is_show,
            Notice.deleted_at,
            case(
                (func.TIMESTAMPDIFF(text("DAY"), func.DATE(Notice.created_at), func.now()) <= 7, 1),
                else_=0
            ).label("is_recent"),
            func.json_arrayagg(
                func.json_object(
                    "order", notice_images.c.order,
                    "type", notice_images.c.type,
                    "image", notice_images.c.image
                )
            ).label("images")
        ).join(
            notice_images, notice_images.c.notice_id == Notice.id, isouter=True
        ).where(
            and_(
                Notice.id == notice_id,
                Notice.deleted_at == None,
                Notice.is_show == 1
            )
        ).group_by(Notice.id)

        notice = self.session.execute(sql).first()
        return notice

    def get_list(self, page_cursor: int, limit: int) -> list:
        # latest_date = date('Y-m-d', time() - (86400 * 7));
        sql = select(
            Notice.id,
            func.date_format(Notice.created_at, '%Y/%m/%d %H:%i:%s').label('created_at'),
            Notice.title,
            case(
                (func.TIMESTAMPDIFF(text("DAY"), func.DATE(Notice.created_at), func.now()) <= 7, 1),
                else_=0
            ).label("is_recent"),
            func.concat(func.lpad(Notice.id, 15, '0')).label('cursor'),
        ).where(
            and_(
                Notice.deleted_at == None,
                Notice.is_show == 1,
                Notice.id < page_cursor
            )
        ).order_by(desc(Notice.id)).limit(limit)
        result = self.session.execute(sql)
        return result

    def count_number_of_notice(self) -> int:
        sql = select(
            func.count(Notice.id)
        ).where(
            and_(
                Notice.deleted_at == None,
                Notice.is_show == 1,
            )
        )
        total_count = self.session.execute(sql).scalar()
        return total_count

    def update(self, notice: Notice):
        sql = update(Notice).where(Notice.id == notice.id).values()
        return self.session.execute(sql)

    def delete(self, notice: Notice):
        sql = update(Notice).where(Notice.id == notice.id).values(deleted_at=func.now())
        return self.session.execute(sql)
