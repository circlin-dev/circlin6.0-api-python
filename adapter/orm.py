from domain.block import Block
from domain.board import Board, BoardCategory, BoardComment, BoardImage, BoardLike
from domain.brand import Brand
from domain.chat import ChatMessage, ChatUser, ChatRoom
from domain.common_code import CommonCode
from domain.feed import Feed, FeedCheck, FeedComment, FeedFood, FeedImage, FeedMission, FeedProduct
from domain.food import Food, FoodBrand, FoodCategory, FoodFlavor, FoodFoodCategory, FoodImage, FoodIngredient, FoodRating, FoodRatingImage, FoodRatingReview, FoodReview, Ingredient
from domain.mission import Mission, MissionCategory, MissionComment, MissionGround, MissionGroundText, MissionImage, MissionNotice, MissionNoticeImage, MissionProduct, MissionRefundProduct, MissionRank, MissionRankUser, MissionStat
from domain.notice import Notice, NoticeComment, NoticeImage
from domain.notification import Notification
from domain.order import Order, OrderProduct
from domain.point_history import PointHistory
from domain.product import OutsideProduct, Product, ProductCategory
from domain.push import PushHistory
from domain.report import Report
from domain.user import DeleteUser, Follow, User, UserFavoriteCategory, UserStat, UserWallpaper
from domain.version import Version

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, Table, TIMESTAMP, text
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR, TINYINT, DOUBLE, TEXT, INTEGER
from sqlalchemy.orm import registry, relationship

mapper_registry = registry()
metadata = mapper_registry.metadata
# region tables


# region areas
areas = Table(
    "areas",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("code", VARCHAR(255), nullable=False, index=True),
    Column("name", VARCHAR(255), nullable=False),
    Column("name_en", VARCHAR(255)),
)
# endregion


# region block
blocks = Table(
    "blocks",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("user_id", BIGINT(unsigned=True), ForeignKey('users.id'), index=True, comment='차단 요청자'),
    Column("target_id", BIGINT(unsigned=True), ForeignKey('users.id'), comment='user_id에 해당하는 유저가 차단하고자하는 상대 유저'),
)

# endregion


# region board
boards = Table(
    "boards",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("user_id", BIGINT(unsigned=True), ForeignKey('users.id'), nullable=False, index=True),
    Column("board_category_id", BIGINT(unsigned=True), ForeignKey('board_categories.id'), nullable=False, index=True),
    Column("body", TEXT(collation='utf8mb4_unicode_ci'), nullable=False),
    Column("deleted_at", TIMESTAMP),
    Column("is_show", TINYINT, nullable=False, server_default=text("'1'"))
)


board_categories = Table(
    "board_categories",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("title", VARCHAR(255), nullable=False)
)


board_comments = Table(
    "board_comments",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("board_id", ForeignKey('boards.id'), nullable=False, index=True),
    Column("user_id", ForeignKey('users.id'), nullable=False, index=True),
    Column("group", Integer, nullable=False, server_default=text("'0'")),
    Column("depth", TINYINT, nullable=False, server_default=text("'0'")),
    Column("comment", TEXT(collation='utf8mb4_unicode_ci'), nullable=False),
    Column("deleted_at", TIMESTAMP),
)


board_images = Table(
    "board_images",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("board_id", ForeignKey('boards.id'), nullable=False, index=True),
    Column("order", TINYINT, server_default=text("'0'")),
    Column("path", VARCHAR(255)),
    Column("file_name", VARCHAR(255)),
    Column("mime_type", VARCHAR(255)),
    Column("size", Integer),
    Column("width", Integer),
    Column("height", Integer),
    Column("original_file_id", BIGINT(unsigned=True), ForeignKey('board_images.id'), index=True)
)


board_likes = Table(
    "board_likes",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("board_id", ForeignKey('boards.id'), nullable=False, index=True),
    Column("user_id", ForeignKey('users.id'), nullable=False, index=True)
)
# endregion


# region brand
brands = Table(
    "brands",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("user_id", ForeignKey('users.id'), index=True, comment='브랜드 소유자'),
    Column("name_ko", VARCHAR(255), nullable=False, unique=True, server_default=text("''"), comment='브랜드명'),
    Column("name_en", VARCHAR(255), comment='브랜드명'),
    Column("image", VARCHAR(255)),
)

# endregion


# region chat
chat_messages = Table(
    "chat_messages",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("chat_room_id", BIGINT(unsigned=True), ForeignKey('chat_rooms.id'), nullable=False, index=True),
    Column("user_id", BIGINT(unsigned=True), ForeignKey('users.id'), nullable=False, index=True),
    Column("type", VARCHAR(255), comment='채팅 종류 (chat|chat_image|feed|feed_emoji|mission|mission_invite)'),
    Column("message", TEXT, comment='메시지'),
    Column("image_type", VARCHAR(255), comment='image/video'),
    Column("image", VARCHAR(255), comment='이미지 url'),
    Column("feed_id", BIGINT(unsigned=True), ForeignKey('feeds.id'), index=True, comment='피드 공유 및 이모지'),
    Column("mission_id", BIGINT(unsigned=True), comment='미션 초대'),
    Column("deleted_at", TIMESTAMP),
)


chat_rooms = Table(
    "chat_rooms",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("title", VARCHAR(255)),
    Column("is_group", TINYINT(1), nullable=False, server_default=text("'0'")),
    Column("deleted_at", TIMESTAMP),
)


chat_users = Table(
    "chat_users",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("chat_room_id", BIGINT(unsigned=True), ForeignKey('chat_rooms.id'), nullable=False, index=True),
    Column("user_id", BIGINT(unsigned=True), ForeignKey('users.id'), nullable=False, index=True),
    Column("is_block", TINYINT(1), nullable=False, server_default=text("'0'")),
    Column("message_notify", TINYINT(1), nullable=False, server_default=text("'1'")),
    Column("enter_message_id", BIGINT(unsigned=True), comment='입장할 때 마지막 메시지 id'),
    Column("read_message_id", BIGINT(unsigned=True), ForeignKey('chat_messages.id'), index=True, comment='마지막으로 읽은 메시지 id'),
    Column("deleted_at", TIMESTAMP),
)
# endregion


# region common_code
common_codes = Table(
    "common_codes",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("ctg_lg", VARCHAR(255)),
    Column("ctg_md", VARCHAR(255)),
    Column("ctg_sm", VARCHAR(255), nullable=False),
    Column("content_ko", VARCHAR(255), nullable=False),
    Column("content_en", VARCHAR(255)),
    Column("description", VARCHAR(255))
)
# endregion


# region deleted users
delete_users = Table(
    "delete_users",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("user_id", BIGINT(unsigned=True), ForeignKey('users.id'), nullable=False, index=True),
    Column("reason", TEXT, comment='탈퇴사유')
)

# endregion


# region feed
feeds = Table(
    "feeds",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("user_id", BIGINT(unsigned=True), ForeignKey('users.id'), nullable=False, index=True),
    Column("content",  TEXT(collation='utf8mb4_unicode_ci'), nullable=False),
    Column("is_hidden", TINYINT, nullable=False, server_default=text("'0'"), comment='비밀글 여부'),
    Column("deleted_at", TIMESTAMP),
    Column("distance", Float(8, True), comment='달린 거리'),
    Column("laptime", Integer, comment='달린 시간'),
    Column("distance_origin", Float(8, True), comment='인식된 달린 거리'),
    Column("laptime_origin", Integer, comment='인식된 달린 시간'),
)


feed_likes = Table(
    "feed_likes",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("feed_id", BIGINT(unsigned=True), ForeignKey('feeds.id'), nullable=False, index=True),
    Column("user_id", BIGINT(unsigned=True), ForeignKey('users.id'), nullable=False, index=True),
    Column("point", Integer, nullable=False, server_default=text("'0'"), comment='대상에게 포인트 지급 여부'),
    Column("deleted_at", TIMESTAMP)
)


feed_comments = Table(
    "feed_comments",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("feed_id", BIGINT(unsigned=True), ForeignKey('feeds.id'), nullable=False, index=True),
    Column("user_id", BIGINT(unsigned=True), ForeignKey('users.id'), nullable=False, index=True),
    Column("group", Integer, nullable=False, server_default=text("'0'")),
    Column("depth", TINYINT, nullable=False, server_default=text("'0'")),
    Column("comment",  TEXT(collation='utf8mb4_unicode_ci'), nullable=False),
    Column("deleted_at", TIMESTAMP),
)


feed_foods = Table(
    "feed_foods",
    metadata,
    Column("feed_id", BIGINT(unsigned=True), ForeignKey('feeds.id'), primary_key=True, nullable=False, index=True),
    Column("food_id", BIGINT(unsigned=True), ForeignKey('foods.id'), primary_key=True, nullable=False, index=True),
)


