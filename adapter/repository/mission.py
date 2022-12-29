from adapter.orm import areas, brands, feeds, feed_missions, follows, mission_refund_products, orders, order_products, outside_products, products
from domain.feed import FeedMission
from domain.mission import Mission, MissionCategory, MissionComment, MissionGround, MissionImage, MissionProduct, MissionRefundProduct, MissionStat
from domain.order import Order, OrderProduct
from domain.product import Product
from domain.user import User

import abc
from sqlalchemy import and_, case, desc, distinct, func, or_, select, text
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
    def get_playground(self):
        pass

    @abc.abstractmethod
    def get_detail(self, mission_id: int, user_id: int):
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
            func.IF(MissionGround.id == None, False, True).label('has_playground'),
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
            MissionGround, MissionGround.mission_id == Mission.id, isouter=True
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
            func.IF(MissionGround.id == None, False, True).label('has_playground'),
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
            MissionGround, MissionGround.mission_id == Mission.id, isouter=True
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
            func.IF(MissionGround.id == None, False, True).label('has_playground'),
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
            MissionGround, MissionGround.mission_id == Mission.id, isouter=True
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
            MissionGround.id.label('playground_id'),
            MissionGround.intro_video,
            MissionGround.logo_image,
            func.json_object(
                "code", MissionGround.code,
                "title", MissionGround.code_title,
                "placeholder", MissionGround.code_placeholder,
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
            MissionGround, MissionGround.mission_id == Mission.id, isouter=True
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

    def get_playground(self):
        pass

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


