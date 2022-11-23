from adapter.orm import brands, follows, missions, mission_categories, outside_products, products
from domain.feed import Feed, FeedCheck, FeedComment, FeedImage, FeedMission, FeedProduct
from domain.user import User

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
    def get_recently_most_checked_feeds(self, user_id: int) -> list:
        pass

    @abc.abstractmethod
    def get_newsfeeds(self, user_id: int, page_cursor: int, limit: int) -> list:
        pass

    @abc.abstractmethod
    def count_number_of_newsfeed(self, user_id: int) -> int:
        pass

    def get_feeds_by_user(self, user_id: int):
        pass

    @abc.abstractmethod
    def count_number_of_feed_of_user(self) -> int:
        pass

    def get_feeds_by_mission(self, mission_id: int):
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

    def get_recently_most_checked_feeds(self, user_id: int) -> list:
        """
        - feed_candidate_query: feed_candidate_query 추천 피드 id 후보를 뽑는 곳이다.
            가장 내부의 nested_query로부터 당일 발생한 모든 feed_check 데이터를 조회한다(= A).
            그리고 A 데이터를 다음 로직에 의해 정제해 추천 피드 후보군을 얻고, 그 결과를 feeds 테이블(Feed 객체)와 INNER JOIN 한다.
            (1) 내가 팔로잉하지 않는 Feed 작성자의 피드만 남긴다.
            (2) (1) 중 삭제되지 않은 피드만 남긴다.
            (3) (2) 중 숨김처리 되지 않은 피드만 최종적으로 남긴다.
        
        - sql: feed_candidate_query 나온 피드 id 후보들에 feeds 테이블을 join하여 실제 피드 데이터를 조회한다.
            단, 'feed_candidate_query.c.column'에서 c.column은 feeeds 테이블의 컬럼을 의미한다.
            이것은 sqlalchemy 문법을 준수하기 위함이다. 가독성이 다소 떨어지므로 개선의 대상이나, sqlalchemy에 조금 더 익숙해져야 할 수 있을 것 같다.
        """

        nested_query = select(
                FeedCheck.id,
                FeedCheck.feed_id
            ).where(
                and_(
                    func.TIMESTAMPDIFF(text("DAY"), FeedCheck.created_at, func.now()) == 0,
                    FeedCheck.created_at >= func.DATE(func.now()),
                    FeedCheck.deleted_at == None
                )
            ).order_by(desc(FeedCheck.id)).alias("t")

        feed_candidate_query = select(
            Feed
        ).select_from(
            nested_query
        ).join(
            Feed, Feed.id == text("t.feed_id")  # FeedCheck.feed_id
        ).where(
            and_(
                Feed.user_id.not_in(select(follows.c.target_id).where(follows.c.user_id == user_id)),
                Feed.deleted_at == None,
                Feed.is_hidden == 0
            )
        ).group_by(
            text("t.feed_id")
        ).order_by(
            desc(func.count(text("t.id"))),
            desc(text("t.feed_id"))
        ).limit(10)

        sql = select(
            feed_candidate_query.c.id,
            func.date_format(feed_candidate_query.c.created_at, '%Y/%m/%d %H:%i:%s').label('created_at'),
            feed_candidate_query.c.content.label('body'),
            select(func.json_arrayagg(
                func.json_object(
                    "order", FeedImage.order,
                    "mimeType", FeedImage.type,
                    "pathname", FeedImage.image,
                    "resized", func.json_array()
                )
            )).select_from(FeedImage).where(FeedImage.feed_id == feed_candidate_query.c.id).label("images"),
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
                "followers", text(f"(SELECT COUNT(*) FROM follows f2 WHERE f2.target_id = {feed_candidate_query.c.user_id})"),
                "area", text("(SELECT a.name FROM areas a WHERE a.code = CONCAT(SUBSTRING(users.area_code, 1, 5), '00000') LIMIT 1)")
            ).label("user_additional_information"),
            func.ifnull(
                text(f"(SELECT cu1.is_block FROM chat_users cu1, chat_users cu2 WHERE cu1.chat_room_id = cu2.chat_room_id AND cu1.user_id={user_id} AND cu2.user_id=users.id AND cu1.deleted_at IS NULL)"),
                0
            ).label("is_chat_blocked"),
            User.gender,
            case(
                (text(f"(SELECT COUNT(*) FROM feed_likes WHERE feed_id = {feed_candidate_query.c.id} AND user_id = {user_id} AND deleted_at IS NULL) > 0"), 1),
                else_=0
            ).label('checked'),
            func.json_object(
                "comments_count", text(f"(SELECT COUNT(*) FROM feed_comments WHERE feed_id = {feed_candidate_query.c.id} AND deleted_at IS NULL)"),
                "checks_count", text(f"(SELECT COUNT(*) FROM feed_likes WHERE feed_id = {feed_candidate_query.c.id} AND deleted_at IS NULL)"),
            ).label("feed_additional_information"),
            func.json_arrayagg(
                func.json_object(
                    "id", missions.c.id,
                    "title", missions.c.title,
                    "emoji", select(mission_categories.c.emoji).where(mission_categories.c.id == missions.c.mission_category_id),
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
                "brand", func.IF(FeedProduct.type == 'inside', select(brands.c.name_ko).where(brands.c.id == products.c.brand_id), outside_products.c.brand),
                "title", func.IF(FeedProduct.type == 'inside', products.c.name_ko, outside_products.c.title),
                "image", func.IF(FeedProduct.type == 'inside', products.c.thumbnail_image, outside_products.c.image),
                "url", func.IF(FeedProduct.type == 'inside', None, outside_products.c.url),
                "price", func.IF(FeedProduct.type == 'inside', products.c.price, outside_products.c.price),
            ).label('product'),
        ).select_from(
            feed_candidate_query
        ).join(
            User, User.id == feed_candidate_query.c.user_id
        ).join(
            FeedMission, FeedMission.feed_id == feed_candidate_query.c.id, isouter=True
        ).join(
            missions, missions.c.id == FeedMission.mission_id, isouter=True
        ).join(
            FeedProduct, FeedProduct.feed_id == feed_candidate_query.c.id, isouter=True
        ).join(
            products, products.c.id == FeedProduct.product_id, isouter=True
        ).join(
            outside_products, outside_products.c.id == FeedProduct.outside_product_id, isouter=True
        ).group_by(
            feed_candidate_query.c.id
        ).order_by(desc(feed_candidate_query.c.id))

        result = self.session.execute(sql)
        return result

    def get_newsfeeds(self, user_id: int, page_cursor: int, limit: int) -> list:
        sql = select(
            Feed.id,
            func.date_format(Feed.created_at, '%Y/%m/%d %H:%i:%s').label('created_at'),
            Feed.content.label('body'),
            select(func.json_arrayagg(
                func.json_object(
                    "order", FeedImage.order,
                    "mimeType", FeedImage.type,
                    "pathname", FeedImage.image,
                    "resized", func.json_array()
                )
            )).select_from(FeedImage).where(FeedImage.feed_id == Feed.id).label("images"),
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
                    "emoji", select(mission_categories.c.emoji).where(mission_categories.c.id == missions.c.mission_category_id),
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
                "brand", func.IF(FeedProduct.type == 'inside', select(brands.c.name_ko).where(brands.c.id == products.c.brand_id), outside_products.c.brand),
                "title", func.IF(FeedProduct.type == 'inside', products.c.name_ko, outside_products.c.title),
                "image", func.IF(FeedProduct.type == 'inside', products.c.thumbnail_image, outside_products.c.image),
                "url", func.IF(FeedProduct.type == 'inside', None, outside_products.c.url),
                "price", func.IF(FeedProduct.type == 'inside', products.c.price, outside_products.c.price),
            ).label('product'),
            func.concat(func.lpad(Feed.id, 15, '0')).label('cursor'),
        ).join(
            User, User.id == Feed.user_id
        ).join(
            FeedMission, FeedMission.feed_id == Feed.id, isouter=True
        ).join(
            missions, missions.c.id == FeedMission.mission_id, isouter=True
        ).join(
            FeedProduct, FeedProduct.feed_id == Feed.id, isouter=True
        ).join(
            products, products.c.id == FeedProduct.product_id, isouter=True
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
                Feed.id < page_cursor,
            )
        ).group_by(
            Feed.id
        ).order_by(desc(Feed.id)).limit(limit)

        result = self.session.execute(sql)
        return result

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

    def get_feeds_by_user(self, user_id: int):
        pass

    def count_number_of_feed_of_user(self) -> int:
        pass

    def get_feeds_by_mission(self, mission_id: int):
        pass

    def count_number_of_feed_of_mission(self) -> int:
        pass

    def update(self, feed: Feed) -> Feed:
        pass

    def delete(self, feed: Feed) -> Feed:
        pass