feed_images = Table(
    "feed_images",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("feed_id", BIGINT(unsigned=True), ForeignKey('feeds.id'), nullable=False, index=True),
    Column("order", TINYINT),
    Column("type", VARCHAR(255), nullable=False, comment='이미지인지 비디오인지 (image / video)'),
    Column("image", VARCHAR(255), nullable=False, comment='원본 이미지'),
    Column("thumbnail_image", VARCHAR(255), comment='미리 작게 보여줄 이미지'),
)


feed_missions = Table(
    "feed_missions",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("feed_id", BIGINT(unsigned=True), ForeignKey('feeds.id'), nullable=False, index=True),
    Column("mission_stat_id", BIGINT(unsigned=True), ForeignKey('mission_stats.id'), index=True),
    Column("mission_id", BIGINT(unsigned=True), ForeignKey('missions.id'), nullable=False, index=True),
)


feed_products = Table(
    "feed_products",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("feed_id", BIGINT(unsigned=True), ForeignKey('feeds.id'), nullable=False, index=True),
    Column("type", VARCHAR(255), nullable=False, comment='내부상품인지 외부상품인지 (inside|outside)'),
    Column("product_id", BIGINT(unsigned=True), ForeignKey('products.id'), index=True),
    Column("outside_product_id", BIGINT(unsigned=True), ForeignKey('outside_products.id'), index=True),
)
# endregion


# region follow
follows = Table(
    "follows",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("user_id", BIGINT(unsigned=True), ForeignKey('users.id'), nullable=False, index=True),
    Column("target_id", BIGINT(unsigned=True), ForeignKey('users.id'), nullable=False, index=True),
    Column("feed_notify", TINYINT(1), nullable=False, server_default=text("'0'")),
)
# endregion


# region foods
foods = Table(
    "foods",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("brand_id", BIGINT(unsigned=True), ForeignKey('food_brands.id'), nullable=False, index=True),
    Column("large_category_title", VARCHAR(64)),
    Column("title", VARCHAR(255), nullable=False, comment='메뉴명, 재료명, 제품명'),
    Column("user_id", BIGINT(unsigned=True), ForeignKey('users.id'), nullable=False, index=True, comment='최초 작성자 id'),
    Column("type", VARCHAR(32), comment='original(원물) | menu(대표메뉴), recipe(레시피), product(제품) => (원물의 조합)'),
    Column("barcode", VARCHAR(50), comment='null이면 원물(재료) 또는 food_category=내 요리'),
    Column("container", VARCHAR(255), comment='제공 용기 1단위: 1회제공량, 인분, 개, 컵, 조각, 접시, 봉지, 팩, 병, 캔, 그릇, 포\\n1용기당 제공량을 구한 후 쓴다.'),
    Column("amount_per_serving", Float, comment='1container 당 제공량'),
    Column("total_amount", Float, comment='총 제공량(중량, 포장 표기를 따름)'),
    Column("unit", VARCHAR(10), comment='제공 단위: 그램(g) | 밀리리터(ml)'),
    Column("servings_per_container", Float, server_default=text("'1'"), comment='1팩(번들) 당 제품 개수'),
    Column("price", Float, comment='원본 판매처 정상가'),
    Column("calorie", Float, comment='칼로리(총 내용량 기준, 포장 표기를 따름)'),
    Column("carbohydrate", Float, comment='탄수화물 함유량(g)(포장 표기를 따름)'),
    Column("protein", Float, comment='단백질 함유량(g)(포장 표기를 따름)'),
    Column("fat", Float, comment='지방 함유량(g)(포장 표기를 따름)'),
    Column("sodium", Float, comment='나트륨 함유량(mg)(포장 표기를 따름)'),
    Column("sugar", Float, comment='당류 함유량(g)(포장 표기를 따름)'),
    Column("trans_fat", Float, comment='트랜스 지방 함유량(g)(포장 표기를 따름)'),
    Column("saturated_fat", Float, comment='포화 지방 함유량(g)(포장 표기를 따름)'),
    Column("cholesterol", Float, comment='콜레스테롤 함유량(mg) (포장 표기를 따름)'),
    Column("url", TEXT(collation='utf8mb4_unicode_ci'), comment='구매처 URL'),
    Column("approved_at", TIMESTAMP, comment='관리자 승인 & 포인트 지급 일시'),
    Column("original_data", JSON, comment='공공 API의 원본 데이터 값'),
    Column("deleted_at", TIMESTAMP),
)


food_brands = Table(
    "food_brands",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("type", VARCHAR(255), nullable=False, comment='4 Types: 레스토랑, 체인점 | 슈퍼마켓, 마트 | 인기 브랜드 | 내 요리'),
    Column("title", VARCHAR(255), nullable=False, comment='type이 내 요리일 때는 기본값 적용, 그 외 세 가지 type일 때는 업체명을 입력 받음.'),
)


food_categories = Table(
    "food_categories",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("large", VARCHAR(255), comment='식단 대분류'),
    Column("medium", VARCHAR(255), comment='식단 중분류'),
    Column("small", VARCHAR(255), comment='식단 소분류'),
)


food_flavors = Table(
    "food_flavors",
    metadata,
    Column("food_id", BIGINT(unsigned=True), ForeignKey('foods.id'), nullable=False),
    Column("flavors", VARCHAR(255))
)


food_food_categories = Table(
    "food_food_categories",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("food_id", BIGINT(unsigned=True), ForeignKey('foods.id'), nullable=False, unique=True),
    Column("food_category_id", BIGINT(unsigned=True), ForeignKey('food_categories.id'), nullable=False, index=True),
)


food_images = Table(
    "food_images",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("food_id", BIGINT(unsigned=True), ForeignKey('foods.id'), nullable=False, index=True),
    Column("type", VARCHAR(32)),
    Column("path", VARCHAR(255)),
    Column("file_name", VARCHAR(255)),
    Column("mime_type", VARCHAR(255)),
    Column("size", Integer),
    Column("width", Integer),
    Column("height", Integer),
    Column("original_file_id", BIGINT(unsigned=True), ForeignKey('food_images.id'), index=True),
)


food_ratings = Table(
    "food_ratings",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("food_id", BIGINT(unsigned=True), ForeignKey('foods.id'), nullable=False, index=True),
    Column("user_id", BIGINT(unsigned=True), ForeignKey('users.id'), nullable=False, index=True),
    Column("rating", BIGINT(unsigned=True), nullable=False, comment='1~5점(클수록 높은 평점)의 범위 내에서 평점 부여하며 1점 단위'),
    Column("body", TEXT(collation='utf8mb4_unicode_ci')),
    Column("deleted_at", TIMESTAMP),
)


food_rating_images = Table(
    "food_rating_images",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("food_rating_id", BIGINT(unsigned=True), ForeignKey('food_ratings.id'), nullable=False, index=True),
    Column("path", VARCHAR(255)),
    Column("file_name", VARCHAR(255)),
    Column("mime_type", VARCHAR(255)),
    Column("size", Integer),
    Column("width", Integer),
    Column("height", Integer),
    Column("original_file_id", BIGINT(unsigned=True), ForeignKey('food_rating_images.id'), index=True),
)


food_rating_reviews = Table(
    "food_rating_reviews",
    metadata,
    Column("food_rating_id", BIGINT(unsigned=True), ForeignKey('food_ratings.id'), primary_key=True, nullable=False, index=True),
    Column("food_review_id", BIGINT(unsigned=True), ForeignKey('food_reviews.id'), primary_key=True, nullable=False, index=True),
)


food_reviews = Table(
    "food_reviews",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("value", VARCHAR(255,), nullable=False, comment='식품 카테고리별 후기 태그값'),
    Column("user_id", BIGINT(unsigned=True), ForeignKey('users.id'), index=True),
)


food_ingredients = Table(
    "food_ingredients",
    metadata,
    Column("food_id", BIGINT(unsigned=True), ForeignKey('foods.id'), primary_key=True, nullable=False, index=True),
    Column("ingredient_id", BIGINT(unsigned=True), ForeignKey('ingredients.id'), primary_key=True, nullable=False, index=True),
)


ingredients = Table(
    "ingredients",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("value", VARCHAR(255), nullable=False, unique=True),
)
# endregion


