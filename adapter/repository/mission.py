from adapter.orm import areas, brands, feeds, feed_missions, follows, mission_conditions, mission_refund_products, mission_stats, orders, order_products, outside_products, products, users
from domain.feed import Feed, FeedMission
from domain.mission import Mission, MissionCategory, MissionComment, MissionPlayground, MissionPlaygroundCertificate, MissionPlaygroundCheerPhrase, MissionPlaygroundGround, MissionPlaygroundRecord, MissionImage, MissionIntroduce, MissionProduct, MissionRefundProduct, MissionStat
from domain.order import Order, OrderProduct
from domain.product import Product
from domain.user import User

import abc
from sqlalchemy import and_, case, desc, distinct, exists, func, or_, select, text
from sqlalchemy.orm import aliased


class AbstractMissionRepository(abc.ABC):
    @abc.abstractmethod
    def get_list_by_category(self, user_id: int, category_id: int, page_cursor: int, limit: int, sort: str):
        pass

    @abc.abstractmethod
    def count_number_of_mission_by_category(self, category_id: int):
        pass

    @abc.abstractmethod
    def get_list_user_participated(self, target_user_id: int, user_id: int, page_cursor: int, limit: int):
        pass

    @abc.abstractmethod
    def count_number_of_mission_user_participated(self, target_user_id: int):
        pass

    @abc.abstractmethod
    def get_list_user_created(self, target_user_id: int, user_id: int, page_cursor: int, limit: int, sort: str):
        pass

    @abc.abstractmethod
    def count_number_of_mission_user_created(self, target_user_id: int):
        pass

    @abc.abstractmethod
    def get_participants(self, mission_id: int, user_id: int, page_cursor: int, limit: int):
        pass

    @abc.abstractmethod
    def count_number_of_participants(self, mission_id: int):
        pass

    @abc.abstractmethod
    def get_introduce(self, mission_id: int):
        pass

    @abc.abstractmethod
    def get_playground(self, mission_id: int, user_id: int):
        pass

    @abc.abstractmethod
    def get_detail(self, mission_id: int, user_id: int):
        pass

    @abc.abstractmethod
    def translate_variables(self, variable: str, mission_id: int, user_id: int):
        pass

    @abc.abstractmethod
    def get_value_of_cheer_phrase_variable(self, variable: str, mission_id: int, user_id: int):
        pass


