from adapter.orm import areas, brands, follows, outside_products, products
from domain.mission import Mission, MissionCategory, MissionComment, MissionProduct, MissionStat
from domain.user import User

import abc
from sqlalchemy import and_, case, desc, distinct, func, select, text
from sqlalchemy.orm import aliased


class AbstractMissionRepository(abc.ABC):
    @abc.abstractmethod
    def get_list_by_category(self, user_id: int, category_id: int, page_cursor: int, limit: int, sort: str):
        pass

    @abc.abstractmethod
    def count_number_of_mission_by_category(self, category_id: int):
        pass

    @abc.abstractmethod
    def get_participants(self, mission_id: int, user_id: int, page_cursor: int, limit: int):
        pass

    @abc.abstractmethod
    def count_number_of_participants(self, mission_id: int):
        pass


class MissionRepository(AbstractMissionRepository):
    def __init__(self, session):
        self.session = session

    def get_list_by_category(self, user_id: int, category_id: int or None, page_cursor: int, limit: int, sort: str):
        user_alias_participants = aliased(User)
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
                    "type", MissionProduct.type,
                    "id", MissionProduct.id,
                    "brand", func.IF(
                        MissionProduct.type == 'inside',
                        select(brands.c.name_ko).where(brands.c.id == products.c.brand_id),
                        outside_products.c.brand
                    ),
                    "title", func.IF(MissionProduct.type == 'inside', products.c.name_ko, outside_products.c.title),
                    "image", func.IF(MissionProduct.type == 'inside', products.c.thumbnail_image, outside_products.c.image),
                    "url", func.IF(MissionProduct.type == 'inside', None, outside_products.c.url),
                    "price", func.IF(MissionProduct.type == 'inside', products.c.price, outside_products.c.price),
                    "salePrice", products.c.sale_price,
                    "discountRate", 100 - func.round(products.c.sale_price / products.c.price * 100),
                    "status", products.c.status,
                    # "availableStock", case(
                    #     (
                    #         Mission.mission_type == 'event_product_refund',
                    #         select(mission_refund_products.c.limit - )
                    #     ),
                    #     else_=None
                    # ),
                )
            ).label('products'),
            Mission.user_limit,
            func.concat(func.lpad(Mission.id, 15, '0')).label('cursor'),
        ).join(
            User, User.id == Mission.user_id
        ).join(
            MissionCategory, MissionCategory.id == Mission.mission_category_id
        ).join(
            MissionProduct, MissionProduct.mission_id == Mission.id, isouter=True
        ).join(
            products, products.c.id == MissionProduct.product_id, isouter=True
        ).join(
            outside_products, outside_products.c.id == MissionProduct.outside_product_id, isouter=True
        ).where(
            condition
        ).group_by(
            Mission.id
        ).order_by(
            desc(Mission.id) if category_id != 0
            else text('bookmarks_count DESC, missions.id DESC') if sort == 'popular' or sort == 'bookmarksCount'
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