# region missions
missions = Table(
    "missions",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("user_id", BIGINT(unsigned=True), ForeignKey('users.id'), nullable=False, index=True, comment='미션 제작자'),
    Column("mission_category_id", BIGINT(unsigned=True), ForeignKey('mission_categories.id'), nullable=False, index=True, comment='카테고리'),
    Column("title", VARCHAR(255), index=True, comment='이름'),
    Column("description", TEXT, comment='상세 내용'),
    Column("thumbnail_image", VARCHAR(255), comment='썸네일'),
    Column("reserve_started_at", TIMESTAMP, comment='사전예약 시작 일시'),
    Column("reserve_ended_at", TIMESTAMP, comment='사전예약 종료 일시'),
    Column("started_at", TIMESTAMP, comment='시작 일시'),
    Column("ended_at", TIMESTAMP, comment='종료 일시'),
    Column("mission_type", VARCHAR(255), comment='식단(제품) 기록 챌린지가 등장하며 미션의 인증 유형을 구분하기 위해 만들어짐(20220616, 최건우)'),
    Column("is_show", TINYINT(1), nullable=False, server_default=text("'1'"), comment='노출 여부'),
    Column("is_event", TINYINT(1), nullable=False, server_default=text("'0'"), comment='이벤트(스페셜 미션) 탭에 노출 여부'),
    Column("is_ground", TINYINT(1), nullable=False, server_default=text("'0'"), comment='운동장으로 입장 여부'),
    Column("late_bookmarkable", TINYINT(1), nullable=False, server_default=text("'1'"), comment='도중 참여 가능 여부'),
    Column("subtitle", VARCHAR(255), comment='운동장 내부에 활용하는 짧은 이름'),
    Column("is_refund", TINYINT(1), nullable=False, server_default=text("'0'"), comment='제품 체험 챌린지 여부'),
    Column("is_ocr", TINYINT(1), nullable=False, server_default=text("'0'"), comment='OCR 필요한 미션인지'),
    Column("is_require_place", TINYINT(1), nullable=False, server_default=text("'0'"), comment='장소 인증 필수 여부'),
    Column("is_not_duplicate_place", TINYINT(1), nullable=False, server_default=text("'0'"), comment='일일 장소 중복 인증 불가 여부'),
    Column("is_tutorial", TINYINT(1), nullable=False, server_default=text("'0'"), comment='맨 처음 가입 시 관심 카테고리로 설정하면 기본적으로 담길 미션 여부'),
    Column("event_order", Integer, nullable=False, server_default=text("'0'"), comment='이벤트 페이지 정렬'),
    Column("deleted_at", TIMESTAMP),
    Column("event_type", TINYINT(1), comment='~5.0 미션룸 구분'),
    Column("reward_point", Integer, nullable=False, server_default=text("'0'"), comment='이벤트 성공 보상'),
    Column("success_count", Integer, nullable=False, server_default=text("'0'"), comment='x회 인증 시 성공 팝업 (지금은 1,0으로 운영)'),
    Column("user_limit", Integer, nullable=False, server_default=text("'0'"), comment='최대 참여자 수(0은 무제한)'),
    Column("treasure_started_at", TIMESTAMP, comment='보물찾기 포인트 지급 시작일자'),
    Column("treasure_ended_at", TIMESTAMP, comment='보물찾기 포인트 지급 종료일자'),
    Column("week_duration", Integer, comment='총 주차'),
    Column("week_min_count", Integer, comment='주당 최소 인증 횟수'),
)


mission_categories = Table(
    "mission_categories",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("mission_category_id", BIGINT(unsigned=True), ForeignKey('mission_categories.id'), index=True),
    Column("title", VARCHAR(255), nullable=False),
    Column("emoji", VARCHAR(255), comment='타이틀 앞의 이모지'),
    Column("description", TEXT, comment='카테고리 설명')
)


mission_comments = Table(
    "mission_comments",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("mission_id", BIGINT(unsigned=True), ForeignKey('missions.id'), nullable=False, index=True),
    Column("user_id", BIGINT(unsigned=True), ForeignKey('users.id'), nullable=False, index=True),
    Column("group", INTEGER, nullable=False, server_default=text("'0'")),
    Column("depth", TINYINT, nullable=False, server_default=text("'0'")),
    Column("comment",  TEXT(collation='utf8mb4_unicode_ci'), nullable=False),
    Column("deleted_at", TIMESTAMP)
)


mission_grounds = Table(
    "mission_grounds",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("mission_id", BIGINT(unsigned=True), ForeignKey('missions.id'), nullable=False, unique=True),
    Column("intro_video", VARCHAR(255), comment='소개 페이지 상단 동영상'),
    Column("logo_image", VARCHAR(255), comment='상단 고정 로고'),
    Column("code_type", VARCHAR(255), comment='코드 타입'),
    Column("code_title", VARCHAR(255), comment='입장코드 라벨'),
    Column("code", VARCHAR(255), comment='입장코드 (있으면 비교, 없으면 입력 받기만)'),
    Column("code_placeholder", VARCHAR(255), comment='입장코드 입력란 placeholder'),
    Column("code_image", VARCHAR(255), comment='입장코드 룸 상단 이미지'),
    Column("goal_distance_title", VARCHAR(255), comment='참가하기 전 목표 거리 타이틀'),
    Column("goal_distance_type", VARCHAR(255), nullable=False, server_default=text("'goal'"), comment='성공 조건 (goal/min)'),
    Column("goal_distances", JSON, comment='참가하기 전 설정할 목표 거리 (km)'),
    Column("goal_distance_text", VARCHAR(255), comment='참가하기 전 설정할 목표 거리 접미사'),
    Column("distance_min", Float(7), comment='인증 시 최소 거리'),
    Column("distance_max", Integer, comment='인증 시 최대 거리'),
    Column("distance_placeholder", VARCHAR(255), comment='입력란 placeholder'),
    Column("background_image", VARCHAR(255), comment='운동장 전체 fixed 배경 이미지'),
    Column("ground_title", VARCHAR(255), nullable=False, server_default=text("'운동장'"), comment='운동장 탭 타이틀'),
    Column("record_title", VARCHAR(255), nullable=False, server_default=text("'내기록'"), comment='내기록 탭 타이틀'),
    Column("cert_title", VARCHAR(255), nullable=False, server_default=text("'인증서'"), comment='인증서 탭 타이틀'),
    Column("feeds_title", VARCHAR(255), server_default=text("'모아보기'"), comment='피드 탭 타이틀 (null 일 경우 노출 X)'),
    Column("rank_title", VARCHAR(255), nullable=False, server_default=text("'랭킹'"), comment='랭킹 탭 타이틀'),
    Column("ground_is_calendar", TINYINT, nullable=False, server_default=text("'0'"), comment='운동장 탭 캘린더 형태 여부'),
    Column("ground_background_image", VARCHAR(255), comment='운동장 탭 배경이미지'),
    Column("ground_progress_type", VARCHAR(255), nullable=False, server_default=text("'feed'"), comment='운동장 탭 진행상황 타입 (feed/distance)'),
    Column("ground_progress_max", Integer, nullable=False, server_default=text("'0'"), comment='운동장 탭 진행상황 최대치'),
    Column("ground_progress_background_image", VARCHAR(255), comment='운동장 탭 진행상황 배경이미지'),
    Column("ground_progress_image", VARCHAR(255), comment='운동장 탭 진행상황 차오르는 이미지'),
    Column("ground_progress_complete_image", VARCHAR(255), comment='운동장 탭 진행상황 완료됐을 때 이미지'),
    Column("ground_progress_title", VARCHAR(255), server_default=text("'총 참가자 누적'"), comment='운동장 탭 진행상황 타이틀'),
    Column("ground_progress_text", VARCHAR(255), nullable=False, server_default=text("'{%%feeds_count}'"), comment='운동장 탭 진행상황 텍스트'),
    Column("ground_box_users_count_text", VARCHAR(255), nullable=False, server_default=text("'{%%users_count}명'"), comment='운동장 탭 참가중인 유저 수 텍스트'),
    Column("ground_box_users_count_title", VARCHAR(255), nullable=False, server_default=text("'참가자'"), comment='운동장 탭 참가중인 유저 수 타이틀'),
    Column("ground_box_summary_text", VARCHAR(255), nullable=False, server_default=text("'{%%today_all_distance} L'"), comment='운동장 탭 피드 수 텍스트'),
    Column("ground_box_summary_title", VARCHAR(255), nullable=False, server_default=text("'금일 누적'"), comment='운동장 탭 피드 수 타이틀'),
    Column("ground_banner_image", VARCHAR(255), comment='운동장 탭 배너 이미지 URL'),
    Column("ground_banner_type", VARCHAR(255), comment='운동장 탭 배너 타입 (url)'),
    Column("ground_banner_link", VARCHAR(255), comment='운동장 탭 배너 링크 URL'),
    Column("ground_users_type", VARCHAR(255), nullable=False, server_default=text("'recent_bookmark'"), comment='운동장 탭 유저 목록 타입'),
    Column("ground_users_title", VARCHAR(255), nullable=False, server_default=text("'실시간 참여자'"), comment='운동장 탭 유저 목록 타이틀'),
    Column("ground_users_text", VARCHAR(255), nullable=False, server_default=text("'아직 참여자가 없습니다! 어서 참여해보세요.'"), comment='운동장 탭 유저 목록 비었을 때 텍스트'),
    Column("record_progress_is_show", TINYINT(1), nullable=False, server_default=text("'1'"), comment='내기록 탭 진행상황 노출 여부'),
    Column("record_background_image", VARCHAR(255), comment='내기록 탭 배경이미지'),
    Column("record_progress_image_count", TINYINT, nullable=False, server_default=text("'9'"), comment='내기록 탭 진행상황 뱃지 개수'),
    Column("record_progress_images", JSON, comment='내기록 탭 진행상황 이미지'),
    Column("record_progress_type", VARCHAR(255), nullable=False, server_default=text("'feeds_count'"), comment='내기록 탭 진행상황 타입'),
    Column("record_progress_title", VARCHAR(255), comment='내기록 탭 진행상황 타이틀'),
    Column("record_progress_text", VARCHAR(255), server_default=text("'{%%remaining_day}'"), comment='내기록 탭 진행상황 텍스트'),
    Column("record_progress_description", VARCHAR(255), comment='내기록 탭 진행상황 텍스트 옆 설명'),
    Column("record_box_is_show", TINYINT(1), nullable=False, server_default=text("'1'"), comment='내기록 탭 박스 노출 여부'),
    Column("record_box_left_title", VARCHAR(255), server_default=text("'NO. {%%entry_no}'"), comment='내기록 탭 박스 왼쪽 타이틀'),
    Column("record_box_left_text", VARCHAR(255), server_default=text("'참가번호'"), comment='내기록 탭 박스 왼쪽 텍스트'),
    Column("record_box_center_title", VARCHAR(255), server_default=text("'{%%feeds_count}회'"), comment='내기록 탭 박스 가운데 타이틀'),
    Column("record_box_center_text", VARCHAR(255), server_default=text("'미션 인증횟수'"), comment='내기록 탭 박스 가운데 텍스트'),
    Column("record_box_right_title", VARCHAR(255), server_default=text("'{%%feeds_count}회'"), comment='내기록 탭 박스 오른쪽 타이틀'),
    Column("record_box_right_text", VARCHAR(255), server_default=text("'누적 인증'"), comment='내기록 탭 박스 오른쪽 텍스트'),
    Column("record_box_description", VARCHAR(255), comment='내기록 탭 박스 하단 설명'),
    Column("cert_subtitle", VARCHAR(255), nullable=False, server_default=text("'모바일 인증서'"), comment='인증서 탭 인증서 타이틀'),
    Column("cert_description", VARCHAR(255), comment='인증서 탭 내용'),
    Column("cert_background_image", JSON, comment='인증서 탭 인증서 배경 이미지'),
    Column("cert_custom_cert", JSON),
    Column("cert_details", JSON, comment='인증서 탭 인증서 상세내용'),
    Column("cert_images", JSON, comment='인증서 탭 하단 이미지'),
    Column("cert_disabled_text", VARCHAR(255), comment='인증서 탭 비활성화 상태 멘트'),
    Column("cert_enabled_feeds_count", TINYINT, nullable=False, server_default=text("'1'"), comment='인증서 탭 인증서 활성화될 피드 수'),
    Column("rank_subtitle", VARCHAR(255), comment='랭킹 탭 부제목'),
    Column("rank_value_text", VARCHAR(255), comment='랭킹 탭 피드 수 포맷'),
    Column("feeds_filter_title", VARCHAR(255), nullable=False, server_default=text("'필터 보기'"), comment='전체 피드 탭 필터 타이틀'),
)