class MissionRepository(AbstractMissionRepository):
    def __init__(self, session):
        self.session = session

    def get_list_by_category(self, user_id: int, category_id: int or None, page_cursor: int, limit: int, sort: str):
        user_alias_participants = aliased(User)
        products_alias = aliased(products)
        products_alias_mission_products = aliased(products)
        comments_count = select(func.count(MissionComment.id)).where(and_(MissionComment.mission_id == Mission.id, MissionComment.deleted_at == None))
        condition = and_(
            Mission.mission_category_id == category_id,
            Mission.is_show == 1,
            Mission.deleted_at == None,
            Mission.id < page_cursor,
        ) if category_id is not None else \
            and_(
                Mission.is_show == 1,
                Mission.deleted_at == None,
                Mission.id < page_cursor,
        )

        sql = select(
            Mission.id,
            Mission.title,
            func.json_object(
                "id", MissionCategory.id,
                "title", MissionCategory.title,
                "emoji", MissionCategory.emoji,
            ).label("category"),
            Mission.description,
            Mission.thumbnail_image,
            func.date_format(Mission.created_at, '%Y/%m/%d %H:%i:%s').label('created_at'),
            func.date_format(Mission.started_at, '%Y/%m/%d %H:%i:%s').label('started_at'),
            func.date_format(Mission.ended_at, '%Y/%m/%d %H:%i:%s').label('ended_at'),
            func.date_format(Mission.reserve_started_at, '%Y/%m/%d %H:%i:%s').label('reserve_started_at'),
            func.date_format(Mission.reserve_ended_at, '%Y/%m/%d %H:%i:%s').label('reserve_ended_at'),
            case(
                (
                    and_(
                        Mission.reserve_started_at == None,
                        Mission.reserve_ended_at == None,
                    ),
                    case(
                        (
                            and_(
                                Mission.started_at == None,
                                Mission.ended_at == None,
                            ),
                            'ongoing'
                        ),
                        (Mission.started_at > func.now(), 'before_ongoing'),
                        (
                            and_(
                                Mission.started_at <= func.now(),
                                Mission.ended_at > func.now()
                            ),
                            'ongoing'
                        ),
                        else_='end'
                    ),
                ),
                else_=case(
                    (Mission.reserve_started_at > func.now(), 'before_reserve'),
                    (
                        and_(
                            Mission.reserve_started_at < Mission.reserve_ended_at,
                            Mission.reserve_ended_at <= Mission.started_at,
                            Mission.reserve_started_at <= func.now(),
                            func.now() < Mission.reserve_ended_at
                        ),
                        'reserve'
                    ),
                    (
                        and_(
                            Mission.reserve_started_at < Mission.reserve_ended_at,
                            Mission.started_at <= Mission.reserve_ended_at,
                            Mission.reserve_started_at <= func.now(),
                            func.now() < Mission.started_at
                        ),
                        'reserve'
                    ),
                    (
                        and_(
                            Mission.reserve_started_at < Mission.reserve_ended_at,
                            Mission.reserve_ended_at <= Mission.started_at,
                            Mission.reserve_ended_at <= func.now(),
                            func.now() < Mission.started_at
                        ),
                        'before_ongoing'
                    ),
                    (
                        and_(
                            Mission.reserve_started_at < Mission.reserve_ended_at,
                            Mission.reserve_ended_at <= Mission.started_at,
                            Mission.started_at <= func.now(),
                            func.now() < Mission.ended_at
                        ),
                        'ongoing'
                    ),
                    (
                        and_(
                            Mission.reserve_started_at < Mission.reserve_ended_at,
                            Mission.started_at <= Mission.reserve_ended_at,
                            Mission.started_at <= func.now(),
                            func.now() < Mission.ended_at
                        ),
                        'ongoing'
                    ),
                    else_='end'
                )
            ).label('status'),
            Mission.mission_type,
            func.json_object(
                'id', Mission.user_id,
                'gender', User.gender,
                'nickname', User.nickname,
                'profile', User.profile_image,
            ).label('producer'),
            select(
                func.count(MissionStat.id)
            ).select_from(
                MissionStat
            ).join(
                user_alias_participants, MissionStat.user_id == user_alias_participants.id, isouter=True
            ).where(
                MissionStat.mission_id == Mission.id,
                case(
                    (Mission.ended_at == None, MissionStat.ended_at == None),  # 종료기한(Mission.ended_at)이 없는 미션은 단순히 중도포기 여부만 체크한다.
                    else_=case(
                        (Mission.ended_at <= func.now(), MissionStat.ended_at >= Mission.ended_at),  # 종료 시점이 현재보다 과거라면 종료된 미션. Mission 종료 시점과 유저의 해당 미션 종료 시점(MissionStat)을 비교한다.
                        else_=MissionStat.ended_at == None  # 종료되지 않은 미션은 단순히 중도포기 여부만 체크한다.
                    )
                ),
                user_alias_participants.deleted_at == None
            ).label('bookmarks_count'),
            comments_count.label('comments_count'),
            func.json_arrayagg(
                func.json_object(
                    "id", products_alias.c.id,
                    "type", "inside",
                    "brand", select(brands.c.name_ko).where(brands.c.id == products_alias.c.brand_id),
                    "title", products_alias.c.name_ko,
                    "image", products_alias.c.thumbnail_image,
                    "url", None,
                    "price", products_alias.c.price,
                    "salePrice", products_alias.c.sale_price,
                    "shippingFee", products_alias.c.shipping_fee,
                    "discountRate", 100 - func.round(products_alias.c.sale_price / products_alias.c.price * 100),
                    "status", products_alias.c.status,
                    "availableStock", MissionRefundProduct.limit - select(
                        func.count(orders.c.id)
                    ).join(
                        order_products, orders.c.id == order_products.c.order_id, isouter=True
                    ).where(
                        and_(
                            order_products.c.product_id == products_alias.c.id,
                            order_products.c.brand_id == None,
                            orders.c.deleted_at == None
                        )
                    ),
                ),
            ).label('refund_products'),
            select(
                func.json_arrayagg(
                    func.json_object(
                        "id", func.IF(MissionProduct.type == 'inside', products_alias_mission_products.c.id, outside_products.c.id),
                        "type", MissionProduct.type,
                        "brand", func.IF(
                            MissionProduct.type == 'inside',
                            select(brands.c.name_ko).where(brands.c.id == products_alias_mission_products.c.brand_id),
                            outside_products.c.brand
                        ),
                        "title", func.IF(MissionProduct.type == 'inside', products_alias_mission_products.c.name_ko, outside_products.c.title),
                        "image", func.IF(MissionProduct.type == 'inside', products_alias_mission_products.c.thumbnail_image, outside_products.c.image),
                        "url", func.IF(MissionProduct.type == 'inside', None, outside_products.c.url),
                        "price", func.IF(MissionProduct.type == 'inside', products_alias_mission_products.c.price, outside_products.c.price),
                        "salePrice", func.IF(MissionProduct.type == 'inside', products_alias_mission_products.c.sale_price, None),
                        "shippingFee", func.IF(MissionProduct.type == 'inside', products_alias.c.shipping_fee, None),
                        "discountRate", func.IF(MissionProduct.type == 'inside', 100 - func.round(products_alias_mission_products.c.sale_price / products_alias_mission_products.c.price * 100), None),
                        "status", func.IF(MissionProduct.type == 'inside', products_alias.c.status, 'soldout'),
                        "availableStock", None
                    ),
                )
            ).select_from(
                MissionProduct
            ).join(
                products_alias_mission_products, products_alias_mission_products.c.id == MissionProduct.product_id, isouter=True
            ).join(
                outside_products, outside_products.c.id == MissionProduct.outside_product_id, isouter=True
            ).where(
                MissionProduct.mission_id == Mission.id
            ).label('mission_products'),
            Mission.user_limit,
            func.IF(MissionPlayground.id == None, False, True).label('has_playground'),
            func.concat(func.lpad(Mission.id, 15, '0')).label('cursor'),
        ).join(
            User, User.id == Mission.user_id
        ).join(
            MissionCategory, MissionCategory.id == Mission.mission_category_id
        ).join(
            MissionRefundProduct, MissionRefundProduct.mission_id == Mission.id, isouter=True
        ).join(
            products_alias, products_alias.c.id == MissionRefundProduct.product_id, isouter=True
        ).join(
            MissionPlayground, MissionPlayground.mission_id == Mission.id, isouter=True
        ).where(
            condition
        ).group_by(
            Mission.id
        ).order_by(
            text('bookmarks_count DESC, missions.id DESC') if sort == 'popular' or sort == 'bookmarksCount'
            else text('missions.event_order DESC, missions.id DESC') if sort == 'recent'
            else text('comments_count DESC, missions.id DESC') if sort == 'commentsCount'
            else desc(Mission.id)
        ).limit(limit)
        result = self.session.execute(sql).all()
        return result

    def count_number_of_mission_by_category(self, category_id: int):
        condition = and_(
                Mission.mission_category_id == category_id,
                Mission.is_show == 1,
                Mission.deleted_at == None,
            ) if category_id is not None else \
            and_(
            Mission.is_show == 1,
            Mission.deleted_at == None,
        )
        sql = select(func.count(Mission.id)).where(condition)
        total_count = self.session.execute(sql).scalar()
        return total_count

    def get_list_user_participated(self, target_user_id: int, user_id: int, page_cursor: int, limit: int):
        candidate = select(
            distinct(Mission.id)
        ).join(
            MissionStat, MissionStat.mission_id == Mission.id
        ).where(
            and_(
                MissionStat.user_id == target_user_id,
                Mission.deleted_at == None,
                Mission.is_show == 1,
                case(
                    (Mission.ended_at == None, MissionStat.ended_at == None),  # 종료기한(Mission.ended_at)이 없는 미션은 단순히 중도포기 여부만 체크한다.
                    else_=case(
                        (
                            Mission.ended_at <= func.now(),  # 종료 기한이 있는 경우
                            # (1) 포기 시점이 미션의 종료기한보다 미래이거나 동일해야 한다.
                            # (2) 삭제되지 않은 인증 피드가 1개 이상 있어야 한다.
                            and_(
                                MissionStat.ended_at >= Mission.ended_at,
                                select(
                                    func.count(feeds.c.id) > 0
                                ).join(
                                    feed_missions, feed_missions.c.feed_id == feeds.c.id
                                ).where(
                                    and_(
                                        feeds.c.user_id == MissionStat.user_id,
                                        feed_missions.c.mission_id == Mission.id,
                                        feeds.c.deleted_at == None
                                    )
                                )
                            )
                        ),
                        # 종료 시점이 현재보다 과거라면 종료된 미션. Mission 종료 시점과 유저의 해당 미션 종료 시점(MissionStat)을 비교한다.
                        else_=MissionStat.ended_at == None  # 종료되지 않은 미션은 단순히 중도포기 여부만 체크한다.
                    )
                ),
            )
        ).order_by(
            desc(Mission.id)
        )

        user_alias_participants = aliased(User)
        products_alias = aliased(products)
        products_alias_mission_products = aliased(products)
        comments_count = select(func.count(MissionComment.id)).where(and_(MissionComment.mission_id == Mission.id, MissionComment.deleted_at == None))
        condition = and_(
            Mission.id.in_(candidate),
            Mission.is_show == 1,
            Mission.deleted_at == None,
            Mission.id < page_cursor,
        )

        sql = select(
            Mission.id,
            Mission.title,
            func.json_object(
                "id", MissionCategory.id,
                "title", MissionCategory.title,
                "emoji", MissionCategory.emoji,
            ).label("category"),
            Mission.description,
            Mission.thumbnail_image,
            func.date_format(Mission.created_at, '%Y/%m/%d %H:%i:%s').label('created_at'),
            func.date_format(Mission.started_at, '%Y/%m/%d %H:%i:%s').label('started_at'),
            func.date_format(Mission.ended_at, '%Y/%m/%d %H:%i:%s').label('ended_at'),
            func.date_format(Mission.reserve_started_at, '%Y/%m/%d %H:%i:%s').label('reserve_started_at'),
            func.date_format(Mission.reserve_ended_at, '%Y/%m/%d %H:%i:%s').label('reserve_ended_at'),
            case(
                (
                    and_(
                        Mission.reserve_started_at == None,
                        Mission.reserve_ended_at == None,
                    ),
                    case(
                        (
                            and_(
                                Mission.started_at == None,
                                Mission.ended_at == None,
                            ),
                            'ongoing'
                        ),
                        (Mission.started_at > func.now(), 'before_ongoing'),
                        (
                            and_(
                                Mission.started_at <= func.now(),
                                Mission.ended_at > func.now()
                            ),
                            'ongoing'
                        ),
                        else_='end'
                    ),
                ),
                else_=case(
                    (Mission.reserve_started_at > func.now(), 'before_reserve'),
                    (
                        and_(
                            Mission.reserve_started_at < Mission.reserve_ended_at,
                            Mission.reserve_ended_at <= Mission.started_at,
                            Mission.reserve_started_at <= func.now(),
                            func.now() < Mission.reserve_ended_at
                        ),
                        'reserve'
                    ),
                    (
                        and_(
                            Mission.reserve_started_at < Mission.reserve_ended_at,
                            Mission.started_at <= Mission.reserve_ended_at,
                            Mission.reserve_started_at <= func.now(),
                            func.now() < Mission.started_at
                        ),
                        'reserve'
                    ),
                    (
                        and_(
                            Mission.reserve_started_at < Mission.reserve_ended_at,
                            Mission.reserve_ended_at <= Mission.started_at,
                            Mission.reserve_ended_at <= func.now(),
                            func.now() < Mission.started_at
                        ),
                        'before_ongoing'
                    ),
                    (
                        and_(
                            Mission.reserve_started_at < Mission.reserve_ended_at,
                            Mission.reserve_ended_at <= Mission.started_at,
                            Mission.started_at <= func.now(),
                            func.now() < Mission.ended_at
                        ),
                        'ongoing'
                    ),
                    (
                        and_(
                            Mission.reserve_started_at < Mission.reserve_ended_at,
                            Mission.started_at <= Mission.reserve_ended_at,
                            Mission.started_at <= func.now(),
                            func.now() < Mission.ended_at
                        ),
                        'ongoing'
                    ),
                    else_='end'
                )
            ).label('status'),
            Mission.mission_type,
            func.json_object(
                'id', Mission.user_id,
                'nickname', User.nickname,
                'gender', User.gender,
                'profile', User.profile_image,
            ).label('producer'),
            select(
                func.count(MissionStat.id)
            ).select_from(
                MissionStat
            ).join(
                user_alias_participants, MissionStat.user_id == user_alias_participants.id, isouter=True
            ).where(
                MissionStat.mission_id == Mission.id,
                case(
                    (Mission.ended_at == None, MissionStat.ended_at == None),  # 종료기한(Mission.ended_at)이 없는 미션은 단순히 중도포기 여부만 체크한다.
                    else_=case(
                        (Mission.ended_at <= func.now(), MissionStat.ended_at >= Mission.ended_at),
                        # 종료 시점이 현재보다 과거라면 종료된 미션. Mission 종료 시점과 유저의 해당 미션 종료 시점(MissionStat)을 비교한다.
                        else_=MissionStat.ended_at == None  # 종료되지 않은 미션은 단순히 중도포기 여부만 체크한다.
                    )
                ),
                user_alias_participants.deleted_at == None
            ).label('bookmarks_count'),
            comments_count.label('comments_count'),
            func.json_arrayagg(
                func.json_object(
                    "id", products_alias.c.id,
                    "type", "inside",
                    "brand", select(brands.c.name_ko).where(brands.c.id == products_alias.c.brand_id),
                    "title", products_alias.c.name_ko,
                    "image", products_alias.c.thumbnail_image,
                    "url", None,
                    "price", products_alias.c.price,
                    "salePrice", products_alias.c.sale_price,
                    "shippingFee", products_alias.c.shipping_fee,
                    "discountRate", 100 - func.round(products_alias.c.sale_price / products_alias.c.price * 100),
                    "status", products_alias.c.status,
                    "availableStock", MissionRefundProduct.limit - select(
                        func.count(orders.c.id)
                    ).join(
                        order_products, orders.c.id == order_products.c.order_id, isouter=True
                    ).where(
                        and_(
                            order_products.c.product_id == products_alias.c.id,
                            order_products.c.brand_id == None,
                            orders.c.deleted_at == None
                        )
                    ),
                ),
            ).label('refund_products'),
            select(
                func.json_arrayagg(
                    func.json_object(
                        "id", func.IF(MissionProduct.type == 'inside', products_alias_mission_products.c.id, outside_products.c.id),
                        "type", MissionProduct.type,
                        "brand", func.IF(
                            MissionProduct.type == 'inside',
                            select(brands.c.name_ko).where(brands.c.id == products_alias_mission_products.c.brand_id),
                            outside_products.c.brand
                        ),
                        "title", func.IF(MissionProduct.type == 'inside', products_alias_mission_products.c.name_ko, outside_products.c.title),
                        "image", func.IF(MissionProduct.type == 'inside', products_alias_mission_products.c.thumbnail_image, outside_products.c.image),
                        "url", func.IF(MissionProduct.type == 'inside', None, outside_products.c.url),
                        "price", func.IF(MissionProduct.type == 'inside', products_alias_mission_products.c.price, outside_products.c.price),
                        "salePrice", func.IF(MissionProduct.type == 'inside', products_alias_mission_products.c.sale_price, None),
                        "shippingFee", func.IF(MissionProduct.type == 'inside', products_alias.c.shipping_fee, None),
                        "discountRate", func.IF(MissionProduct.type == 'inside', 100 - func.round(products_alias_mission_products.c.sale_price / products_alias_mission_products.c.price * 100), None),
                        "status", func.IF(MissionProduct.type == 'inside', products_alias.c.status, 'soldout'),
                        "availableStock", None
                    ),
                )
            ).select_from(
                MissionProduct
            ).join(
                products_alias_mission_products, products_alias_mission_products.c.id == MissionProduct.product_id, isouter=True
            ).join(
                outside_products, outside_products.c.id == MissionProduct.outside_product_id, isouter=True
            ).where(
                MissionProduct.mission_id == Mission.id
            ).label('mission_products'),
            Mission.user_limit,
            func.IF(MissionPlayground.id == None, False, True).label('has_playground'),
            case(
                (select(
                    func.count(feed_missions.c.id) > 0
                ).join(
                    feeds, feed_missions.c.feed_id == feeds.c.id
                ).where(
                    and_(
                        feed_missions.c.mission_id == Mission.id,
                        feeds.c.user_id == target_user_id,
                        feeds.c.created_at >= func.DATE(func.now()),
                        feeds.c.deleted_at == None,
                    )
                ), True),
                else_=False
            ).label('completed_today'),
            func.concat(func.lpad(Mission.id, 15, '0')).label('cursor'),
        ).join(
            User, User.id == Mission.user_id
        ).join(
            MissionCategory, MissionCategory.id == Mission.mission_category_id
        ).join(
            MissionRefundProduct, MissionRefundProduct.mission_id == Mission.id, isouter=True
        ).join(
            products_alias, products_alias.c.id == MissionRefundProduct.product_id, isouter=True
        ).join(
            MissionPlayground, MissionPlayground.mission_id == Mission.id, isouter=True
        ).where(
            condition
        ).group_by(
            Mission.id
        ).order_by(
            desc(Mission.id)
        ).limit(limit)
        result = self.session.execute(sql).all()
        return result

    def count_number_of_mission_user_participated(self, target_user_id: int):
        sql = select(
            func.count(distinct(Mission.id))
        ).join(
            MissionStat, MissionStat.mission_id == Mission.id
        ).where(
            and_(
                MissionStat.user_id == target_user_id,
                Mission.deleted_at == None,
                Mission.is_show == 1,
                case(
                    (Mission.ended_at == None, MissionStat.ended_at == None),  # 종료기한(Mission.ended_at)이 없는 미션은 단순히 중도포기 여부만 체크한다.
                    else_=case(
                        (
                            Mission.ended_at <= func.now(),  # 종료 기한이 있는 경우
                            # (1) 포기 시점이 미션의 종료기한보다 미래이거나 동일해야 한다.
                            # (2) 삭제되지 않은 인증 피드가 1개 이상 있어야 한다.
                            and_(
                                MissionStat.ended_at >= Mission.ended_at,
                                select(
                                    func.count(feeds.c.id) > 0
                                ).join(
                                    feed_missions, feed_missions.c.feed_id == feeds.c.id
                                ).where(
                                    and_(
                                        feeds.c.user_id == MissionStat.user_id,
                                        feed_missions.c.mission_id == Mission.id,
                                        feeds.c.deleted_at == None
                                    )
                                )
                            )
                        ),
                        # 종료 시점이 현재보다 과거라면 종료된 미션. Mission 종료 시점과 유저의 해당 미션 종료 시점(MissionStat)을 비교한다.
                        else_=MissionStat.ended_at == None  # 종료되지 않은 미션은 단순히 중도포기 여부만 체크한다.
                    )
                ),
            )
        ).order_by(
            desc(Mission.id)
        )
        total_count = self.session.execute(sql).scalar()
        return total_count

    def get_list_user_created(self, target_user_id: int, user_id: int, page_cursor: int, limit: int, sort: str):
        user_alias_participants = aliased(User)
        products_alias = aliased(products)
        products_alias_mission_products = aliased(products)
        comments_count = select(func.count(MissionComment.id)).where(and_(MissionComment.mission_id == Mission.id, MissionComment.deleted_at == None))
        condition = and_(
            Mission.user_id == target_user_id,
            Mission.is_show == 1,
            Mission.deleted_at == None,
            Mission.id < page_cursor,
        )

        sql = select(
            Mission.id,
            Mission.title,
            func.json_object(
                "id", MissionCategory.id,
                "title", MissionCategory.title,
                "emoji", MissionCategory.emoji,
            ).label("category"),
            Mission.description,
            Mission.thumbnail_image,
            func.date_format(Mission.created_at, '%Y/%m/%d %H:%i:%s').label('created_at'),
            func.date_format(Mission.started_at, '%Y/%m/%d %H:%i:%s').label('started_at'),
            func.date_format(Mission.ended_at, '%Y/%m/%d %H:%i:%s').label('ended_at'),
            func.date_format(Mission.reserve_started_at, '%Y/%m/%d %H:%i:%s').label('reserve_started_at'),
            func.date_format(Mission.reserve_ended_at, '%Y/%m/%d %H:%i:%s').label('reserve_ended_at'),
            case(
                (
                    and_(
                        Mission.reserve_started_at == None,
                        Mission.reserve_ended_at == None,
                    ),
                    case(
                        (
                            and_(
                                Mission.started_at == None,
                                Mission.ended_at == None,
                            ),
                            'ongoing'
                        ),
                        (Mission.started_at > func.now(), 'before_ongoing'),
                        (
                            and_(
                                Mission.started_at <= func.now(),
                                Mission.ended_at > func.now()
                            ),
                            'ongoing'
                        ),
                        else_='end'
                    ),
                ),
                else_=case(
                    (Mission.reserve_started_at > func.now(), 'before_reserve'),
                    (
                        and_(
                            Mission.reserve_started_at < Mission.reserve_ended_at,
                            Mission.reserve_ended_at <= Mission.started_at,
                            Mission.reserve_started_at <= func.now(),
                            func.now() < Mission.reserve_ended_at
                        ),
                        'reserve'
                    ),
                    (
                        and_(
                            Mission.reserve_started_at < Mission.reserve_ended_at,
                            Mission.started_at <= Mission.reserve_ended_at,
                            Mission.reserve_started_at <= func.now(),
                            func.now() < Mission.started_at
                        ),
                        'reserve'
                    ),
                    (
                        and_(
                            Mission.reserve_started_at < Mission.reserve_ended_at,
                            Mission.reserve_ended_at <= Mission.started_at,
                            Mission.reserve_ended_at <= func.now(),
                            func.now() < Mission.started_at
                        ),
                        'before_ongoing'
                    ),
                    (
                        and_(
                            Mission.reserve_started_at < Mission.reserve_ended_at,
                            Mission.reserve_ended_at <= Mission.started_at,
                            Mission.started_at <= func.now(),
                            func.now() < Mission.ended_at
                        ),
                        'ongoing'
                    ),
                    (
                        and_(
                            Mission.reserve_started_at < Mission.reserve_ended_at,
                            Mission.started_at <= Mission.reserve_ended_at,
                            Mission.started_at <= func.now(),
                            func.now() < Mission.ended_at
                        ),
                        'ongoing'
                    ),
                    else_='end'
                )
            ).label('status'),
            Mission.mission_type,
            func.json_object(
                'id', Mission.user_id,
                'nickname', User.nickname,
                'gender', User.gender,
                'profile', User.profile_image,
            ).label('producer'),
            select(
                func.count(MissionStat.id)
            ).select_from(
                MissionStat
            ).join(
                user_alias_participants, MissionStat.user_id == user_alias_participants.id, isouter=True
            ).where(
                MissionStat.mission_id == Mission.id,
                case(
                    (Mission.ended_at == None, MissionStat.ended_at == None),  # 종료기한(Mission.ended_at)이 없는 미션은 단순히 중도포기 여부만 체크한다.
                    else_=case(
                        (Mission.ended_at <= func.now(), MissionStat.ended_at >= Mission.ended_at),
                        # 종료 시점이 현재보다 과거라면 종료된 미션. Mission 종료 시점과 유저의 해당 미션 종료 시점(MissionStat)을 비교한다.
                        else_=MissionStat.ended_at == None  # 종료되지 않은 미션은 단순히 중도포기 여부만 체크한다.
                    )
                ),
                user_alias_participants.deleted_at == None
            ).label('bookmarks_count'),
            comments_count.label('comments_count'),
            func.json_arrayagg(
                func.json_object(
                    "id", products_alias.c.id,
                    "type", "inside",
                    "brand", select(brands.c.name_ko).where(brands.c.id == products_alias.c.brand_id),
                    "title", products_alias.c.name_ko,
                    "image", products_alias.c.thumbnail_image,
                    "url", None,
                    "price", products_alias.c.price,
                    "salePrice", products_alias.c.sale_price,
                    "shippingFee", products_alias.c.shipping_fee,
                    "discountRate", 100 - func.round(products_alias.c.sale_price / products_alias.c.price * 100),
                    "status", products_alias.c.status,
                    "availableStock", MissionRefundProduct.limit - select(
                        func.count(orders.c.id)
                    ).join(
                        order_products, orders.c.id == order_products.c.order_id, isouter=True
                    ).where(
                        and_(
                            order_products.c.product_id == products_alias.c.id,
                            order_products.c.brand_id == None,
                            orders.c.deleted_at == None
                        )
                    ),
                ),
            ).label('refund_products'),
            select(
                func.json_arrayagg(
                    func.json_object(
                        "id", func.IF(MissionProduct.type == 'inside', products_alias_mission_products.c.id, outside_products.c.id),
                        "type", MissionProduct.type,
                        "brand", func.IF(
                            MissionProduct.type == 'inside',
                            select(brands.c.name_ko).where(brands.c.id == products_alias_mission_products.c.brand_id),
                            outside_products.c.brand
                        ),
                        "title", func.IF(MissionProduct.type == 'inside', products_alias_mission_products.c.name_ko, outside_products.c.title),
                        "image",
                        func.IF(MissionProduct.type == 'inside', products_alias_mission_products.c.thumbnail_image, outside_products.c.image),
                        "url", func.IF(MissionProduct.type == 'inside', None, outside_products.c.url),
                        "price", func.IF(MissionProduct.type == 'inside', products_alias_mission_products.c.price, outside_products.c.price),
                        "salePrice", func.IF(MissionProduct.type == 'inside', products_alias_mission_products.c.sale_price, None),
                        "shippingFee", func.IF(MissionProduct.type == 'inside', products_alias.c.shipping_fee, None),
                        "discountRate", func.IF(MissionProduct.type == 'inside', 100 - func.round(
                            products_alias_mission_products.c.sale_price / products_alias_mission_products.c.price * 100), None),
                        "status", func.IF(MissionProduct.type == 'inside', products_alias.c.status, 'soldout'),
                        "availableStock", None
                    ),
                )
            ).select_from(
                MissionProduct
            ).join(
                products_alias_mission_products, products_alias_mission_products.c.id == MissionProduct.product_id, isouter=True
            ).join(
                outside_products, outside_products.c.id == MissionProduct.outside_product_id, isouter=True
            ).where(
                MissionProduct.mission_id == Mission.id
            ).label('mission_products'),
            Mission.user_limit,
            func.IF(MissionPlayground.id == None, False, True).label('has_playground'),
            func.concat(func.lpad(Mission.id, 15, '0')).label('cursor'),
        ).join(
            User, User.id == Mission.user_id
        ).join(
            MissionCategory, MissionCategory.id == Mission.mission_category_id
        ).join(
            MissionRefundProduct, MissionRefundProduct.mission_id == Mission.id, isouter=True
        ).join(
            products_alias, products_alias.c.id == MissionRefundProduct.product_id, isouter=True
        ).join(
            MissionPlayground, MissionPlayground.mission_id == Mission.id, isouter=True
        ).where(
            condition
        ).group_by(
            Mission.id
        ).order_by(
            text('bookmarks_count DESC, missions.id DESC') if sort == 'popular' or sort == 'bookmarksCount'
            else text('missions.event_order DESC, missions.id DESC') if sort == 'recent'
            else text('comments_count DESC, missions.id DESC') if sort == 'commentsCount'
            else desc(Mission.id)
        ).limit(limit)
        result = self.session.execute(sql).all()
        return result

    def count_number_of_mission_user_created(self, target_user_id: int):
        sql = select(
            func.count(Mission.id)
        ).where(
            and_(
                Mission.user_id == target_user_id,
                Mission.is_show == True,
                Mission.deleted_at == None
            )
        )
        total_count = self.session.execute(sql).scalar()
        return total_count

    def get_participants(self, mission_id: int, user_id: int, page_cursor: int, limit: int):
        followings = select(follows.c.target_id).where(follows.c.user_id == user_id)
        follows_for_participant = aliased(follows)
        followers_of_user = select(func.count(follows_for_participant.c.id)).where(follows_for_participant.c.target_id == User.id)
        # area = select(areas.c.name).where(areas.c.code == func.concat(func.substring(User.area_code, 1, 5), '00000')).limit(1)

        sql = select(
            User.id,
            User.nickname,
            User.gender,
            User.profile_image,
            case(
                (User.id.in_(followings), True),
                else_=False
            ).label("followed"),
            followers_of_user.label('followers'),
            # area.label('area'),
            func.row_number().over(
                order_by=[
                    desc(
                        case(
                            (User.id.in_(followings), True),
                            else_=False
                        )
                    )
                ]
            ).label('cursor')
        ).select_from(
            MissionStat
        ).join(
            User, MissionStat.user_id == User.id, isouter=True
        ).join(
            Mission, MissionStat.mission_id == Mission.id, isouter=True
        ).where(
            and_(
                MissionStat.id > page_cursor,
                MissionStat.mission_id == mission_id,
                case(
                    (Mission.ended_at == None, MissionStat.ended_at == None),  # 종료기한(Mission.ended_at)이 없는 미션은 단순히 중도포기 여부만 체크한다.
                    else_=case(
                        (Mission.ended_at <= func.now(), MissionStat.ended_at >= Mission.ended_at),
                        # 종료 시점이 현재보다 과거라면 종료된 미션. Mission 종료 시점과 유저의 해당 미션 종료 시점(MissionStat)을 비교한다.
                        else_=MissionStat.ended_at == None  # 종료되지 않은 미션은 단순히 중도포기 여부만 체크한다.
                    )
                ),
                User.deleted_at == None
            )
        ).order_by(
            desc('followed'),
            'cursor'
        )
        candidate = self.session.execute(sql)
        result = [data for data in candidate if data.cursor > page_cursor][:limit]
        return result

    def count_number_of_participants(self, mission_id: int):
        sql = select(
            func.count(User.id),
        ).select_from(
            MissionStat
        ).join(
            User, MissionStat.user_id == User.id, isouter=True
        ).join(
            Mission, MissionStat.mission_id == Mission.id, isouter=True
        ).where(
            and_(
                MissionStat.mission_id == mission_id,
                case(
                    (Mission.ended_at == None, MissionStat.ended_at == None),  # 종료기한(Mission.ended_at)이 없는 미션은 단순히 중도포기 여부만 체크한다.
                    else_=case(
                        (Mission.ended_at <= func.now(), MissionStat.ended_at >= Mission.ended_at),
                        # 종료 시점이 현재보다 과거라면 종료된 미션. Mission 종료 시점과 유저의 해당 미션 종료 시점(MissionStat)을 비교한다.
                        else_=MissionStat.ended_at == None  # 종료되지 않은 미션은 단순히 중도포기 여부만 체크한다.
                    )
                ),
                User.deleted_at == None
            )
        )
        total_count = self.session.execute(sql).scalar()
        return total_count

    def get_introduce(self, mission_id: int):
        products_alias = aliased(products)
        products_alias_mission_products = aliased(products)
        sql = select(
            Mission.id,
            Mission.title,
            Mission.description,
            Mission.thumbnail_image,
            Mission.mission_type,
            Mission.user_limit,
            Mission.late_bookmarkable,
            func.date_format(Mission.created_at, '%Y/%m/%d %H:%i:%s').label('created_at'),
            func.date_format(Mission.started_at, '%Y/%m/%d %H:%i:%s').label('started_at'),
            func.date_format(Mission.ended_at, '%Y/%m/%d %H:%i:%s').label('ended_at'),
            func.date_format(Mission.reserve_started_at, '%Y/%m/%d %H:%i:%s').label('reserve_started_at'),
            func.date_format(Mission.reserve_ended_at, '%Y/%m/%d %H:%i:%s').label('reserve_ended_at'),
            MissionIntroduce.id.label('introduce_id'),
            MissionIntroduce.intro_video,
            MissionIntroduce.logo_image,
            func.json_object(
                "code", MissionIntroduce.code,
                "title", MissionIntroduce.code_title,
                "placeholder", MissionIntroduce.code_placeholder,
            ).label('enter_code'),
            func.json_arrayagg(
                func.json_object(
                    "id", MissionImage.id,
                    "order", MissionImage.order,
                    "type", MissionImage.type,
                    "pathname", MissionImage.image
                )
            ).label('images'),
            func.json_object(
                'id', Mission.user_id,
                'gender', User.gender,
                'nickname', User.nickname,
                'profile', User.profile_image,
            ).label('producer'),
            case(
                (
                    and_(
                        Mission.reserve_started_at == None,
                        Mission.reserve_ended_at == None,
                    ),
                    case(
                        (
                            and_(
                                Mission.started_at == None,
                                Mission.ended_at == None,
                            ),
                            'ongoing'
                        ),
                        (Mission.started_at > func.now(), 'before_ongoing'),
                        (
                            and_(
                                Mission.started_at <= func.now(),
                                Mission.ended_at > func.now()
                            ),
                            'ongoing'
                        ),
                        else_='end'
                    ),
                ),
                else_=case(
                    (Mission.reserve_started_at > func.now(), 'before_reserve'),
                    (
                        and_(
                            Mission.reserve_started_at < Mission.reserve_ended_at,
                            Mission.reserve_ended_at <= Mission.started_at,
                            Mission.reserve_started_at <= func.now(),
                            func.now() < Mission.reserve_ended_at
                        ),
                        'reserve'
                    ),
                    (
                        and_(
                            Mission.reserve_started_at < Mission.reserve_ended_at,
                            Mission.started_at <= Mission.reserve_ended_at,
                            Mission.reserve_started_at <= func.now(),
                            func.now() < Mission.started_at
                        ),
                        'reserve'
                    ),
                    (
                        and_(
                            Mission.reserve_started_at < Mission.reserve_ended_at,
                            Mission.reserve_ended_at <= Mission.started_at,
                            Mission.reserve_ended_at <= func.now(),
                            func.now() < Mission.started_at
                        ),
                        'before_ongoing'
                    ),
                    (
                        and_(
                            Mission.reserve_started_at < Mission.reserve_ended_at,
                            Mission.reserve_ended_at <= Mission.started_at,
                            Mission.started_at <= func.now(),
                            func.now() < Mission.ended_at
                        ),
                        'ongoing'
                    ),
                    (
                        and_(
                            Mission.reserve_started_at < Mission.reserve_ended_at,
                            Mission.started_at <= Mission.reserve_ended_at,
                            Mission.started_at <= func.now(),
                            func.now() < Mission.ended_at
                        ),
                        'ongoing'
                    ),
                    else_='end'
                )
            ).label('status'),
            func.json_arrayagg(
                func.json_object(
                    "id", products_alias.c.id,
                    "type", "inside",
                    "brand", select(brands.c.name_ko).where(brands.c.id == products_alias.c.brand_id),
                    "title", products_alias.c.name_ko,
                    "image", products_alias.c.thumbnail_image,
                    "url", None,
                    "price", products_alias.c.price,
                    "salePrice", products_alias.c.sale_price,
                    "shippingFee", products_alias.c.shipping_fee,
                    "discountRate", 100 - func.round(products_alias.c.sale_price / products_alias.c.price * 100),
                    "status", products_alias.c.status,
                    "availableStock", MissionRefundProduct.limit - select(
                        func.count(orders.c.id)
                    ).join(
                        order_products, orders.c.id == order_products.c.order_id, isouter=True
                    ).where(
                        and_(
                            order_products.c.product_id == products_alias.c.id,
                            order_products.c.brand_id == None,
                            orders.c.deleted_at == None
                        )
                    ),
                ),
            ).label('refund_products'),
            select(
                func.json_arrayagg(
                    func.json_object(
                        "id", func.IF(MissionProduct.type == 'inside', products_alias_mission_products.c.id, outside_products.c.id),
                        "type", MissionProduct.type,
                        "brand", func.IF(
                            MissionProduct.type == 'inside',
                            select(brands.c.name_ko).where(brands.c.id == products_alias_mission_products.c.brand_id),
                            outside_products.c.brand
                        ),
                        "title", func.IF(MissionProduct.type == 'inside', products_alias_mission_products.c.name_ko, outside_products.c.title),
                        "image",
                        func.IF(MissionProduct.type == 'inside', products_alias_mission_products.c.thumbnail_image, outside_products.c.image),
                        "url", func.IF(MissionProduct.type == 'inside', None, outside_products.c.url),
                        "price", func.IF(MissionProduct.type == 'inside', products_alias_mission_products.c.price, outside_products.c.price),
                        "salePrice", func.IF(MissionProduct.type == 'inside', products_alias_mission_products.c.sale_price, None),
                        "shippingFee", func.IF(MissionProduct.type == 'inside', products_alias.c.shipping_fee, None),
                        "discountRate", func.IF(MissionProduct.type == 'inside', 100 - func.round(
                            products_alias_mission_products.c.sale_price / products_alias_mission_products.c.price * 100), None),
                        "status", func.IF(MissionProduct.type == 'inside', products_alias.c.status, 'soldout'),
                        "availableStock", None
                    ),
                )
            ).select_from(
                MissionProduct
            ).join(
                products_alias_mission_products, products_alias_mission_products.c.id == MissionProduct.product_id, isouter=True
            ).join(
                outside_products, outside_products.c.id == MissionProduct.outside_product_id, isouter=True
            ).where(
                MissionProduct.mission_id == Mission.id
            ).label('mission_products'),
        ).join(
            MissionIntroduce, MissionIntroduce.mission_id == Mission.id, isouter=True
        ).join(
            MissionImage, MissionImage.mission_id == Mission.id,
        ).join(
            MissionRefundProduct, MissionRefundProduct.mission_id == Mission.id, isouter=True
        ).join(
            products_alias, products_alias.c.id == MissionRefundProduct.product_id, isouter=True
        ).join(
            User, User.id == Mission.user_id
        ).where(
            Mission.id == mission_id,
            Mission.is_show == 1,
            Mission.deleted_at == None
        )

        return self.session.execute(sql).first()

    def get_playground(self, mission_id: int, user_id: int):
        sql = select(
            MissionPlayground.id,
            MissionPlayground.background_image,
            MissionPlayground.rank_title,
            MissionPlayground.rank_value,
            MissionPlayground.rank_scale,

            MissionPlaygroundGround.symbol_image.label('ground_symbol_image'),
            MissionPlaygroundGround.progress_initial_image.label('ground_progress_initial_image'),
            MissionPlaygroundGround.progress_progressed_image.label('ground_progress_progressed_image'),
            MissionPlaygroundGround.progress_achieved_image.label('ground_progress_achieved_image'),
            MissionPlaygroundGround.progress_type.label('ground_progress_type'),
            MissionPlaygroundGround.progress_goal.label('ground_progress_goal'),
            MissionPlaygroundGround.progress_title.label('ground_progress_title'),
            MissionPlaygroundGround.progress_value.label('ground_progress_value'),
            MissionPlaygroundGround.progress_scale.label('ground_progress_scale'),
            MissionPlaygroundGround.dashboard_center_title.label('ground_dashboard_center_title'),
            MissionPlaygroundGround.dashboard_center_value.label('ground_dashboard_center_value'),
            MissionPlaygroundGround.dashboard_right_title.label('ground_dashboard_right_title'),
            MissionPlaygroundGround.dashboard_right_value.label('ground_dashboard_right_value'),
            MissionPlaygroundGround.banner_image,
            MissionPlaygroundGround.banner_type,
            MissionPlaygroundGround.banner_link,

            MissionPlaygroundRecord.symbol_image.label('record_symbol_image'),
            MissionPlaygroundRecord.total_success_count,
            MissionPlaygroundRecord.daily_image_before_completed,
            MissionPlaygroundRecord.daily_image_after_completed,
            MissionPlaygroundRecord.progress_type.label('record_progress_type'),
            MissionPlaygroundRecord.progress_title.label('record_progress_title'),
            MissionPlaygroundRecord.progress_value.label('record_progress_value'),
            MissionPlaygroundRecord.dashboard_left_title.label('record_dashboard_left_title'),
            MissionPlaygroundRecord.dashboard_left_value.label('record_dashboard_left_value'),
            MissionPlaygroundRecord.dashboard_center_title.label('record_dashboard_center_title'),
            MissionPlaygroundRecord.dashboard_center_value.label('record_dashboard_center_value'),
            MissionPlaygroundRecord.dashboard_right_title.label('record_dashboard_right_title'),
            MissionPlaygroundRecord.dashboard_right_value.label('record_dashboard_right_value'),
            MissionPlaygroundRecord.dashboard_description.label('record_dashboard_description'),

            MissionPlaygroundCertificate.title.label('certificate_title'),
            MissionPlaygroundCertificate.description.label('certificate_description'),
            MissionPlaygroundCertificate.certificate_image,
            MissionPlaygroundCertificate.event_images.label('certificate_event_images'),
            MissionPlaygroundCertificate.content_left_title.label('certificate_content_left_title'),
            MissionPlaygroundCertificate.content_left_value.label('certificate_content_left_value'),
            MissionPlaygroundCertificate.content_center_title.label('certificate_content_center_title'),
            MissionPlaygroundCertificate.content_center_value.label('certificate_content_center_value'),
            MissionPlaygroundCertificate.content_right_title.label('certificate_content_right_title'),
            MissionPlaygroundCertificate.content_right_value.label('certificate_content_right_value'),
            MissionPlaygroundCertificate.criterion_for_issue.label('certificate_criterion_for_issue'),
            MissionPlaygroundCertificate.minimum_value_for_issue.label('certificate_minimum_value_for_issue'),
            MissionPlaygroundCertificate.guidance_for_issue.label('certificate_guidance_for_issue'),
            func.json_arrayagg(
                func.json_object(
                # "ground", func.json_arrayagg(func.json_object(
                #     "tab", MissionPlaygroundCheerPhrase.tab,
                #     "order", MissionPlaygroundCheerPhrase.order,
                #     "variable", MissionPlaygroundCheerPhrase.variable,
                #     "value", MissionPlaygroundCheerPhrase.value,
                #     "sentence", MissionPlaygroundCheerPhrase.sentence,
                # )),
                # "record", func.json_arrayagg(func.json_object(
                    "tab", MissionPlaygroundCheerPhrase.tab,
                    "order", MissionPlaygroundCheerPhrase.order,
                    "condition", MissionPlaygroundCheerPhrase.condition,
                    "value", MissionPlaygroundCheerPhrase.value,
                    "sentence", MissionPlaygroundCheerPhrase.sentence,
                # )),
                )
            ).label("cheer_phrases"),
            # mission_conditions.c.certification_criterion,
            # mission_conditions.c.amount_determining_daily_success,
            # mission_conditions.c.input_scale,
            # mission_conditions.c.minimum_input,
            # mission_conditions.c.maximum_input,
            # mission_conditions.c.input_placeholder,
            Mission.mission_type,
            func.IFNULL(
                func.abs(
                    func.TIMESTAMPDIFF(
                        text("DAY"),
                        func.date_format(Mission.started_at, '%Y-%m-%D'),
                        func.date_format(func.now(), '%Y-%m-%D')
                    )
                ),
                0
            ).label("d_day"),
            case(
                (
                    and_(
                        Mission.reserve_started_at == None,
                        Mission.reserve_ended_at == None,
                    ),
                    case(
                        (
                            and_(
                                Mission.started_at == None,
                                Mission.ended_at == None,
                            ),
                            'ongoing'
                        ),
                        (Mission.started_at > func.now(), 'before_ongoing'),
                        (
                            and_(
                                Mission.started_at <= func.now(),
                                Mission.ended_at > func.now()
                            ),
                            'ongoing'
                        ),
                        else_='end'
                    ),
                ),
                else_=case(
                    (Mission.reserve_started_at > func.now(), 'before_reserve'),
                    (
                        and_(
                            Mission.reserve_started_at < Mission.reserve_ended_at,
                            Mission.reserve_ended_at <= Mission.started_at,
                            Mission.reserve_started_at <= func.now(),
                            func.now() < Mission.reserve_ended_at
                        ),
                        'reserve'
                    ),
                    (
                        and_(
                            Mission.reserve_started_at < Mission.reserve_ended_at,
                            Mission.started_at <= Mission.reserve_ended_at,
                            Mission.reserve_started_at <= func.now(),
                            func.now() < Mission.started_at
                        ),
                        'reserve'
                    ),
                    (
                        and_(
                            Mission.reserve_started_at < Mission.reserve_ended_at,
                            Mission.reserve_ended_at <= Mission.started_at,
                            Mission.reserve_ended_at <= func.now(),
                            func.now() < Mission.started_at
                        ),
                        'before_ongoing'
                    ),
                    (
                        and_(
                            Mission.reserve_started_at < Mission.reserve_ended_at,
                            Mission.reserve_ended_at <= Mission.started_at,
                            Mission.started_at <= func.now(),
                            func.now() < Mission.ended_at
                        ),
                        'ongoing'
                    ),
                    (
                        and_(
                            Mission.reserve_started_at < Mission.reserve_ended_at,
                            Mission.started_at <= Mission.reserve_ended_at,
                            Mission.started_at <= func.now(),
                            func.now() < Mission.ended_at
                        ),
                        'ongoing'
                    ),
                    else_='end'
                )
            ).label('status'),
        ).join(
            Mission, Mission.id == MissionPlayground.mission_id, isouter=True
        ).join(
            MissionPlaygroundGround, MissionPlaygroundGround.mission_playground_id == MissionPlayground.id, isouter=True
        ).join(
            MissionPlaygroundCertificate, MissionPlaygroundCertificate.mission_playground_id == MissionPlayground.id, isouter=True
        ).join(
            MissionPlaygroundCheerPhrase, MissionPlaygroundCheerPhrase.mission_id == Mission.id, isouter=True
        ).join(
            MissionPlaygroundRecord, MissionPlaygroundRecord.mission_playground_id == MissionPlayground.id, isouter=True
        ).where(
            and_(
                Mission.id == mission_id,
                # MissionPlayground.mission_id == mission_id,
                Mission.deleted_at == None,
                # Mission.is_show == 1,
            )
        # ).group_by(
        #     MissionPlaygroundCheerPhrase.tab
        )

        result = self.session.execute(sql).first()
        return result

    def get_detail(self, mission_id: int, user_id: int):
        products_alias = aliased(products)
        products_alias_mission_products = aliased(products)
        followings = select(follows.c.target_id).where(follows.c.user_id == user_id)
        follows_for_participant = aliased(follows)
        followers_of_user = select(func.count(follows_for_participant.c.id)).where(follows_for_participant.c.target_id == User.id)
        my_feeds_count = select(
            func.count(feeds.c.id)
        ).join(
            FeedMission, FeedMission.feed_id == feeds.c.id
        ).where(
            and_(
                FeedMission.mission_id == mission_id,
                feeds.c.user_id == user_id,
                feeds.c.deleted_at == None
            )
        )

        sql = select(
            Mission.id,
            Mission.title,
            Mission.description,
            Mission.thumbnail_image,
            Mission.mission_type,
            Mission.user_limit,
            my_feeds_count.label('my_feeds_count'),
            func.date_format(Mission.created_at, '%Y/%m/%d %H:%i:%s').label('created_at'),
            func.date_format(Mission.started_at, '%Y/%m/%d %H:%i:%s').label('started_at'),
            func.date_format(Mission.ended_at, '%Y/%m/%d %H:%i:%s').label('ended_at'),
            func.json_arrayagg(
                func.json_object(
                    "id", MissionImage.id,
                    "order", MissionImage.order,
                    "type", MissionImage.type,
                    "pathname", MissionImage.image
                )
            ).label('images'),
            func.json_object(
                'id', Mission.user_id,
                'gender', User.gender,
                'nickname', User.nickname,
                'profile', User.profile_image,
                followers_of_user.label('followers'),
                case(
                    (User.id.in_(followings), True),
                    else_=False
                ).label("followed"),
            ).label('producer'),
            case(
                (
                    and_(
                        Mission.reserve_started_at == None,
                        Mission.reserve_ended_at == None,
                    ),
                    case(
                        (
                            and_(
                                Mission.started_at == None,
                                Mission.ended_at == None,
                            ),
                            'ongoing'
                        ),
                        (Mission.started_at > func.now(), 'before_ongoing'),
                        (
                            and_(
                                Mission.started_at <= func.now(),
                                Mission.ended_at > func.now()
                            ),
                            'ongoing'
                        ),
                        else_='end'
                    ),
                ),
                else_=case(
                    (Mission.reserve_started_at > func.now(), 'before_reserve'),
                    (
                        and_(
                            Mission.reserve_started_at < Mission.reserve_ended_at,
                            Mission.reserve_ended_at <= Mission.started_at,
                            Mission.reserve_started_at <= func.now(),
                            func.now() < Mission.reserve_ended_at
                        ),
                        'reserve'
                    ),
                    (
                        and_(
                            Mission.reserve_started_at < Mission.reserve_ended_at,
                            Mission.started_at <= Mission.reserve_ended_at,
                            Mission.reserve_started_at <= func.now(),
                            func.now() < Mission.started_at
                        ),
                        'reserve'
                    ),
                    (
                        and_(
                            Mission.reserve_started_at < Mission.reserve_ended_at,
                            Mission.reserve_ended_at <= Mission.started_at,
                            Mission.reserve_ended_at <= func.now(),
                            func.now() < Mission.started_at
                        ),
                        'before_ongoing'
                    ),
                    (
                        and_(
                            Mission.reserve_started_at < Mission.reserve_ended_at,
                            Mission.reserve_ended_at <= Mission.started_at,
                            Mission.started_at <= func.now(),
                            func.now() < Mission.ended_at
                        ),
                        'ongoing'
                    ),
                    (
                        and_(
                            Mission.reserve_started_at < Mission.reserve_ended_at,
                            Mission.started_at <= Mission.reserve_ended_at,
                            Mission.started_at <= func.now(),
                            func.now() < Mission.ended_at
                        ),
                        'ongoing'
                    ),
                    else_='end'
                )
            ).label('status'),
            func.json_arrayagg(
                func.json_object(
                    "id", products_alias.c.id,
                    "type", "inside",
                    "brand", select(brands.c.name_ko).where(brands.c.id == products_alias.c.brand_id),
                    "title", products_alias.c.name_ko,
                    "image", products_alias.c.thumbnail_image,
                    "url", None,
                    "price", products_alias.c.price,
                    "salePrice", products_alias.c.sale_price,
                    "shippingFee", products_alias.c.shipping_fee,
                    "discountRate", 100 - func.round(products_alias.c.sale_price / products_alias.c.price * 100),
                    "status", products_alias.c.status,
                    "availableStock", MissionRefundProduct.limit - select(
                        func.count(orders.c.id)
                    ).join(
                        order_products, orders.c.id == order_products.c.order_id, isouter=True
                    ).where(
                        and_(
                            order_products.c.product_id == products_alias.c.id,
                            order_products.c.brand_id == None,
                            orders.c.deleted_at == None
                        )
                    ),
                ),
            ).label('refund_products'),
            select(
                func.json_arrayagg(
                    func.json_object(
                        "id", func.IF(MissionProduct.type == 'inside', products_alias_mission_products.c.id, outside_products.c.id),
                        "type", MissionProduct.type,
                        "brand", func.IF(
                            MissionProduct.type == 'inside',
                            select(brands.c.name_ko).where(brands.c.id == products_alias_mission_products.c.brand_id),
                            outside_products.c.brand
                        ),
                        "title", func.IF(MissionProduct.type == 'inside', products_alias_mission_products.c.name_ko, outside_products.c.title),
                        "image",
                        func.IF(MissionProduct.type == 'inside', products_alias_mission_products.c.thumbnail_image, outside_products.c.image),
                        "url", func.IF(MissionProduct.type == 'inside', None, outside_products.c.url),
                        "price", func.IF(MissionProduct.type == 'inside', products_alias_mission_products.c.price, outside_products.c.price),
                        "salePrice", func.IF(MissionProduct.type == 'inside', products_alias_mission_products.c.sale_price, None),
                        "shippingFee", func.IF(MissionProduct.type == 'inside', products_alias.c.shipping_fee, None),
                        "discountRate", func.IF(MissionProduct.type == 'inside', 100 - func.round(products_alias_mission_products.c.sale_price / products_alias_mission_products.c.price * 100), None),
                        "status", func.IF(MissionProduct.type == 'inside', products_alias.c.status, 'soldout'),
                        "availableStock", None
                    ),
                )
            ).select_from(
                MissionProduct
            ).join(
                products_alias_mission_products, products_alias_mission_products.c.id == MissionProduct.product_id, isouter=True
            ).join(
                outside_products, outside_products.c.id == MissionProduct.outside_product_id, isouter=True
            ).where(
                MissionProduct.mission_id == Mission.id
            ).label('mission_products'),
        ).join(
            User, User.id == Mission.user_id
        ).join(
            MissionImage, MissionImage.mission_id == Mission.id, isouter=True
        ).join(
            MissionRefundProduct, MissionRefundProduct.mission_id == Mission.id, isouter=True
        ).join(
            products_alias, products_alias.c.id == MissionRefundProduct.product_id, isouter=True
        ).where(
            Mission.id == mission_id,
            Mission.is_show == 1,
            Mission.deleted_at == None,
        )

        result = self.session.execute(sql).first()
        return result

    def translate_variables(self, variable: str, mission_id: int, user_id: int):
        """

        :param variable: 치환하고자 하는 변수
            - 'all_' 이 있는 variable은 미션에 참여한 유저 전체에 대한 기록을, 그렇지 않은 것은 user_id에 해당하는 유저에 대한 기록만을 집계.
            - 2023.1.3 현재 새로 추가될 미션에는 예정이 없으나, 과거 운영한 바가 있어 이를 위해 구현하는 변수
                - feed_places_count
                - today_feed_places_count
                - all_feed_places_count
                - today_all_feed_places_count
                - feed_places_count_3
                - feed_places_count_6
                - feed_places_count_9
        :param mission_id: 미션 id
        :param user_id: 유저 id
        :return: str
        """
        # func.TIMESTAMPDIFF(text("DAY"), func.DATE(FeedCheck.created_at), func.now()) == 0,
        # FeedCheck.created_at >= func.DATE(func.now()),
        if variable == 'users_count':
            sql = select(
                func.IFNULL(func.count(mission_stats.c.id), 0)
            ).join(
                users, mission_stats.c.user_id == users.c.id, isouter=True
            ).join(
                Mission, mission_stats.c.mission_id == Mission.id
            ).where(
                mission_stats.c.mission_id == mission_id,
                case(
                    (Mission.ended_at == None, mission_stats.c.ended_at == None),  # 종료기한(Mission.ended_at)이 없는 미션은 단순히 중도포기 여부만 체크한다.
                    else_=case(
                        (Mission.ended_at <= func.now(), mission_stats.c.ended_at >= Mission.ended_at), # 종료 시점이 현재보다 과거라면 종료된 미션. Mission 종료 시점과 유저의 해당 미션 종료 시점(MissionStat)을 비교한다.
                        else_=mission_stats.c.ended_at == None  # 종료되지 않은 미션은 단순히 중도포기 여부만 체크한다.
                    )
                ),
                users.c.deleted_at == None
            )
            result = self.session.execute(sql).scalar()
        elif variable == 'feeds_count':
            sql = select(
                func.IFNULL(func.count(distinct(feeds.c.id)), 0)
            ).join(
                feed_missions, feed_missions.c.feed_id == feeds.c.id
            ).where(
                and_(
                    feed_missions.c.mission_id == mission_id,
                    feeds.c.user_id == user_id,
                    feeds.c.deleted_at == None,
                )
            )
            result = self.session.execute(sql).scalar()
        elif variable == 'today_feeds_count':
            sql = select(
                func.IFNULL(func.count(distinct(feeds.c.id)), 0)
            ).join(
                feed_missions, feed_missions.c.feed_id == feeds.c.id
            ).where(
                and_(
                    feed_missions.c.mission_id == mission_id,
                    feeds.c.user_id == user_id,
                    func.TIMESTAMPDIFF(text("DAY"), func.DATE(feeds.c.created_at), func.now()) == 0,
                    feeds.c.created_at >= func.DATE(func.now()),
                    feeds.c.deleted_at == None,
                )
            )
            result = self.session.execute(sql).scalar()
        elif variable == 'all_feeds_count':
            sql = select(
                func.IFNULL(func.count(distinct(feeds.c.id)), 0)
            ).join(
                feed_missions, feed_missions.c.feed_id == feeds.c.id
            ).where(
                and_(
                    feed_missions.c.mission_id == mission_id,
                    feeds.c.deleted_at == None,
                )
            )
            result = self.session.execute(sql).scalar()
        elif variable == 'today_all_feeds_count':
            sql = select(
                func.IFNULL(func.count(distinct(feeds.c.id)), 0)
            ).join(
                feed_missions, feed_missions.c.feed_id == feeds.c.id
            ).where(
                and_(
                    feed_missions.c.mission_id == mission_id,
                    func.TIMESTAMPDIFF(text("DAY"), func.DATE(feeds.c.created_at), func.now()) == 0,
                    feeds.c.created_at >= func.DATE(func.now()),
                    feeds.c.deleted_at == None,
                )
            )
            result = self.session.execute(sql).scalar()
        elif variable == 'feed_places_count':  # feed_places : 장소 인증된 피드 수
            result = None

        elif variable == 'today_feed_places_count':
            result = None

        elif variable == 'all_feed_places_count':
            result = None

        elif variable == 'today_all_feed_places_count':
            result = None

        elif variable == 'feed_users_count':  # feed_users : 피드 올린 유저 수
            sql = select(
                func.IFNULL(func.count(distinct(feeds.c.user_id)), 0)
            ).join(
                feed_missions, feed_missions.c.feed_id == feeds.c.id
            ).where(
                and_(
                    feed_missions.c.mission_id == mission_id,
                    feeds.c.user_id == user_id,
                    feeds.c.deleted_at == None,
                )
            )
            result = self.session.execute(sql).scalar()
        elif variable in ['today_cert_count', 'today_feed_users_count']:
            sql = select(
                func.IFNULL(func.count(distinct(feeds.c.user_id)), 0)
            ).join(
                feed_missions, feed_missions.c.feed_id == feeds.c.id
            ).where(
                and_(
                    feed_missions.c.mission_id == mission_id,
                    func.TIMESTAMPDIFF(text("DAY"), func.DATE(feeds.c.created_at), func.now()) == 0,
                    feeds.c.created_at >= func.DATE(func.now()),
                    feeds.c.deleted_at == None,
                )
            )
            result = self.session.execute(sql).scalar()
        elif variable in ['total_distance', 'distance_summation']:
            sql = select(
                func.IFNULL(func.sum(feeds.c.distance), 0)
            ).join(
                feed_missions, feed_missions.c.feed_id == feeds.c.id
            ).where(
                and_(
                    feed_missions.c.mission_id == mission_id,
                    feeds.c.user_id == user_id,
                    feeds.c.deleted_at == None,
                )
            )
            result = self.session.execute(sql).scalar()
        elif variable in ['all_distance', 'all_distance_summation']:
            sql = select(
                func.IFNULL(func.sum(feeds.c.distance), 0)
            ).join(
                feed_missions, feed_missions.c.feed_id == feeds.c.id
            ).where(
                and_(
                    feed_missions.c.mission_id == mission_id,
                    feeds.c.deleted_at == None,
                )
            )
            result = self.session.execute(sql).scalar()
        elif variable in ['today_total_distance', 'today_distance_summation']:
            sql = select(
                func.IFNULL(func.sum(feeds.c.distance), 0)
            ).join(
                feed_missions, feed_missions.c.feed_id == feeds.c.id
            ).where(
                and_(
                    feed_missions.c.mission_id == mission_id,
                    feeds.c.user_id == user_id,
                    func.TIMESTAMPDIFF(text("DAY"), func.DATE(feeds.c.created_at), func.now()) == 0,
                    feeds.c.created_at >= func.DATE(func.now()),
                    feeds.c.deleted_at == None,
                )
            )
            result = self.session.execute(sql).scalar()
        elif variable in ['today_all_distance', 'today_all_distance_summation']:
            sql = select(
                func.IFNULL(func.sum(distinct(feeds.c.distance)), 0)
            ).join(
                feed_missions, feed_missions.c.feed_id == feeds.c.id
            ).where(
                and_(
                    feed_missions.c.mission_id == mission_id,
                    func.TIMESTAMPDIFF(text("DAY"), func.DATE(feeds.c.created_at), func.now()) == 0,
                    feeds.c.created_at >= func.DATE(func.now()),
                    feeds.c.deleted_at == None,
                )
            )
            result = self.session.execute(sql).scalar()
        elif variable in ['total_complete_day', 'complete_days_count']:
            sql = select(
                func.sum(feeds.c.distance).label('total_distance'),
                mission_conditions.c.amount_determining_daily_success
            ).join(
                feed_missions, feed_missions.c.feed_id == feeds.c.id
            ).join(
                Mission, feed_missions.c.mission_id == Mission.id
            ).join(
                mission_conditions, mission_conditions.c.mission_id == Mission.id
            ).where(
                and_(
                    feed_missions.c.mission_id == mission_id,
                    feeds.c.user_id == user_id,
                    feeds.c.deleted_at == None,
                )
            ).having(
                text('total_distance is NULL or total_distance >= amount_determining_daily_success')
            ).group_by(
                func.date_format(feeds.c.created_at, '%Y/%m/%d'), feeds.c.user_id
            )
            result = f"{str(len(self.session.execute(sql).all()))}일"
        elif variable in ['all_complete_day', 'all_complete_days_count']:
            sql = select(
                func.sum(feeds.c.distance).label('total_distance'),
                mission_conditions.c.amount_determining_daily_success
            ).join(
                feed_missions, feed_missions.c.feed_id == feeds.c.id
            ).join(
                Mission, feed_missions.c.mission_id == Mission.id
            ).join(
                mission_conditions, mission_conditions.c.mission_id == Mission.id
            ).where(
                and_(
                    feed_missions.c.mission_id == mission_id,
                    feeds.c.deleted_at == None,
                )
            ).having(
                text('total_distance is NULL or total_distance >= amount_determining_daily_success')
            ).group_by(
                func.date_format(feeds.c.created_at, '%Y/%m/%d'), feeds.c.user_id
            )
            result = f"{str(len(self.session.execute(sql).all()))}일"
        elif variable in ['feed_places_count_3', 'feed_places_count_6', 'feed_places_count_9']:
            threshold: int = int(variable.split('_')[-1])
            result = None

        elif variable == 'mission_starts_at':
            sql = select(func.date_format(Mission.started_at, '%Y/%m/%d %H:%i:%s')).where(Mission.id == mission_id)
            result = self.session.execute(sql).scalar()
        elif variable == 'mission_ends_at':
            sql = select(func.date_format(Mission.ended_at, '%Y/%m/%d %H:%i:%s')).where(Mission.id == mission_id)
            result = self.session.execute(sql).scalar()
        elif variable in ['mission_dday_end', 'remaining_day']:
            sql = select(
                func.TIMESTAMPDIFF(text("DAY"), func.DATE(Mission.ended_at), func.date_format(func.now(), '%Y/%m/%d 00:00:00'))
            ).where(
                MissionStat.mission_id == mission_id,
            )
            result = self.session.execute(sql).scalar()
        elif variable == 'entry_no':
            sql = select(
                mission_stats.c.entry_no
            ).join(
                Mission, mission_stats.c.mission_id == Mission.id
            ).where(
                and_(
                    mission_stats.c.mission_id == mission_id,
                    mission_stats.c.user_id == user_id,
                    case(
                        (Mission.ended_at == None, mission_stats.c.ended_at == None),  # 종료기한(Mission.ended_at)이 없는 미션은 단순히 중도포기 여부만 체크한다.
                        else_=case(
                            (Mission.ended_at <= func.now(), mission_stats.c.ended_at >= Mission.ended_at), # 종료 시점이 현재보다 과거라면 종료된 미션. Mission 종료 시점과 유저의 해당 미션 종료 시점(MissionStat)을 비교한다.
                            else_=mission_stats.c.ended_at == None  # 종료되지 않은 미션은 단순히 중도포기 여부만 체크한다.
                        )
                    )
                )
            )
            result = "NO. " if self.session.execute(sql).scalar() is None else f"NO. {str(self.session.execute(sql).scalar())}"
        else:
            result = None

        return result

    def get_value_of_cheer_phrase_variable(self, variable: str, mission_id: int, user_id: int):
        if variable == 'cert':
            sql = select(
                func.count(feeds.c.id)
            ).join(
                feed_missions, feed_missions.c.feed_id == feeds.c.id
            ).where(
                and_(
                    feeds.c.user_id == user_id,
                    feed_missions.c.mission_id == mission_id,
                    feeds.c.deleted_at == None
                )
            )
            result = self.session.execute(sql).scalar()
        elif variable == 'today_cert':
            sql = select(
                func.count(feeds.c.id)
            ).join(
                feed_missions, feed_missions.c.feed_id == feeds.c.id
            ).where(
                and_(
                    feeds.c.user_id == user_id,
                    feed_missions.c.mission_id == mission_id,
                    feeds.c.deleted_at == None,
                    func.TIMESTAMPDIFF(text("DAY"), func.DATE(feeds.c.created_at), func.now()) == 0,
                    feeds.c.created_at >= func.DATE(func.now()),
                )
            )
            result = self.session.execute(sql).scalar()
        elif variable == 'complete':  # 미션 전체 성공 여부
            sql = select(
                func.sum(feeds.c.distance).label('total_distance'),
                mission_conditions.c.amount_determining_daily_success
            ).join(
                feed_missions, feed_missions.c.feed_id == feeds.c.id
            ).join(
                Mission, feed_missions.c.mission_id == Mission.id
            ).join(
                mission_conditions, mission_conditions.c.mission_id == Mission.id
            ).where(
                and_(
                    feed_missions.c.mission_id == mission_id,
                    feeds.c.user_id == user_id,
                    feeds.c.deleted_at == None,
                )
            ).having(
                text('total_distance >= amount_determining_daily_success')
            ).group_by(
                func.date_format(feeds.c.created_at, '%Y/%m/%d'), mission_conditions.c.amount_determining_daily_success
            )
            result = 1 if len(self.session.execute(sql).all()) > 0 else 0
        elif variable == 'today_complete':  # 금일 미션 성공 여부
            sql = select(
                func.sum(feeds.c.distance).label('total_distance'),
                mission_conditions.c.amount_determining_daily_success
            ).join(
                feed_missions, feed_missions.c.feed_id == feeds.c.id
            ).join(
                Mission, feed_missions.c.mission_id == Mission.id
            ).join(
                mission_conditions, mission_conditions.c.mission_id == Mission.id
            ).where(
                and_(
                    feed_missions.c.mission_id == mission_id,
                    feeds.c.user_id == user_id,
                    feeds.c.deleted_at == None,
                    func.TIMESTAMPDIFF(text("DAY"), func.DATE(feeds.c.created_at), func.now()) == 0,
                    feeds.c.created_at >= func.DATE(func.now()),
                )
            ).having(
                text('total_distance >= amount_determining_daily_success')
            ).group_by(
                func.date_format(feeds.c.created_at, '%Y/%m/%d'), mission_conditions.c.amount_determining_daily_success
            )
            result = 1 if len(self.session.execute(sql).all()) > 0 else 0
        elif variable == 'end':
            sql = select(exists(Mission.id).where(and_(Mission.id == mission_id, Mission.ended_at < func.now())))
            result = 1 if self.session.execute(sql).scalar() is True else 0
        else:  # variable == 'default':  # 미션 시작 전 기본 문구
            result = 1

        return result
