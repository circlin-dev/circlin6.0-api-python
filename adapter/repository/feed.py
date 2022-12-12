from adapter.orm import areas, brands, feed_comments, feed_images, feed_likes, food_brands, food_images, follows, foods, missions, mission_categories, outside_products, products, users
from domain.feed import Feed, FeedCheck, FeedComment, FeedFood, FeedImage, FeedMission, FeedProduct
from domain.user import User
from helper.cache import cache
from helper.constant import INITIAL_DESCENDING_PAGE_CURSOR, INITIAL_ASCENDING_PAGE_CURSOR

import abc
from sqlalchemy import select, delete, insert, update, join, desc, and_, case, func, text
from sqlalchemy.orm import aliased


class AbstractFeedRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, new_feed: Feed) -> int:
        pass

    @abc.abstractmethod
    def get_one(self, feed_id: int, user_id: int) -> Feed:
        pass

    @abc.abstractmethod
    def get_recently_most_checked_feeds(self, user_id: int) -> list:
        pass

    @abc.abstractmethod
    def get_newsfeeds(self, user_id: int, page_cursor: int, limit: int) -> list:
        pass

    @abc.abstractmethod
    def count_number_of_newsfeed(self, user_id: int, page_cursor: int) -> int:
        pass

    @abc.abstractmethod
    def get_checked_feeds_by_user(self, user_id: int, page_cursor: int, limit: int):
        pass

    @abc.abstractmethod
    def count_number_of_checked_feed_of_user(self, user_id: int):
        pass

    @abc.abstractmethod
    def get_feeds_by_user(self, user_id: int, page_cursor: int, limit: int) -> list:
        pass

    @abc.abstractmethod
    def count_number_of_feed_of_user(self, user_id: int) -> int:
        pass

    @abc.abstractmethod
    def get_feeds_by_mission(self, mission_id: int, user_id: int, page_cursor: int, limit: int) -> list:
        pass

    @abc.abstractmethod
    def count_number_of_feed_of_mission(self, mission_id: int) -> int:
        pass

    @abc.abstractmethod
    def get_simple_one(self, feed_id: int) -> Feed:
        pass

    @abc.abstractmethod
    def update(self, feed: Feed):
        pass

    @abc.abstractmethod
    def delete(self, feed: Feed):
        pass