mission_ground_texts = Table(
    "mission_ground_texts",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("mission_id", BIGINT(unsigned=True), ForeignKey('missions.id'), nullable=False, index=True),
    Column("tab", VARCHAR(255), nullable=False, comment='ground/record'),
    Column("order", TINYINT, nullable=False, comment='체크 순서 (높을수록 우선 출력)'),
    Column("type", VARCHAR(255), nullable=False, comment='조건'),
    Column("value", Integer, nullable=False, server_default=text("'0'"), comment='값'),
    Column("message", VARCHAR(255), nullable=False, comment='출력될 내용'),
)


mission_images = Table(
    "mission_images",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("mission_id", BIGINT(unsigned=True), ForeignKey('missions.id'), nullable=False, index=True),
    Column("order", TINYINT),
    Column("type", VARCHAR(255), nullable=False, comment='이미지인지 비디오인지 (image / video)'),
    Column("image", VARCHAR(255), nullable=False),
    Column("thumbnail_image", VARCHAR(255)),
)


mission_notices = Table(
    "mission_notices",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("mission_id", BIGINT(unsigned=True), ForeignKey('missions.id'), nullable=False, index=True),
    Column("created_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("title", VARCHAR(255), nullable=False),
    Column("body", TEXT(collation='utf8mb4_unicode_ci'), nullable=False),
    Column("deleted_at", TIMESTAMP),
)


mission_notice_images = Table(
    "mission_notice_images",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("mission_notice_id", BIGINT(unsigned=True), ForeignKey('mission_notices.id'), nullable=False, index=True),
    Column("created_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("order", INTEGER, nullable=False),
    Column("type", VARCHAR(255), nullable=False, comment='이미지인지 비디오인지 (image / video)'),
    Column("image", VARCHAR(255), nullable=False),
)


mission_products = Table(
    "mission_products",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("mission_id", BIGINT(unsigned=True), ForeignKey('missions.id'), nullable=False, index=True),
    Column("type", VARCHAR(255), nullable=False, comment='내부상품인지 외부상품인지 (inside|outside)'),
    Column("product_id", BIGINT(unsigned=True), ForeignKey('products.id'), index=True),
    Column("outside_product_id", BIGINT(unsigned=True), ForeignKey('outside_products.id'), index=True),
    Column("food_id", BIGINT(unsigned=True), ForeignKey('foods.id'),),
)


mission_ranks = Table(
    "mission_ranks",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("mission_id", BIGINT(unsigned=True), ForeignKey('missions.id'), nullable=False, index=True),
)


mission_rank_users = Table(
    "mission_rank_users",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("mission_rank_id", BIGINT(unsigned=True), ForeignKey('mission_ranks.id'), nullable=False, index=True),
    Column("user_id", BIGINT(unsigned=True), ForeignKey('users.id'), nullable=False, index=True),
    Column("rank", INTEGER, nullable=False, comment='feeds_count를 높은 순으로 랭킹을 매기되, 필요 시 거리나 횟수 등을 summation에 저장하고 이를 순위에 사용하게 될 수도 있다(마라톤 챌린지에서 사용한 바 있음).'),
    Column("feeds_count", INTEGER, nullable=False),
    Column("summation", INTEGER, nullable=False),
)


mission_refund_products = Table(
    "mission_refund_products",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("mission_id", BIGINT(unsigned=True), ForeignKey('missions.id'), nullable=False, index=True),
    Column("product_id", BIGINT(unsigned=True), ForeignKey('products.id'), nullable=False, index=True),
    Column("limit", TINYINT, nullable=False, comment='제품 최대 구매 수량'),
    Column("food_id", BIGINT(unsigned=True)),
)


mission_stats = Table(
    "mission_stats",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("user_id", BIGINT(unsigned=True), ForeignKey('users.id'), nullable=False, index=True),
    Column("mission_id", BIGINT(unsigned=True), ForeignKey('missions.id'), nullable=False, index=True),
    Column("ended_at", TIMESTAMP, comment='미션 콤보 마지막 기록 일시'),
    Column("completed_at", TIMESTAMP, comment='이벤트 미션 성공 일시'),
    Column("code", VARCHAR(255), comment='이벤트 미션 참가할 때 입력한 코드'),
    Column("entry_no", INTEGER, comment='미션 참여 순번'),
    Column("goal_distance", Float(8, True), comment='이벤트 미션 목표 거리'),
    Column("certification_image", VARCHAR(255), comment='인증서에 업로드한 이미지 URL'),
)
# endregion


# region notices
notices = Table(
    "notices",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("title", VARCHAR(255), nullable=False),
    Column("content", TEXT, nullable=False),
    Column("link_text", TEXT),
    Column("link_url", TEXT),
    Column("is_show", TINYINT(1), nullable=False, server_default=text("'1'")),
    Column("deleted_at", TIMESTAMP)
)


notice_comments = Table(
    "notice_comments",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("notice_id", BIGINT(unsigned=True), ForeignKey('notices.id'), nullable=False, index=True),
    Column("user_id", BIGINT(unsigned=True), ForeignKey('users.id'), nullable=False, index=True),
    Column("group", Integer, nullable=False, server_default=text("'0'")),
    Column("depth", TINYINT, nullable=False, server_default=text("'0'")),
    Column("comment",  TEXT(collation='utf8mb4_unicode_ci'), nullable=False),
    Column("deleted_at", TIMESTAMP),
)


notice_images = Table(
    "notice_images",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("notice_id", BIGINT(unsigned=True), ForeignKey('notices.id'), nullable=False, index=True),
    Column("order", INTEGER, server_default=text("'0'")),
    Column("type", VARCHAR(255), nullable=False, comment='이미지인지 비디오인지 (image / video)'),
    Column("image", VARCHAR(255), nullable=False),
)
# endregion


# region notification
notifications = Table(
    "notifications",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("target_id", ForeignKey('users.id'), nullable=False, index=True, comment='알림 받는 사람'),
    Column("type", VARCHAR(255), ForeignKey('common_codes.ctg_lg'), nullable=False, comment='알림 구분 (출력 내용은 common_codes)'),
    Column("user_id", BIGINT(unsigned=True), ForeignKey('users.id'), index=True, comment='알림 발생시킨 사람'),
    Column("feed_id", BIGINT(unsigned=True), ForeignKey('feeds.id'), index=True, comment='알림 발생한 게시물'),
    Column("feed_comment_id", BIGINT(unsigned=True), ForeignKey('feed_comments.id'), index=True),
    Column("mission_id", BIGINT(unsigned=True), ForeignKey('missions.id'), index=True),
    Column("mission_comment_id", BIGINT(unsigned=True), ForeignKey('mission_comments.id'), index=True),
    Column("mission_stat_id", BIGINT(unsigned=True), ForeignKey('mission_stats.id'), index=True),
    Column("notice_id", BIGINT(unsigned=True), ForeignKey('notices.id'), index=True),
    Column("notice_comment_id", BIGINT(unsigned=True), ForeignKey('notice_comments.id'), index=True),
    Column("board_id", BIGINT(unsigned=True), ForeignKey('boards.id'), index=True),
    Column("board_comment_id", BIGINT(unsigned=True), ForeignKey('board_comments.id'), index=True),
    Column("read_at", TIMESTAMP, comment='읽은 일시'),
    Column("variables", JSON)
)
# endregion


# region orders
orders = Table(
    "orders",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("order_no", VARCHAR(255), nullable=False, unique=True),
    Column("user_id", BIGINT(unsigned=True), ForeignKey('users.id'), nullable=False, index=True),
    Column("total_price", Integer, nullable=False, comment='결제금액'),
    Column("use_point", Integer, nullable=False, comment='사용한 포인트'),
    Column(
        "deleted_at",
        TIMESTAMP,
        comment="주문 취소 시점(refund에 관한 테이블, 컬럼이 없어 현재는 이것이 refund 역할을 함)\\n주문 취소 시 주문 취소 커맨드를 입력하고(노션 '써클인 인수인계' 참조), 아임포트 어드민에서도 취소해줘야 한다."),
    Column("imp_id", VARCHAR(40), comment='결제 식별번호(아임포트 키)'),
    Column("merchant_id", VARCHAR(40)),
)


order_products = Table(
    "order_products",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("order_id", BIGINT(unsigned=True), ForeignKey('orders.id'), nullable=False, index=True),
    Column("product_id", BIGINT(unsigned=True), ForeignKey('products.id'), index=True, comment='상품'),
    Column("brand_id", BIGINT, comment='배송비'),
    Column("qty", Integer, server_default=text("'0'")),
    Column("price", INTEGER, nullable=False, comment='구매 당시 단일 가격 or 배송비'),
)
# endregion


# region point history
point_histories = Table(
    "point_histories",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("user_id", BIGINT(unsigned=True), ForeignKey('users.id'), nullable=False, index=True),
    Column("point", Integer, nullable=False, comment='변경된 포인트'),
    Column("result", Integer, comment='잔여 포인트'),
    Column("reason", VARCHAR(255), nullable=False, comment='지급차감 사유 (like,mission 등) 출력될 내용은 common_codes'),
    Column("feed_id", BIGINT(unsigned=True), ForeignKey('feeds.id'), index=True),
    Column("order_id", BIGINT(unsigned=True), ForeignKey('orders.id'), index=True),
    Column("mission_id", BIGINT(unsigned=True), ForeignKey('missions.id'), index=True),
    Column("food_rating_id", BIGINT(unsigned=True), ForeignKey('food_ratings.id'), index=True),
    Column("feed_comment_id", BIGINT(unsigned=True), ForeignKey('feed_comments.id'), index=True),
)
# endregion


# region product
outside_products = Table(
    "outside_products",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("product_id", BIGINT(unsigned=True), comment='상품 고유 ID'),
    Column("brand", VARCHAR(255)),
    Column("title", VARCHAR(255), nullable=False),
    Column("image", VARCHAR(255)),
    Column("url", VARCHAR(255), nullable=False, unique=True),
    Column("price", Integer, nullable=False),
)


products = Table(
    "products",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("code", VARCHAR(255), nullable=False, unique=True),
    Column("name_ko", VARCHAR(255), nullable=False),
    Column("name_en", VARCHAR(255)),
    Column("thumbnail_image", VARCHAR(255), nullable=False),
    Column("brand_id", BIGINT(unsigned=True), ForeignKey('brands.id'), nullable=False, index=True),
    Column("product_category_id", BIGINT(unsigned=True), ForeignKey('product_categories.id'), index=True),
    Column("is_show", TINYINT(1), nullable=False, server_default=text("'1'")),
    Column("status", VARCHAR(255), nullable=False, server_default=text("'sale'"), comment='현재 상태 (sale / soldout)'),
    Column("order", Integer, nullable=False, server_default=text("'0'"), comment='정렬 (높을수록 우선)'),
    Column("price", Integer, nullable=False, comment='정상가'),
    Column("sale_price", Integer, nullable=False, server_default=text("'0'"), comment='판매가'),
    Column("shipping_fee", Integer, nullable=False, comment='배송비'),
    Column("deleted_at", TIMESTAMP),
)

product_categories = Table(
    "product_categories",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("title", VARCHAR(255), nullable=False),
    Column("deleted_at", TIMESTAMP),
)
# endregion


# region push
push_histories = Table(
    "push_histories",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("target_id", ForeignKey('users.id'), nullable=False, index=True, comment='푸시 받은 사람'),
    Column("device_token", VARCHAR(255)),
    Column("title", VARCHAR(255)),
    Column("message", TEXT, nullable=False),
    Column("type", VARCHAR(255), comment='tag'),
    Column("result", TINYINT(1), nullable=False),
    Column("json", JSON, comment='전송한 데이터'),
    Column("result_json", JSON, comment='반환 데이터')
)
# endregion


# region report
reports = Table(
    "reports",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("user_id", BIGINT(unsigned=True), ForeignKey('users.id'), index=True, comment='신고자 user id'),
    Column("target_feed_id", BIGINT(unsigned=True), ForeignKey('feeds.id'), index=True, comment='피드 신고 시 feed id값'),
    Column("target_user_id", BIGINT(unsigned=True), ForeignKey('users.id'), index=True, comment='유저 신고 시 user id값'),
    Column("target_mission_id", BIGINT(unsigned=True), ForeignKey('missions.id'), index=True, comment='미션 신고 시 mission id값'),
    Column("target_feed_comment_id", BIGINT(unsigned=True), ForeignKey('feed_comments.id'), index=True, comment='피드 댓글 신고 시 feed_comment id값'),
    Column("target_notice_comment_id", BIGINT(unsigned=True), ForeignKey('notice_comments.id'), index=True, comment='공지사항 댓글 신고 시 notice_comment id값'),
    Column("target_mission_comment_id", BIGINT(unsigned=True), ForeignKey('mission_comments.id'), index=True, comment='미션 댓글 신고 시 mission_comment id값'),
    Column("reason", TEXT(collation='utf8mb4_unicode_ci')),
)
# endregion

# region user
users = Table(
    "users",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True, nullable=False),
    Column("created_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("login_method", VARCHAR(32), default='email'),
    Column("sns_email", VARCHAR(255)),
    Column("email", VARCHAR(255), nullable=False),
    Column("email_verified_at", TIMESTAMP),
    Column("password", VARCHAR(255)),
    Column("nickname", VARCHAR(255)),
    Column("family_name", VARCHAR(255)),
    Column("given_name", VARCHAR(255)),
    Column("name", VARCHAR(255)),
    Column("gender", VARCHAR(255)),
    Column("phone", VARCHAR(255)),
    Column("phone_verified_at", TIMESTAMP),
    Column("point", Integer, default=0, nullable=False),
    Column("profile_image", VARCHAR(255)),
    Column("greeting", VARCHAR(255)),
    Column("background_image", VARCHAR(255)),
    Column("area_code", VARCHAR(255), ForeignKey("areas.code")),
    Column("area_updated_at", TIMESTAMP),
    Column("deleted_at", TIMESTAMP),
    Column("remember_token", VARCHAR(100)),
    Column("device_type", VARCHAR(255)),
    Column("socket_id", VARCHAR(255)),
    Column("device_token", VARCHAR(255)),
    Column("access_token", VARCHAR(255)),
    Column("refresh_token", VARCHAR(255)),
    Column("refresh_token_expire_in", VARCHAR(255)),
    Column("last_login_at", TIMESTAMP),
    Column("last_login_ip", VARCHAR(255)),
    Column("current_version", VARCHAR(255)),
    Column("agree1", TINYINT(1), default=0, nullable=False),
    Column("agree2", TINYINT(1), default=0, nullable=False),
    Column("agree3", TINYINT(1), default=0, nullable=False),
    Column("agree4", TINYINT(1), default=0, nullable=False),
    Column("agree5", TINYINT(1), default=0, nullable=False),
    Column("agree_push", TINYINT(1), default=1, nullable=False),
    Column("agree_push_mission", TINYINT(1), default=1, nullable=False),
    Column("agree_ad", TINYINT(1), default=1, nullable=False),
    Column("banner_hid_at", TIMESTAMP),
    Column("invite_code", VARCHAR(255)),
    Column("recommend_user_id", BIGINT(unsigned=True)),
    Column("recommend_updated_at", TIMESTAMP),
    Column("lat", DOUBLE(10, 7), default=37.4969117, nullable=False),
    Column("lng", DOUBLE(10, 7), default=127.0328342, nullable=False)
)


user_favorite_categories = Table(
    "user_favorite_categories",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("user_id", BIGINT(unsigned=True), ForeignKey('users.id'), nullable=False, index=True),
    Column("mission_category_id", BIGINT(unsigned=True), ForeignKey('mission_categories.id'), nullable=False, index=True)
)


user_stats = Table(
    "user_stats",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("user_id", BIGINT(unsigned=True), ForeignKey('users.id'), nullable=False, index=True),
    Column("birthday", DateTime, comment='생년월일'),
    Column("height", Float(8, True)),
    Column("weight", Float(8, True)),
    Column("bmi", Float(8, True)),
    Column("yesterday_feeds_count", INTEGER, nullable=False, server_default=text("'0'"), comment='어제 체크해야했던 피드 수'),
)


user_wallpapers = Table(
    "user_wallpapers",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("user_id", ForeignKey('users.id'), nullable=False, index=True),
    Column("title", VARCHAR(255), comment='스킨 이름'),
    Column("image", VARCHAR(255), nullable=False),
    Column("thumbnail_image", VARCHAR(255)),
    Column("deleted_at", TIMESTAMP),
)
# endregion


# region version
versions = Table(
    "versions",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True, nullable=False, unique=True),
    Column("created_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("version", VARCHAR(255), nullable=False, unique=True),
    Column("type", VARCHAR(50)),
    Column("description", VARCHAR(255)),
    Column("is_force", TINYINT(1), nullable=False),
)
# endregion

# endregion


# region mappers

# region areas
# def area_mappers():
#     mapper = mapper_registry.map_imperatively(
#         Area,
#         areas
#     )
#     return mapper
# endregion


def block_mappers():
    mapper_registry.map_imperatively(User, users)
    mapper = mapper_registry.map_imperatively(
        Block,
        blocks,
        properties={
            "users": relationship(User, primaryjoin='Block.user_id == User.id'),
        }
    )
    return mapper


# region boards
def board_mappers():
    mapper_registry.map_imperatively(BoardCategory, board_categories)
    mapper_registry.map_imperatively(BoardComment, board_comments)
    mapper_registry.map_imperatively(BoardImage, board_images)
    mapper_registry.map_imperatively(BoardLike, board_likes)
    mapper_registry.map_imperatively(User, users)

    mapper = mapper_registry.map_imperatively(
        Board,
        boards,
        properties={
            "board_categories": relationship(BoardCategory),
            "board_comments": relationship(BoardComment),
            "board_images": relationship(BoardImage),
            "board_likes": relationship(BoardLike),
            "users": relationship(User)
        }
    )
    return mapper


def board_category_mappers():
    mapper = mapper_registry.map_imperatively(BoardCategory, board_categories)
    return mapper


def board_comment_mappers():
    mapper_registry.map_imperatively(Board, boards)
    mapper_registry.map_imperatively(User, users)

    mapper = mapper_registry.map_imperatively(
        BoardComment,
        board_comments,
        properties={
            "boards": relationship(Board),
            "users": relationship(User)
        }
    )
    return mapper


def board_image_mappers():
    mapper_registry.map_imperatively(Board, boards)
    mapper = mapper_registry.map_imperatively(
        BoardImage,
        board_images,
        properties={
            "boards": relationship(Board),
            "board_images": relationship(BoardImage)
        }
    )
    return mapper


def board_like_mappers():
    mapper_registry.map_imperatively(Board, boards)
    mapper_registry.map_imperatively(User, users)

    mapper = mapper_registry.map_imperatively(
        BoardLike,
        board_likes,
        properties={
            "boards": relationship(Board),
            "users": relationship(User)
        }
    )
    return mapper
# endregion


# region brand
def brand_mappers():
    mapper_registry.map_imperatively(User, users)
    mapper = mapper_registry.map_imperatively(Brand, brands, properties={"users": relationship(User)})
    return mapper
# endregion


# region chat
def chat_message_mappers():
    mapper_registry.map_imperatively(User, users)
    mapper_registry.map_imperatively(ChatRoom, chat_rooms)
    mapper_registry.map_imperatively(Feed, feeds)
    mapper = mapper_registry.map_imperatively(
        ChatMessage,
        chat_messages,
        properties={
            "users": relationship(User),
            "chat_rooms": relationship(ChatRoom),
            "feeds": relationship(Feed)
        }
    )
    return mapper


def chat_room_mappers():
    mapper = mapper_registry.map_imperatively(ChatRoom, chat_rooms)
    return mapper


def chat_user_mappers():
    mapper_registry.map_imperatively(ChatRoom, chat_rooms)
    mapper_registry.map_imperatively(ChatMessage, chat_messages)
    mapper_registry.map_imperatively(User, users)
    mapper = mapper_registry.map_imperatively(
        ChatUser,
        chat_users,
        properties={
            "chat_rooms": relationship(ChatRoom),
            "chat_messages": relationship(ChatMessage),
            "users": relationship(User),
        }
    )
    return mapper
# endregion


# region common_code
def common_code_mappers():
    mapper = mapper_registry.map_imperatively(
        CommonCode,
        common_codes,
        properties={"notifications": relationship(notifications)}
    )
    return mapper
# endregion


# region deleted users
def delete_user_mappers():
    mapper = mapper_registry.map_imperatively(
        DeleteUser,
        delete_users,
        properties={"users": relationship(User)}
    )
    return mapper

# endregion


# region feed
def feed_mappers():
    mapper_registry.map_imperatively(User, users)
    mapper_registry.map_imperatively(FeedImage, feed_images)
    mapper_registry.map_imperatively(FeedComment, feed_comments)
    mapper_registry.map_imperatively(FeedCheck, feed_likes)
    mapper_registry.map_imperatively(FeedMission, feed_missions)
    mapper_registry.map_imperatively(FeedProduct, feed_products)
    mapper_registry.map_imperatively(FeedFood, feed_foods)
    mapper = mapper_registry.map_imperatively(
        Feed,
        feeds,
        properties={
            "users": relationship(User),
            "feed_images": relationship(FeedImage),
            "feed_comments": relationship(FeedComment),
            "feed_likes": relationship(FeedCheck),
            "feed_missions": relationship(FeedMission),
            "feed_products": relationship(FeedProduct),
            "feed_foods": relationship(FeedFood),
        }
    )
    return mapper


def feed_check_mappers():
    mapper_registry.map_imperatively(Feed, feeds)
    mapper_registry.map_imperatively(User, users)
    mapper = mapper_registry.map_imperatively(
        FeedCheck,
        feed_likes,
        properties={
            "feeds": relationship(Feed),
            "users": relationship(User)
        }
    )
    return mapper


def feed_comment_mappers():
    mapper_registry.map_imperatively(Feed, feeds)
    mapper_registry.map_imperatively(User, users)

    mapper = mapper_registry.map_imperatively(
        FeedComment,
        feed_comments,
        properties={
            "feeds": relationship(Feed),
            "users": relationship(User)
        }
    )
    return mapper


def feed_food_mappers():
    mapper_registry.map_imperatively(Feed, feeds)
    mapper_registry.map_imperatively(Food, foods)
    mapper = mapper_registry.map_imperatively(
        FeedFood,
        feed_foods,
        properties={
            "feeds": relationship(Feed),
            "foods": relationship(Food)
        }
    )
    return mapper


def feed_image_mappers():
    mapper_registry.map_imperatively(Feed, feeds)
    mapper = mapper_registry.map_imperatively(
        FeedImage,
        feed_images,
        properties={"feeds": relationship(Feed)}
    )
    return mapper


def feed_mission_mappers():
    mapper_registry.map_imperatively(Feed, feeds)
    mapper_registry.map_imperatively(Mission, missions)
    mapper_registry.map_imperatively(MissionProduct, mission_products)
    mapper_registry.map_imperatively(MissionStat, mission_stats)
    mapper = mapper_registry.map_imperatively(
        FeedMission,
        feed_missions,
        properties={
            "feeds": relationship(Feed),
            "missions": relationship(Mission),
            "mission_products": relationship(MissionProduct),
            "mission_stats": relationship(MissionStat)
        }
    )
    return mapper


def feed_product_mappers():
    mapper_registry.map_imperatively(Feed, feeds)
    mapper_registry.map_imperatively(OutsideProduct, outside_products)
    mapper_registry.map_imperatively(Product, products)
    mapper = mapper_registry.map_imperatively(
        FeedProduct,
        feed_products,
        properties={
            relationship('Feed'),
            relationship('OutsideProduct'),
            relationship('Product')
        }
    )
    return mapper
# endregion


# region follow
def follow_mappers():
    mapper_registry.map_imperatively(User, users)
    mapper = mapper_registry.map_imperatively(Follow, follows, properties={"users": relationship(User, primaryjoin='Follow.user_id == User.id')})
    return mapper
# endregion


# region food
def food_flavor_mappers():
    mapper_registry.map_imperatively(Food, foods)
    mapper = mapper_registry.map_imperatively(FoodFlavor, food_flavors, properties={"foods": relationship(Food)})
    return mapper


def food_mappers():
    mapper_registry.map_imperatively(FoodBrand, food_brands)
    mapper_registry.map_imperatively(FoodFoodCategory, food_food_categories)
    mapper_registry.map_imperatively(FoodIngredient, food_ingredients)
    mapper_registry.map_imperatively(FoodImage, food_images)
    mapper_registry.map_imperatively(User, users)
    mapper = mapper_registry.map_imperatively(
        Food,
        foods,
        properties={
            "food_brands": relationship(FoodBrand),
            "food_food_categories": relationship(FoodFoodCategory),
            "food_ingredients": relationship(FoodIngredient),
            "food_images": relationship(FoodImage),
            "users": relationship(User)
        }
    )
    return mapper


def food_brand_mappers():
    mapper_registry.map_imperatively(Food, foods)
    mapper = mapper_registry.map_imperatively(
        FoodBrand,
        food_brands,
        properties={"foods": Food}
    )
    return mapper


def food_category_mappers():
    mapper = mapper_registry.map_imperatively(FoodCategory, food_categories)
    return mapper


def food_food_category_mappers():
    mapper_registry.map_imperatively(FoodCategory, food_categories)
    mapper_registry.map_imperatively(Food, foods)
    mapper = mapper_registry.map_imperatively(
        FoodFoodCategory,
        food_food_categories,
        properties={
            "food_categories": relationship(FoodCategory),
            "foods": relationship(Food)
        }
    )
    return mapper


def food_image_mappers():
    mapper_registry.map_imperatively(Food, foods)
    mapper_registry.map_imperatively(FoodImage, food_images)
    mapper = mapper_registry.map_imperatively(
        FoodImage,
        food_images,
        properties={
            "foods": relationship(Food),
            "food_images": relationship(FoodImage)
        }
    )
    return mapper


def food_ingredient_mappers():
    mapper_registry.map_imperatively(Food, foods)
    mapper = mapper_registry.map_imperatively(
        FoodIngredient,
        food_ingredients,
        properties={"foods": relationship(Food)}
    )
    return mapper


def food_rating_mappers():
    mapper_registry.map_imperatively(Food, foods)
    mapper_registry.map_imperatively(User, users)
    mapper_registry.map_imperatively(FoodRatingReview, food_rating_reviews)
    mapper = mapper_registry.map_imperatively(
        FoodRating,
        food_ratings,
        properties={
            "foods": relationship(Food),
            "users": relationship(User),
            "food_rating_reviews": relationship(FoodRatingReview)
        }
    )
    return mapper


def food_rating_image_mappers():
    mapper_registry.map_imperatively(FoodRating, food_ratings)
    mapper = mapper_registry.map_imperatively(
        FoodRatingImage,
        food_rating_images,
        properties={
            "food_ratings": relationship(FoodRating),
            "food_rating_images": relationship(FoodRatingImage)
        }
    )
    return mapper


def food_rating_review_mappers():
    mapper_registry.map_imperatively(FoodRating, food_ratings)
    mapper_registry.map_imperatively(FoodReview, food_reviews)
    mapper = mapper_registry.map_imperatively(
        FoodRatingReview,
        food_rating_reviews,
        properties={
            "food_ratings": relationship(FoodRating),
            "food_reviews": relationship(FoodReview)
        }
    )
    return mapper


def food_review_mappers():
    mapper_registry.map_imperatively(User, users)
    mapper = mapper_registry.map_imperatively(
        FoodReview,
        food_reviews,
        properties={"users": relationship(User)}
    )
    return mapper


def ingredient_mappers():
    mapper = mapper_registry.map_imperatively(Ingredient, ingredients)
    return mapper
# endregion


# region missions
def mission_mappers():
    mapper_registry.map_imperatively(FeedMission, feed_missions)
    mapper_registry.map_imperatively(MissionCategory, mission_categories)
    mapper_registry.map_imperatively(MissionComment, mission_comments)
    mapper_registry.map_imperatively(MissionGround, mission_grounds)
    # mapper_registry.map_imperatively(MissionGroundText, mission_ground_texts)
    mapper_registry.map_imperatively(MissionImage, mission_images)
    mapper_registry.map_imperatively(MissionNotice, mission_notices)
    mapper_registry.map_imperatively(MissionProduct, mission_products)
    # mapper_registry.map_imperatively(MissionPush, mission_pushes)
    mapper_registry.map_imperatively(MissionRank, mission_ranks)
    mapper_registry.map_imperatively(MissionRefundProduct, mission_refund_products)
    mapper_registry.map_imperatively(MissionStat, mission_stats)
    mapper_registry.map_imperatively(User, users)
    mapper = mapper_registry.map_imperatively(
        Mission,
        missions,
        properties={
            "feed_missions": relationship(FeedMission),
            "mission_categories": relationship(MissionCategory),
            "mission_comments": relationship(MissionComment),
            "mission_grounds": relationship(MissionGround),
            # "mission_ground_texts": relationship(MissionGroundText),
            "mission_images": relationship(MissionImage),
            "mission_notices": relationship(MissionNotice),
            "mission_products": relationship(MissionProduct),
            # "mission_pushes": relationship(MissionPush),
            "mission_ranks": relationship(MissionRank),
            "mission_refund_products": relationship(MissionRefundProduct),
            "mission_stats": relationship(MissionStat),
            "users": relationship(User)
        }
    )
    return mapper


def mission_category_mappers():
    mapper = mapper_registry.map_imperatively(
        MissionCategory,
        mission_categories,
        properties={
            "mission_categories": relationship(MissionCategory)
        }
    )
    return mapper


def mission_comment_mappers():
    mapper_registry.map_imperatively(Mission, missions)
    mapper_registry.map_imperatively(User, users)
    mapper = mapper_registry.map_imperatively(
        MissionComment,
        mission_comments,
        properties={
            "missions": relationship(Mission),
            "users": relationship(User)
        }
    )
    return mapper


def mission_ground_mappers():
    mapper_registry.map_imperatively(Mission, missions)
    mapper = mapper_registry.map_imperatively(MissionGround, mission_grounds, properties={"missions": relationship(Mission)})
    return mapper


def mission_ground_text_mappers():
    mapper_registry.map_imperatively(Mission, missions)
    mapper = mapper_registry.map_imperatively(MissionGround, mission_ground_texts, properties={"missions": relationship(Mission)})
    return mapper


def mission_image_mappers():
    mapper_registry.map_imperatively(Mission, missions)
    mapper = mapper_registry.map_imperatively(MissionGround, mission_images, properties={"missions": relationship(Mission)})
    return mapper


def mission_notice_mappers():
    mapper_registry.map_imperatively(Mission, missions)
    mapper_registry.map_imperatively(MissionNoticeImage, mission_notice_images)
    mapper = mapper_registry.map_imperatively(
        MissionNotice,
        mission_notices,
        properties={
            "missions": relationship(Mission),
            "mission_notice_images": relationship(MissionNoticeImage)
        }
    )
    return mapper


def mission_notice_image_mappers():
    mapper_registry.map_imperatively(MissionNotice, mission_notices)
    mapper = mapper_registry.map_imperatively(MissionNoticeImage, mission_notice_images, properties={"mission_notices": relationship(MissionNotice)})
    return mapper


def mission_product_mappers():
    mapper_registry.map_imperatively(Food, foods)
    mapper_registry.map_imperatively(Mission, missions)
    mapper_registry.map_imperatively(OutsideProduct, outside_products)
    mapper_registry.map_imperatively(Product, products)
    mapper = mapper_registry.map_imperatively(
        MissionGround,
        mission_products,
        properties={
            "foods": relationship(Food),
            "missions": relationship(Mission),
            "outside_products": relationship(OutsideProduct),
            "products": relationship(Product)
        }
    )
    return mapper


def mission_rank_mappers():
    mapper_registry.map_imperatively(Mission, missions)
    mapper_registry.map_imperatively(MissionRankUser, mission_rank_users)
    mapper = mapper_registry.map_imperatively(
        MissionRank,
        mission_ranks,
        properties={
            "missions": relationship(Mission),
            "mission_rank_users": relationship(MissionRankUser),
        }
    )
    return mapper


def mission_rank_user_mappers():
    mapper_registry.map_imperatively(MissionRank, mission_ranks)
    mapper_registry.map_imperatively(User, users)
    mapper = mapper_registry.map_imperatively(
        MissionRankUser,
        mission_rank_users,
        properties={
            "mission_ranks": relationship(MissionRank),
            "users": relationship(User)
        }
    )
    return mapper


def mission_refund_product_mappers():
    mapper_registry.map_imperatively(Mission, missions)
    mapper_registry.map_imperatively(Product, products)
    mapper_registry.map_imperatively(Food, foods)
    mapper = mapper_registry.map_imperatively(
        MissionRefundProduct,
        mission_refund_products,
        properties={
            "missions": relationship(Mission),
            "products": relationship(Product),
            "foods": relationship(Food),
        }
    )
    return mapper


def mission_stat_mappers():
    mapper_registry.map_imperatively(Mission, missions)
    mapper_registry.map_imperatively(User, users)
    mapper = mapper_registry.map_imperatively(
        MissionStat,
        mission_stats,
        properties={
            "missions": relationship(Mission),
            "users": relationship(User)
        }
    )
    return mapper
# endregion


# region notice
def notice_mappers():
    mapper_registry.map_imperatively(NoticeImage, notice_images)
    mapper_registry.map_imperatively(NoticeComment, notice_comments)
    mapper = mapper_registry.map_imperatively(
        Notice,
        notices,
        properties={
            "notice_images": relationship(NoticeImage),
            "notice_comments": relationship(NoticeComment)
        }
    )
    return mapper


def notice_comment_mappers():
    mapper_registry.map_imperatively(Notice, notices)
    mapper_registry.map_imperatively(User, users)

    mapper = mapper_registry.map_imperatively(
        NoticeComment,
        notice_comments,
        properties={
            "notices": relationship(Notice),
            "users": relationship(User)
        }
    )
    return mapper


def notice_image_mappers():
    mapper_registry.map_imperatively(Notice, notices)
    mapper = mapper_registry.map_imperatively(NoticeImage, notice_images, properties={"notices": relationship(Notice)})
    return mapper
# endregion


# region notification
def notification_mappers():
    mapper_registry.map_imperatively(Board, boards)
    mapper_registry.map_imperatively(BoardComment, board_comments)
    mapper_registry.map_imperatively(Feed, feeds)
    mapper_registry.map_imperatively(FeedComment, feed_comments)
    mapper_registry.map_imperatively(Notice, notices)
    mapper_registry.map_imperatively(NoticeComment, notice_comments)
    mapper_registry.map_imperatively(Mission, missions)
    mapper_registry.map_imperatively(MissionComment, mission_comments)
    mapper_registry.map_imperatively(MissionStat, mission_stats)
    mapper_registry.map_imperatively(User, users)
    mapper_registry.map_imperatively(CommonCode, common_codes)

    mapper = mapper_registry.map_imperatively(
        Notification,
        notifications,
        properties={
            "board_comments": relationship(BoardComment),
            "boards": relationship(Board),
            "feed_comments": relationship(FeedComment),
            "feeds": relationship(Feed),
            "notices": relationship(Notice),
            "notice_comments": relationship(NoticeComment),
            "missions": relationship(Mission),
            "mission_comments": relationship(MissionComment),
            "mission_stats": relationship(MissionStat),
            "users": relationship(User, primaryjoin='Notification.user_id == User.id'),
            "common_codes": relationship(CommonCode)
        }
    )
    return mapper
# endregion


# region order
def order_mappers():
    mapper_registry.map_imperatively(User, users)
    mapper_registry.map_imperatively(OrderProduct, order_products)
    mapper = mapper_registry.map_imperatively(
        Order,
        orders,
        properties={
            "users": relationship(User),
            "order_products": relationship(OrderProduct),
        })
    return mapper


def order_product_mappers():
    mapper_registry.map_imperatively(User, users)
    mapper_registry.map_imperatively(Product, products)
    mapper = mapper_registry.map_imperatively(
        OrderProduct,
        order_products,
        properties={
            "users": relationship(User),
            "products": relationship(Product)
        }
    )
    return mapper
# endregion


# region point histories
def point_history_mappers():
    mapper_registry.map_imperatively(User, users)
    mapper_registry.map_imperatively(Feed, feeds)
    # mapper_registry.map_imperatively(Order, orders)
    mapper_registry.map_imperatively(Mission, missions)
    mapper_registry.map_imperatively(FoodRating, food_ratings)
    mapper_registry.map_imperatively(FeedComment, feed_comments)
    mapper = mapper_registry.map_imperatively(
        PointHistory,
        point_histories,
        properties={
            "users": relationship(User),
            "feeds": relationship(Feed),
            # "orders": relationship(Order),
            "missions": relationship(Mission),
            "food_ratings": relationship(FoodRating),
            "feed_comments": relationship(FeedComment)
        }
    )
    return mapper
# endregion


# region product
def outside_product_mappers():
    mapper = mapper_registry.map_imperatively(OutsideProduct, outside_products)
    return mapper


def product_mappers():
    mapper_registry.map_imperatively(Brand, brands)
    mapper_registry.map_imperatively(ProductCategory, product_categories)
    mapper = mapper_registry.map_imperatively(
        Product,
        products,
        properties={
            "brands": relationship(Brand),
            "product_categories": relationship(ProductCategory)
        }
    )
    return mapper


def product_category_mappers():
    mapper = mapper_registry.map_imperatively(ProductCategory, product_categories)
    return mapper
# endregion


# region push
def push_history_mappers():
    mapper_registry.map_imperatively(User, users)
    mapper = mapper_registry.map_imperatively(
        PushHistory,
        push_histories,
        properties={
            "users": relationship(User),
        }
    )
    return mapper
# endregion


# region
def report_mappers():
    mapper_registry.map_imperatively(User, users)
    mapper_registry.map_imperatively(Feed, feeds)
    mapper_registry.map_imperatively(Mission, missions)
    mapper_registry.map_imperatively(FeedComment, feed_comments)
    mapper_registry.map_imperatively(NoticeComment, notice_comments)
    mapper_registry.map_imperatively(MissionComment, mission_comments)
    mapper = mapper_registry.map_imperatively(
        Report,
        reports,
        properties={
            "users": relationship(User, primaryjoin='Report.user_id == User.id'),
            "feeds": relationship(Feed),
            "missions": relationship(Mission),
            "feed_comments": relationship(FeedComment),
            "notice_comments": relationship(NoticeComment),
            "mission_comments": relationship(MissionComment),
        }
    )

# endregion


# region users
def user_mappers():
    mapper_registry.map_imperatively(UserStat, user_stats)
    mapper = mapper_registry.map_imperatively(User, users, properties={"user_stats": relationship(UserStat)})
    return mapper


def user_favorite_category_mappers():
    mapper_registry.map_imperatively(MissionCategory, mission_categories)  # Foreign Key mapping
    mapper_registry.map_imperatively(User, users)  # Foreign Key mapping

    user_favorite_category_mapper = mapper_registry.map_imperatively(
        UserFavoriteCategory,
        user_favorite_categories,
        properties={
            "mission_categories": relationship(MissionCategory),
            "users": relationship(User)
        }
    )
    return user_favorite_category_mapper


def user_stat_mappers():
    mapper_registry.map_imperatively(User, users)
    user_stat_mapper = mapper_registry.map_imperatively(UserStat, user_stats, properties={"users": relationship(User)})
    return user_stat_mapper


def user_wallpaper_mappers():
    mapper_registry.map_imperatively(User, users)
    user_wallpaper_mapper = mapper_registry.map_imperatively(UserWallpaper, user_wallpapers, properties={"users": relationship(User)})
    return user_wallpaper_mapper
# endregion


# region version
def version_mappers():
    version_mapper = mapper_registry.map_imperatively(Version, versions)
    return version_mapper
# endregion


# endregion
