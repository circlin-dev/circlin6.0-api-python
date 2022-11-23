from adapter.orm import brands, follows, missions, outside_products, products
from domain.brand import Brand
from domain.feed import Feed, FeedCheck, FeedComment, FeedImage, FeedMission, FeedProduct
from domain.user import Follow, User
from domain.mission import Mission, MissionCategory
from domain.product import OutsideProduct, Product

import abc
from sqlalchemy import select, delete, insert, update, join, desc, and_, case, func, text


class AbstractFeedRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, new_feed: Feed) -> int:
        pass

    @abc.abstractmethod
    def get_one(self, feed_id: int) -> Feed:
        pass

    @abc.abstractmethod
    def get_newsfeeds(self, user_id: int, page_cursor: int, limit: int) -> list:
        pass

    @abc.abstractmethod
    def get_recently_most_checked_feeds(self, user_id: int, page_cursor: int, limit: int) -> list:
        pass

    @abc.abstractmethod
    def count_number_of_newsfeed(self) -> int:
        pass

    @abc.abstractmethod
    def count_number_of_feed_of_user(self) -> int:
        pass

    @abc.abstractmethod
    def count_number_of_feed_of_mission(self) -> int:
        pass

    @abc.abstractmethod
    def update(self, feed: Feed) -> Feed:
        pass

    @abc.abstractmethod
    def delete(self, feed: Feed) -> Feed:
        pass


class FeedRepository(AbstractFeedRepository):
    def __init__(self, session):
        self.session = session

    def add(self, new_feed: Feed) -> int:
        pass

    def get_one(self, feed_id: int) -> Feed:
        pass

    def get_newsfeeds(self, user_id: int, page_cursor: int, limit: int) -> list:
        sql = select(
            Feed.id,
            func.date_format(Feed.created_at, '%Y/%m/%d %H:%i:%s').label('created_at'),
            Feed.content.label('body'),
            func.json_arrayagg(
                func.json_object(
                    "order", FeedImage.order,
                    "mimeType", FeedImage.type,
                    "pathname", FeedImage.image,
                    "resized", func.json_array()
                )
            ).label('images'),
            User.id.label('user_id'),
            User.nickname,
            User.profile_image,
            case(
                (text(f"users.id IN (SELECT f1.target_id FROM follows f1 WHERE f1.user_id={user_id})"), 1),
                else_=0
            ).label("followed"),
            case(
                (text(f"users.id IN (SELECT b1.target_id FROM blocks b1 WHERE b1.user_id={user_id})"), 1),
                else_=0
            ).label("is_blocked"),
            func.json_object(
                "followers", text("(SELECT COUNT(*) FROM follows f2 WHERE f2.target_id = feeds.user_id)"),
                "area", text("(SELECT a.name FROM areas a WHERE a.code = CONCAT(SUBSTRING(users.area_code, 1, 5), '00000') LIMIT 1)")
            ).label("user_additional_information"),
            func.ifnull(
                text(f"(SELECT cu1.is_block FROM chat_users cu1, chat_users cu2 WHERE cu1.chat_room_id = cu2.chat_room_id AND cu1.user_id={user_id} AND cu2.user_id=users.id AND cu1.deleted_at IS NULL)"),
                0
            ).label("is_chat_blocked"),
            User.gender,
            case(
                (text(f"(SELECT COUNT(*) FROM feed_likes WHERE feed_id = feeds.id AND user_id = {user_id} AND deleted_at IS NULL) > 0"), 1),
                else_=0
            ).label('checked'),
            func.json_object(
                "comments_count", text("(SELECT COUNT(*) FROM feed_comments WHERE feed_id = feeds.id AND deleted_at IS NULL)"),
                "checks_count", text("(SELECT COUNT(*) FROM feed_likes WHERE feed_id = feeds.id AND deleted_at IS NULL)"),
            ).label("feed_additional_information"),
            func.json_arrayagg(
                func.json_object(
                    "id", missions.c.id,
                    "title", missions.c.title,
                    "emoji", text(f"(SELECT mc.emoji FROM mission_categories mc WHERE mc.id = missions.mission_category_id)"),
                    "is_ground", missions.c.is_ground,
                    "is_event", missions.c.is_event,
                    "is_old_event", case(
                        (and_(missions.c.id <= 1749, missions.c.is_event == 1), 1),
                        else_=0
                    ),
                    "event_type", missions.c.event_type,
                    "thumbnail", missions.c.thumbnail_image,
                    "bookmarked", case(
                        (text(f"(SELECT COUNT(*) FROM mission_stats WHERE mission_id = missions.id AND user_id = {user_id} AND ended_at IS NULL) > 0"), 1),
                        else_=0
                    )
                )
            ).label('mission'),
            func.json_object(
                "type", FeedProduct.type,
                "id", FeedProduct.id,
                "brand", func.IF(FeedProduct.type == 'inside', brands.c.name_ko, outside_products.c.brand),
                "title", func.IF(FeedProduct.type == 'inside', products.c.name_ko, outside_products.c.title),
                "image", func.IF(FeedProduct.type == 'inside', products.c.thumbnail_image, outside_products.c.image),
                "url", func.IF(FeedProduct.type == 'inside', None, outside_products.c.url),
                "price", func.IF(FeedProduct.type == 'inside', products.c.price, outside_products.c.price),
            ).label('product'),
            func.concat(func.lpad(Feed.id, 15, '0')).label('cursor'),
        ).join(
            User, User.id == Feed.user_id
        ).join(
            FeedImage, FeedImage.feed_id == Feed.id
        ).join(
            FeedMission, FeedMission.feed_id == Feed.id, isouter=True
        ).join(
            missions, missions.c.id == FeedMission.mission_id, isouter=True
        ).join(
            FeedProduct, FeedProduct.feed_id == Feed.id, isouter=True
        ).join(
            products, products.c.id == FeedProduct.product_id, isouter=True
        ).join(
            brands, brands.c.id == products.c.brand_id, isouter=True
        ).join(
            outside_products, outside_products.c.id == FeedProduct.outside_product_id, isouter=True
        ).where(
            and_(
                select(
                    follows.c.target_id
                ).where(
                    and_(
                        follows.c.user_id == user_id,
                        follows.c.target_id == Feed.user_id,
                    )
                ).exists(),
                func.abs(func.TIMESTAMPDIFF(text("DAY"), Feed.created_at, func.now())) <= 1,
                Feed.deleted_at == None,
                Feed.is_hidden == 0,
                Feed.id < page_cursor
            )
        ).group_by(
            Feed.id
        ).order_by(desc(Feed.id)).limit(limit)

        result = self.session.execute(sql)
        return result

    def get_recently_most_checked_feeds(self, user_id: int, page_cursor: int, limit: int) -> list:
        pass

    def count_number_of_newsfeed(self, user_id: int) -> int:
        sql = select(
            func.count(Feed.id)
        ).where(
            and_(
                select(
                    follows.c.target_id
                ).where(
                    and_(
                        follows.c.user_id == user_id,
                        follows.c.target_id == Feed.user_id,
                    )
                ).exists(),
                func.abs(func.TIMESTAMPDIFF(text("DAY"), Feed.created_at, func.now())) <= 1,
                Feed.deleted_at == None,
                Feed.is_hidden == 0,
            )
        )
        total_count = self.session.execute(sql).scalar()
        return total_count

    def count_number_of_feed_of_user(self) -> int:
        pass

    def count_number_of_feed_of_mission(self) -> int:
        pass

    def update(self, feed: Feed) -> Feed:
        pass

    def delete(self, feed: Feed) -> Feed:
        pass