class FeedRepository(AbstractFeedRepository):
    def __init__(self, session):
        self.session = session

    def add(self, new_feed: Feed) -> int:
        pass

    def get_one(self, feed_id: int, user_id: int) -> Feed:
        sql = select(
            Feed.id,
            func.date_format(Feed.created_at, '%Y/%m/%d %H:%i:%s').label('created_at'),
            Feed.content.label('body'),
            select(func.json_arrayagg(
                func.json_object(
                    "order", feed_images.c.order,
                    "mimeType", feed_images.c.type,
                    "pathname", feed_images.c.image,
                    "resized", func.json_array()
                )
            )).select_from(feed_images).where(feed_images.c.feed_id == Feed.id).label("images"),
            Feed.is_hidden,
            Feed.distance,
            Feed.laptime,
            Feed.distance_origin,
            Feed.laptime_origin,
            func.date_format(Feed.deleted_at, '%Y/%m/%d %H:%i:%s').label('deleted_at'),
            case(
                (text(f"(SELECT COUNT(*) FROM feed_likes WHERE feed_id = feeds.id AND user_id = {user_id} AND deleted_at IS NULL) > 0"), 1),
                else_=0
            ).label('checked'),
            select(func.count(feed_comments.c.id)).where(and_(feed_comments.c.feed_id == Feed.id, feed_comments.c.deleted_at == None)).label('comments_count'),
            select(func.count(FeedCheck.id)).where(and_(FeedCheck.feed_id == Feed.id, FeedCheck.deleted_at == None)).label('checks_count'),

            User.id.label('user_id'),
            User.nickname,
            User.profile_image,
            User.gender,
            case(
                (text(f"users.id IN (SELECT f1.target_id FROM follows f1 WHERE f1.user_id={user_id})"), 1),
                else_=0
            ).label("followed"),
            case(
                (text(f"users.id IN (SELECT b1.target_id FROM blocks b1 WHERE b1.user_id={user_id})"), 1),
                else_=0
            ).label("is_blocked"),
            func.ifnull(
                case(
                    (user_id == User.id, None),  # user_id == User.id 일 때 아래 서브쿼리에서 에러 발생(Error: Subquery returns more than 1 rows)
                    else_=text(f"(SELECT cu1.is_block FROM chat_users cu1, chat_users cu2 WHERE cu1.chat_room_id = cu2.chat_room_id AND cu1.user_id={user_id} AND cu2.user_id=users.id AND cu1.deleted_at IS NULL)")
                ),
                0
            ).label("is_chat_blocked"),
            select(func.count(follows.c.id)).where(follows.c.target_id == User.id).label('followers'),
            select(areas.c.name).where(areas.c.code == func.concat(func.substring(User.area_code, 1, 5), '00000')).limit(1).label('area'),

            func.json_arrayagg(
                func.json_object(
                    "id", missions.c.id,
                    "title", missions.c.title,
                    "emoji", select(mission_categories.c.emoji).where(
                        mission_categories.c.id == missions.c.mission_category_id),
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

            func.json_object(
                "id", foods.c.id,
                "largeCategoryTitle", foods.c.large_category_title,
                "title", foods.c.title,
                "brand", food_brands.c.title,
                "images", select(func.json_arrayagg(
                    func.json_object(
                        "width", food_images.c.width,
                        "height", food_images.c.height,
                        "type", food_images.c.type,
                        "mimeType", food_images.c.mime_type,
                        "pathname", food_images.c.path,
                        "resized", text(f"""(SELECT IFNULL(JSON_ARRAYAGG(JSON_OBJECT(
                        'mimeType', fi.mime_type,
                        'pathname', fi.path,
                        'width', fi.width,
                        'height', fi.height
                        )), JSON_ARRAY()) FROM food_images fi WHERE fi.original_file_id = food_images.id)""")
                    )
                )).where(and_(
                    food_images.c.food_id == foods.c.id,
                    food_images.c.original_file_id == None)),
            ).label('food'),
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
        ).join(
            FeedFood, FeedFood.feed_id == Feed.id, isouter=True
        ).join(
            foods, foods.c.id == FeedFood.food_id, isouter=True
        ).join(
            food_brands, foods.c.brand_id == food_brands.c.id, isouter=True
        ).where(
            and_(
                Feed.id == feed_id,
                Feed.deleted_at == None,
            )
        )

        result = self.session.execute(sql).first()
        return result

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
        followings = select(follows.c.target_id).where(follows.c.user_id == user_id)

        nested_query = select(
            FeedCheck.id,
            FeedCheck.feed_id
        ).where(
            and_(
                func.TIMESTAMPDIFF(text("DAY"), FeedCheck.created_at, func.now()) == 0,
                FeedCheck.created_at >= func.DATE(func.now()),
                FeedCheck.deleted_at == None
            )
        ).group_by(FeedCheck.feed_id).order_by(desc(FeedCheck.id)).alias("t")

        feed_candidate_query = select(
            Feed
        ).select_from(
            nested_query
        ).join(
            Feed, Feed.id == text("t.feed_id")  # FeedCheck.feed_id
        ).where(
            and_(
                Feed.user_id.not_in(followings),
                Feed.deleted_at == None,
                Feed.is_hidden == 0
            )
        ).group_by(
            Feed.user_id
        ).order_by(
            desc(func.count(text("t.id"))),
            Feed.user_id
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
            select(func.count(follows.c.id)).where(follows.c.target_id == User.id).label('followers'),
            select(areas.c.name).where(areas.c.code == func.concat(func.substring(User.area_code, 1, 5), '00000')).limit(1).label('area'),
            func.ifnull(
                case(
                    (user_id == User.id, None),  # user_id == User.id 일 때 아래 서브쿼리에서 에러 발생(Error: Subquery returns more than 1 rows)
                    else_=text(f"(SELECT cu1.is_block FROM chat_users cu1, chat_users cu2 WHERE cu1.chat_room_id = cu2.chat_room_id AND cu1.user_id={user_id} AND cu2.user_id=users.id AND cu1.deleted_at IS NULL)")
                ),
                0
            ).label("is_chat_blocked"),
            User.gender,
            case(
                (text(f"(SELECT COUNT(*) FROM feed_likes WHERE feed_id = {feed_candidate_query.c.id} AND user_id = {user_id} AND deleted_at IS NULL) > 0"), 1),
                else_=0
            ).label('checked'),
            select(func.count(feed_comments.c.id)).where(and_(feed_comments.c.feed_id == Feed.id, feed_comments.c.deleted_at == None)).label('comments_count'),
            select(func.count(FeedCheck.id)).where(and_(FeedCheck.feed_id == Feed.id, FeedCheck.deleted_at == None)).label('checks_count'),

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
        '''
        (1) current_number_of_following < 10 이면 newsfeed + 추천 피드를 함께 보내줘야 한다.
        이때, newsfeed와 추천피드는 쿼리가 다르므로 UNION한 후 cursor를 생성한다.
        (2) 반면, current_number_of_following >= 10 이면 newsfeed만 보낸다.
        이때, newsfeed 조회 쿼리에는 cursor를 생성하는 쿼리가 추가되어야 한다.
        이 때문에 함수 코드가 다소 길어졌다.
        :param user_id:
        :param page_cursor:
        :param limit:
        :return:
        '''
        if page_cursor == INITIAL_DESCENDING_PAGE_CURSOR:
            # first API call or refreshing
            # Clear cache first if exists.
            if cache.get("customized_sort_query") is not None:
                cache.clear()

            followings = select(follows.c.target_id).where(follows.c.user_id == user_id)
            followings_number = select(func.count(follows.c.target_id)).where(follows.c.user_id == user_id)
            current_number_of_following = self.session.execute(followings_number).scalar()

            if current_number_of_following >= 10:
                # newsfeed only
                customized_sort_query = select(
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
                    func.ifnull(
                        select(True).where(
                            and_(
                                feed_likes.c.feed_id == Feed.id,
                                feed_likes.c.user_id == user_id,
                                feed_likes.c.deleted_at == None
                            )
                        ),
                        False
                    ).label('checked'),
                    select(func.count(feed_comments.c.id)).where(
                        and_(feed_comments.c.feed_id == Feed.id, feed_comments.c.deleted_at == None)).label(
                        'comments_count'),
                    select(func.count(FeedCheck.id)).where(
                        and_(FeedCheck.feed_id == Feed.id, FeedCheck.deleted_at == None)).label('checks_count'),

                    User.id.label('user_id'),
                    User.nickname,
                    User.profile_image,
                    User.gender,
                    case(
                        (text(f"users.id IN (SELECT f1.target_id FROM follows f1 WHERE f1.user_id={user_id})"), 1),
                        else_=0
                    ).label("followed"),
                    case(
                        (text(f"users.id IN (SELECT b1.target_id FROM blocks b1 WHERE b1.user_id={user_id})"), 1),
                        else_=0
                    ).label("is_blocked"),
                    func.ifnull(
                        case(
                            (user_id == User.id, None),  # user_id == User.id 일 때 아래 서브쿼리에서 에러 발생(Error: Subquery returns more than 1 rows)
                            else_=text(
                                f"(SELECT cu1.is_block FROM chat_users cu1, chat_users cu2 WHERE cu1.chat_room_id = cu2.chat_room_id AND cu1.user_id={user_id} AND cu2.user_id=users.id AND cu1.deleted_at IS NULL)")
                        ),
                        0
                    ).label("is_chat_blocked"),
                    select(func.count(follows.c.id)).where(follows.c.target_id == User.id).label('followers'),
                    select(areas.c.name).where(
                        areas.c.code == func.concat(func.substring(User.area_code, 1, 5), '00000')).limit(1).label(
                        'area'),

                    func.json_arrayagg(
                        func.json_object(
                            "id", missions.c.id,
                            "title", missions.c.title,
                            "emoji", select(mission_categories.c.emoji).where(
                                mission_categories.c.id == missions.c.mission_category_id),
                            "is_ground", missions.c.is_ground,
                            "is_event", missions.c.is_event,
                            "is_old_event", case(
                                (and_(missions.c.id <= 1749, missions.c.is_event == 1), 1),
                                else_=0
                            ),
                            "event_type", missions.c.event_type,
                            "thumbnail", missions.c.thumbnail_image,
                            "bookmarked", case(
                                (text(
                                    f"(SELECT COUNT(*) FROM mission_stats WHERE mission_id = missions.id AND user_id = {user_id} AND ended_at IS NULL) > 0"),
                                 1),
                                else_=0
                            )
                        )
                    ).label('mission'),

                    func.json_object(
                        "type", FeedProduct.type,
                        "id", FeedProduct.id,
                        "brand", func.IF(FeedProduct.type == 'inside',
                                         select(brands.c.name_ko).where(brands.c.id == products.c.brand_id),
                                         outside_products.c.brand),
                        "title", func.IF(FeedProduct.type == 'inside', products.c.name_ko, outside_products.c.title),
                        "image",
                        func.IF(FeedProduct.type == 'inside', products.c.thumbnail_image, outside_products.c.image),
                        "url", func.IF(FeedProduct.type == 'inside', None, outside_products.c.url),
                        "price", func.IF(FeedProduct.type == 'inside', products.c.price, outside_products.c.price),
                    ).label('product'),

                    func.row_number().over(
                        order_by=[
                            desc(func.ifnull(
                                select(True).where(
                                    and_(
                                        feed_likes.c.feed_id == Feed.id,
                                        feed_likes.c.user_id == user_id,
                                        feed_likes.c.deleted_at == None
                                    )
                                ),
                                False
                            )),
                            Feed.created_at
                        ]
                    ).label('cursor')
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
                        Feed.user_id.in_(followings),
                        func.abs(func.TIMESTAMPDIFF(text("HOUR"), Feed.created_at, func.now())) <= 24,
                        Feed.deleted_at == None,
                        Feed.is_hidden == 0,
                    )
                ).group_by(
                    Feed.id
                ).order_by(
                    'checked',
                    desc('cursor')
                )

                candidate = self.session.execute(customized_sort_query).all()
                cache.set("customized_sort_query", candidate)
            else:
                # newsfeed + recommendation
                # newsfeed
                customized_sort_query = select(
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
                    func.ifnull(
                        select(True).where(
                            and_(
                                feed_likes.c.feed_id == Feed.id,
                                feed_likes.c.user_id == user_id,
                                feed_likes.c.deleted_at == None
                            )
                        ),
                        False
                    ).label('checked'),
                    select(func.count(feed_comments.c.id)).where(
                        and_(feed_comments.c.feed_id == Feed.id, feed_comments.c.deleted_at == None)).label(
                        'comments_count'),
                    select(func.count(FeedCheck.id)).where(
                        and_(FeedCheck.feed_id == Feed.id, FeedCheck.deleted_at == None)).label('checks_count'),

                    User.id.label('user_id'),
                    User.nickname,
                    User.profile_image,
                    User.gender,
                    case(
                        (text(f"users.id IN (SELECT f1.target_id FROM follows f1 WHERE f1.user_id={user_id})"), 1),
                        else_=0
                    ).label("followed"),
                    case(
                        (text(f"users.id IN (SELECT b1.target_id FROM blocks b1 WHERE b1.user_id={user_id})"), 1),
                        else_=0
                    ).label("is_blocked"),
                    func.ifnull(
                        case(
                            (user_id == User.id, None),
                            # user_id == User.id 일 때 아래 서브쿼리에서 에러 발생(Error: Subquery returns more than 1 rows)
                            else_=text(f"(SELECT cu1.is_block FROM chat_users cu1, chat_users cu2 WHERE cu1.chat_room_id = cu2.chat_room_id AND cu1.user_id={user_id} AND cu2.user_id=users.id AND cu1.deleted_at IS NULL)")),
                        0
                    ).label("is_chat_blocked"),
                    select(func.count(follows.c.id)).where(follows.c.target_id == User.id).label('followers'),
                    select(areas.c.name).where(
                        areas.c.code == func.concat(func.substring(User.area_code, 1, 5), '00000')).limit(1).label(
                        'area'),

                    func.json_arrayagg(
                        func.json_object(
                            "id", missions.c.id,
                            "title", missions.c.title,
                            "emoji", select(mission_categories.c.emoji).where(
                                mission_categories.c.id == missions.c.mission_category_id),
                            "is_ground", missions.c.is_ground,
                            "is_event", missions.c.is_event,
                            "is_old_event", case(
                                (and_(missions.c.id <= 1749, missions.c.is_event == 1), 1),
                                else_=0
                            ),
                            "event_type", missions.c.event_type,
                            "thumbnail", missions.c.thumbnail_image,
                            "bookmarked", case(
                                (text(f"(SELECT COUNT(*) FROM mission_stats WHERE mission_id = missions.id AND user_id = {user_id} AND ended_at IS NULL) > 0"),1),
                                else_=0
                            )
                        )
                    ).label('mission'),

                    func.json_object(
                        "type", FeedProduct.type,
                        "id", FeedProduct.id,
                        "brand", func.IF(
                            FeedProduct.type == 'inside',
                            select(brands.c.name_ko).where(brands.c.id == products.c.brand_id),
                            outside_products.c.brand
                        ),
                        "title", func.IF(FeedProduct.type == 'inside', products.c.name_ko, outside_products.c.title),
                        "image",
                        func.IF(FeedProduct.type == 'inside', products.c.thumbnail_image, outside_products.c.image),
                        "url", func.IF(FeedProduct.type == 'inside', None, outside_products.c.url),
                        "price", func.IF(FeedProduct.type == 'inside', products.c.price, outside_products.c.price),
                    ).label('product'),
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
                        Feed.user_id.in_(followings),
                        func.abs(func.TIMESTAMPDIFF(text("HOUR"), Feed.created_at, func.now())) <= 24,
                        Feed.deleted_at == None,
                        Feed.is_hidden == 0,
                    )
                ).group_by(
                    Feed.id
                ).order_by(
                    'checked'
                )

                # recommendation
                nested_query = select(
                    FeedCheck.id,
                    FeedCheck.feed_id
                ).where(
                    and_(
                        func.TIMESTAMPDIFF(text("DAY"), FeedCheck.created_at, func.now()) == 0,
                        FeedCheck.created_at >= func.DATE(func.now()),
                        FeedCheck.deleted_at == None
                    )
                ).group_by(FeedCheck.feed_id).order_by(desc(FeedCheck.id)).alias("t")

                feed_candidate_query = select(
                    Feed
                ).select_from(
                    nested_query
                ).join(
                    Feed, Feed.id == text("t.feed_id")  # FeedCheck.feed_id
                ).where(
                    and_(
                        Feed.user_id.not_in(followings),
                        Feed.deleted_at == None,
                        Feed.is_hidden == 0
                    )
                ).group_by(
                    Feed.user_id
                ).order_by(
                    desc(func.count(text("t.id"))),
                    Feed.user_id
                ).limit(10)

                feed_for_recommendation = select(
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
                    func.ifnull(
                        select(True).where(
                            and_(
                                feed_likes.c.feed_id == feed_candidate_query.c.id,
                                feed_likes.c.user_id == user_id,
                                feed_likes.c.deleted_at == None
                            )
                        ),
                        False
                    ).label('checked'),
                    select(func.count(feed_comments.c.id)).where(and_(feed_comments.c.feed_id == feed_candidate_query.c.id, feed_comments.c.deleted_at == None)).label('comments_count'),
                    select(func.count(FeedCheck.id)).where(and_(FeedCheck.feed_id == feed_candidate_query.c.id, FeedCheck.deleted_at == None)).label('checks_count'),

                    User.id.label('user_id'),
                    User.nickname,
                    User.gender,
                    User.profile_image,
                    case(
                        (text(f"users.id IN (SELECT f1.target_id FROM follows f1 WHERE f1.user_id={user_id})"), 1),
                        else_=0
                    ).label("followed"),
                    case(
                        (text(f"users.id IN (SELECT b1.target_id FROM blocks b1 WHERE b1.user_id={user_id})"), 1),
                        else_=0
                    ).label("is_blocked"),
                    select(func.count(follows.c.id)).where(follows.c.target_id == User.id).label('followers'),
                    select(areas.c.name).where(areas.c.code == func.concat(func.substring(User.area_code, 1, 5), '00000')).limit(1).label('area'),
                    func.ifnull(
                        case(
                            (user_id == User.id, None), # user_id == User.id 일 때 아래 서브쿼리에서 에러 발생(Error: Subquery returns more than 1 rows)
                            else_=text(f"(SELECT cu1.is_block FROM chat_users cu1, chat_users cu2 WHERE cu1.chat_room_id = cu2.chat_room_id AND cu1.user_id={user_id} AND cu2.user_id=users.id AND cu1.deleted_at IS NULL)")
                        ),
                        0
                    ).label("is_chat_blocked"),

                    func.json_arrayagg(
                        func.json_object(
                            "id", missions.c.id,
                            "title", missions.c.title,
                            "emoji", select(mission_categories.c.emoji).where(
                                mission_categories.c.id == missions.c.mission_category_id),
                            "is_ground", missions.c.is_ground,
                            "is_event", missions.c.is_event,
                            "is_old_event", case(
                                (and_(missions.c.id <= 1749, missions.c.is_event == 1), 1),
                                else_=0
                            ),
                            "event_type", missions.c.event_type,
                            "thumbnail", missions.c.thumbnail_image,
                            "bookmarked", case(
                                (text(
                                    f"(SELECT COUNT(*) FROM mission_stats WHERE mission_id = missions.id AND user_id = {user_id} AND ended_at IS NULL) > 0"),
                                    1),
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

                union = customized_sort_query.union(feed_for_recommendation).alias('union_feed')
                cursored_union = select(
                    text('union_feed.*'),
                    func.row_number().over(
                        order_by=[
                            desc(func.ifnull(
                                    select(True).where(
                                        and_(
                                            feed_likes.c.feed_id == union.c.id,
                                            feed_likes.c.user_id == user_id,
                                            feed_likes.c.deleted_at == None
                                        )
                                    ),
                                    False
                                )),
                                union.c.created_at
                            ]
                    ).label('cursor')
                ).select_from(union).order_by(union.c.checked, desc('cursor'))
                candidate = self.session.execute(cursored_union).all()
                cache.set("customized_sort_query", candidate)
        else:
            # pagination
            candidate = cache.get("customized_sort_query")

        result = [data for data in candidate if data.cursor < page_cursor][:limit]
        return result

    def count_number_of_newsfeed(self, user_id: int, page_cursor: int) -> int:
        followings = select(follows.c.target_id).where(follows.c.user_id == user_id)
        followings_number = select(func.count(follows.c.target_id)).where(follows.c.user_id == user_id)
        current_number_of_following = self.session.execute(followings_number).scalar()

        if page_cursor == INITIAL_DESCENDING_PAGE_CURSOR:
            customized_sort_query = select(
                Feed.id,
                func.ifnull(
                    select(True).where(
                        and_(
                            feed_likes.c.feed_id == Feed.id,
                            feed_likes.c.user_id == user_id,
                            feed_likes.c.deleted_at == None
                        )
                    ),
                    False
                ).label('checked'),
            ).join(
                User, Feed.user_id == User.id
            ).where(
                and_(
                    Feed.user_id.in_(followings),
                    func.TIMESTAMPDIFF(text("HOUR"), Feed.created_at, func.now()) <= 24,
                    Feed.is_hidden == 0,
                    Feed.deleted_at == None,
                )
            ).order_by(
                'checked'
            )
            newsfeed_count = select(func.count(customized_sort_query.c.id)).select_from(customized_sort_query)

            if current_number_of_following >= 10:
                # newsfeed only
                total_count = self.session.execute(newsfeed_count).scalar()
                cache.set("total_count_newsfeed", total_count)
            else:
                # newsfeed + recommendation

                # recommendation
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
                        Feed.user_id.not_in(followings),
                        Feed.deleted_at == None,
                        Feed.is_hidden == 0
                    )
                ).group_by(
                    text("t.feed_id")
                ).order_by(
                    desc(func.count(text("t.id"))),
                    desc(text("t.feed_id"))
                ).limit(10)
                recommend_feed_count = select(func.count(feed_candidate_query.c.id)).select_from(feed_candidate_query)

                total_count = self.session.execute(newsfeed_count).scalar() + self.session.execute(recommend_feed_count).scalar()
                cache.set("total_count_newsfeed", total_count)
        else:
            # pagination
            total_count = cache.get("total_count_newsfeed")

        return total_count

    def get_checked_feeds_by_user(self, user_id: int, page_cursor: int, limit: int):
        feed_likes_aliased = aliased(FeedCheck)
        sql = select(
            Feed.id,
            func.date_format(Feed.created_at, '%Y/%m/%d %H:%i:%s').label('created_at'),
            Feed.content.label('body'),
            Feed.is_hidden,
            select(func.json_arrayagg(
                func.json_object(
                    "order", FeedImage.order,
                    "mimeType", FeedImage.type,
                    "pathname", FeedImage.image,
                    "resized", func.json_array()
                )
            )).where(feed_images.c.feed_id == Feed.id).label("images"),
            select(func.count(feed_comments.c.id)).where(and_(feed_comments.c.feed_id == Feed.id, feed_comments.c.deleted_at == None)).label('comments_count'),
            select(func.count(feed_likes_aliased.id)).where(and_(feed_likes_aliased.feed_id == Feed.id, feed_likes_aliased.deleted_at == None)).label('checks_count'),

            users.c.id.label('user_id'),
            users.c.nickname,
            users.c.profile_image,
            case(
                (text(f"users.id IN (SELECT b1.target_id FROM blocks b1 WHERE b1.user_id={user_id})"), 1),
                else_=0
            ).label("is_blocked"),

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
            FeedCheck, FeedCheck.feed_id == Feed.id
        ).join(
            users, users.c.id == Feed.user_id
        ).join(
            FeedProduct, FeedProduct.feed_id == Feed.id, isouter=True
        ).join(
            products, products.c.id == FeedProduct.product_id, isouter=True
        ).join(
            outside_products, outside_products.c.id == FeedProduct.outside_product_id, isouter=True
        ).where(
            and_(
                FeedCheck.user_id == user_id,
                FeedCheck.deleted_at == None,
                User.deleted_at == None,
                Feed.deleted_at == None,
                Feed.id < page_cursor,
            )
        ).group_by(
            Feed.id
        ).order_by(desc(Feed.id)).limit(limit)

        result = self.session.execute(sql).all()
        return result

    def count_number_of_checked_feed_of_user(self, user_id: int):
        sql = select(
            func.count(Feed.id)
        ).join(
            feed_likes, feed_likes.c.feed_id == Feed.id
        ).join(
            User, Feed.user_id == User.id
        ).where(
            and_(
                feed_likes.c.user_id == user_id,
                feed_likes.c.deleted_at == None,
                User.deleted_at == None,
                Feed.deleted_at == None,
            )
        )

        result = self.session.execute(sql).scalar()
        return result

    def get_feeds_by_user(self, user_id: int, page_cursor: int, limit: int) -> list:
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
            Feed.is_hidden,
            func.date_format(Feed.deleted_at, '%Y/%m/%d %H:%i:%s').label('deleted_at'),
            case(
                (text(f"(SELECT COUNT(*) FROM feed_likes WHERE feed_id = feeds.id AND user_id = {user_id} AND deleted_at IS NULL) > 0"), 1),
                else_=0
            ).label('checked'),
            select(func.count(feed_comments.c.id)).where(and_(feed_comments.c.feed_id == Feed.id, feed_comments.c.deleted_at == None)).label('comments_count'),
            select(func.count(FeedCheck.id)).where(and_(FeedCheck.feed_id == Feed.id, FeedCheck.deleted_at == None)).label('checks_count'),

            User.id.label('user_id'),
            User.nickname,
            User.profile_image,
            User.gender,
            case(
                (text(f"users.id IN (SELECT f1.target_id FROM follows f1 WHERE f1.user_id={user_id})"), 1),
                else_=0
            ).label("followed"),
            case(
                (text(f"users.id IN (SELECT b1.target_id FROM blocks b1 WHERE b1.user_id={user_id})"), 1),
                else_=0
            ).label("is_blocked"),
            func.ifnull(
                case(
                    (user_id == User.id, None),  # user_id == User.id 일 때 아래 서브쿼리에서 에러 발생(Error: Subquery returns more than 1 rows)
                    else_=text(
                        f"(SELECT cu1.is_block FROM chat_users cu1, chat_users cu2 WHERE cu1.chat_room_id = cu2.chat_room_id AND cu1.user_id={user_id} AND cu2.user_id=users.id AND cu1.deleted_at IS NULL)")
                ),
                0
            ).label("is_chat_blocked"),
            select(func.count(follows.c.id)).where(follows.c.target_id == User.id).label('followers'),
            select(areas.c.name).where(areas.c.code == func.concat(func.substring(User.area_code, 1, 5), '00000')).limit(1).label('area'),

            func.json_arrayagg(
                func.json_object(
                    "id", missions.c.id,
                    "title", missions.c.title,
                    "emoji",
                    select(mission_categories.c.emoji).where(mission_categories.c.id == missions.c.mission_category_id),
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
                Feed.user_id == user_id,
                Feed.deleted_at == None,
                Feed.id < page_cursor,
            )
        ).group_by(
            Feed.id
        ).order_by(desc(Feed.id)).limit(limit)

        result = self.session.execute(sql)
        return result

    def count_number_of_feed_of_user(self, user_id: int) -> int:
        sql = select(
            func.count(Feed.id)
        ).where(
            and_(
                Feed.user_id == user_id,
                Feed.deleted_at == None,
            )
        )
        total_count = self.session.execute(sql).scalar()
        return total_count

    def get_feeds_by_mission(self, mission_id: int, user_id: int, page_cursor: int, limit: int) -> list:
        sql = select(
            Feed.id,
            func.date_format(Feed.created_at, '%Y/%m/%d %H:%i:%s').label('created_at'),
            Feed.content.label('body'),
            Feed.is_hidden,
            select(func.json_arrayagg(
                func.json_object(
                    "order", FeedImage.order,
                    "mimeType", FeedImage.type,
                    "pathname", FeedImage.image,
                    "resized", func.json_array()
                )
            )).select_from(FeedImage).where(FeedImage.feed_id == Feed.id).label("images"),
            case(
                (text(f"(SELECT COUNT(*) FROM feed_likes WHERE feed_id = feeds.id AND user_id = {user_id} AND deleted_at IS NULL) > 0"), 1),
                else_=0
            ).label('checked'),
            select(func.count(feed_comments.c.id)).where(and_(feed_comments.c.feed_id == Feed.id, feed_comments.c.deleted_at == None)).label('comments_count'),
            select(func.count(FeedCheck.id)).where(and_(FeedCheck.feed_id == Feed.id, FeedCheck.deleted_at == None)).label('checks_count'),

            User.id.label('user_id'),
            User.nickname,
            User.profile_image,
            User.gender,
            case(
                (text(f"users.id IN (SELECT f1.target_id FROM follows f1 WHERE f1.user_id={user_id})"), 1),
                else_=0
            ).label("followed"),
            case(
                (text(f"users.id IN (SELECT b1.target_id FROM blocks b1 WHERE b1.user_id={user_id})"), 1),
                else_=0
            ).label("is_blocked"),
            func.ifnull(
                case(
                    (user_id == User.id, None),  # user_id == User.id 일 때 아래 서브쿼리에서 에러 발생(Error: Subquery returns more than 1 rows)
                    else_=text(f"(SELECT cu1.is_block FROM chat_users cu1, chat_users cu2 WHERE cu1.chat_room_id = cu2.chat_room_id AND cu1.user_id={user_id} AND cu2.user_id=users.id AND cu1.deleted_at IS NULL)")
                ),
                0
            ).label("is_chat_blocked"),
            select(func.count(follows.c.id)).where(follows.c.target_id == User.id).label('followers'),
            select(areas.c.name).where(areas.c.code == func.concat(func.substring(User.area_code, 1, 5), '00000')).limit(1).label('area'),

            func.concat(func.lpad(Feed.id, 15, '0')).label('cursor'),
        ).join(
            User, User.id == Feed.user_id
        ).join(
            FeedMission, FeedMission.feed_id == Feed.id, isouter=True
        ).where(
            and_(
                FeedMission.mission_id == mission_id,
                Feed.deleted_at == None,
                Feed.id < page_cursor,
            )
        ).group_by(
            Feed.id
        ).order_by(desc(Feed.id)).limit(limit)

        result = self.session.execute(sql)
        return result

    def count_number_of_feed_of_mission(self, mission_id: int) -> int:
        sql = select(
            func.count(Feed.id)
        ).join(
            FeedMission, FeedMission.feed_id == Feed.id, isouter=True
        ).where(
            and_(
                FeedMission.mission_id == mission_id,
                Feed.deleted_at == None,
            )
        )
        total_count = self.session.execute(sql).scalar()
        return total_count

    def get_simple_one(self, feed_id: int) -> Feed:
        sql = select(Feed).where(Feed.id == feed_id)
        result = self.session.execute(sql).scalars().first()

        if result is not None:
            result.is_hidden = True if result.is_hidden == 1 else False

        return result

    def update(self, feed: Feed):
        sql = update(
            Feed
        ).where(
            Feed.id == feed.id
        ).values(
            content=feed.content,
            is_hidden=feed.is_hidden
        )
        return self.session.execute(sql)

    def delete(self, feed: Feed):
        sql = update(Feed).where(Feed.id == feed.id).values(deleted_at=func.now())
        return self.session.execute(sql)
