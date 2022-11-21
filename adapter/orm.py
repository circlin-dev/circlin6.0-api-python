from sqlalchemy import Table, Column, Integer, TIMESTAMP, text, Float, ForeignKey, JSON
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR, TINYINT, DOUBLE, TEXT, INTEGER
from sqlalchemy.orm import registry, relationship

from domain.board import Board, BoardCategory, BoardComment, BoardImage, BoardLike
from domain.common_code import CommonCode
from domain.feed import Feed, FeedComment, FeedImage, FeedMission
from domain.file import File
from domain.mission import Mission, MissionCategory, MissionComment, MissionStat
from domain.notice import Notice, NoticeComment
from domain.notification import Notification
from domain.push import PushHistory
from domain.user import User, UserFavoriteCategory
from domain.version import Version

mapper_registry = registry()

# region tables

# region board
boards = Table(
    "boards",
    mapper_registry.metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("user_id", ForeignKey('users.id'), nullable=False, index=True),
    Column("board_category_id", ForeignKey('board_categories.id'), nullable=False, index=True),
    Column("body", TEXT(collation='utf8mb4_unicode_ci'), nullable=False),
    Column("deleted_at", TIMESTAMP),
    Column("is_show", TINYINT, nullable=False, server_default=text("'1'"))
)


board_categories = Table(
    "board_categories",
    mapper_registry.metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("title", VARCHAR(255), nullable=False)
)


board_comments = Table(
    "board_comments",
    mapper_registry.metadata,
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


board_files = Table(
    "board_files",
    mapper_registry.metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("board_id", ForeignKey('boards.id'), nullable=False, index=True),
    Column("order", TINYINT, server_default=text("'0'")),
    Column("type", VARCHAR(255), nullable=False, comment='이미지인지 비디오인지 (image / video)'),
    Column("file_id", ForeignKey('files.id'), nullable=False, index=True, comment='원본 이미지'),
)


board_images = Table(
    "board_images",
    mapper_registry.metadata,
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
    mapper_registry.metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("board_id", ForeignKey('boards.id'), nullable=False, index=True),
    Column("user_id", ForeignKey('users.id'), nullable=False, index=True)
)
# endregion


# region common_code
common_codes = Table(
    "common_codes",
    mapper_registry.metadata,
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


# region feed
feeds = Table(
    "feeds",
    mapper_registry.metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("user_id", BIGINT(unsigned=True), ForeignKey('users.id'), nullable=False, index=True),
    Column("content", TEXT, nullable=False),
    Column("is_hidden", TINYINT, nullable=False, server_default=text("'0'"), comment='비밀글 여부'),
    Column("deleted_at", TIMESTAMP),
    Column("distance", Float(8, True), comment='달린 거리'),
    Column("laptime", Integer, comment='달린 시간'),
    Column("distance_origin", Float(8, True), comment='인식된 달린 거리'),
    Column("laptime_origin", Integer, comment='인식된 달린 시간'),
)


feed_comments = Table(
    "feed_comments",
    mapper_registry.metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("feed_id", BIGINT(unsigned=True), ForeignKey('feeds.id'), nullable=False, index=True),
    Column("user_id", BIGINT(unsigned=True), ForeignKey('users.id'), nullable=False, index=True),
    Column("group", Integer, nullable=False, server_default=text("'0'")),
    Column("depth", TINYINT, nullable=False, server_default=text("'0'")),
    Column("comment", TEXT, nullable=False),
    Column("deleted_at", TIMESTAMP),
)


feed_images = Table(
    "feed_images",
    mapper_registry.metadata,
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
    mapper_registry.metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("feed_id", BIGINT(unsigned=True), ForeignKey('feeds.id'), nullable=False, index=True),
    Column("mission_stat_id", BIGINT(unsigned=True), ForeignKey('mission_stats.id'), index=True),
    Column("mission_id", BIGINT(unsigned=True), ForeignKey('missions.id'), nullable=False, index=True),
)
# endregion


# region file
files = Table(
    "files",
    mapper_registry.metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("pathname", VARCHAR(255), nullable=False),
    Column("original_name", VARCHAR(255), nullable=False),
    Column("mime_type", VARCHAR(255), nullable=False),
    Column("size", INTEGER(unsigned=True)),
    Column("width", INTEGER(unsigned=True)),
    Column("height", INTEGER(unsigned=True)),
    Column("original_file_id", BIGINT(unsigned=True)),
)
# endregion


# region missions
missions = Table(
    "missions",
    mapper_registry.metadata,
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
    mapper_registry.metadata,
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
    mapper_registry.metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("mission_id", BIGINT(unsigned=True), ForeignKey('missions.id'), nullable=False, index=True),
    Column("user_id", BIGINT(unsigned=True), ForeignKey('users.id'), nullable=False, index=True),
    Column("group", INTEGER, nullable=False, server_default=text("'0'")),
    Column("depth", TINYINT, nullable=False, server_default=text("'0'")),
    Column("comment", TEXT, nullable=False),
    Column("deleted_at", TIMESTAMP)
)


mission_stats = Table(
    "mission_stats",
    mapper_registry.metadata,
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
    mapper_registry.metadata,
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
    mapper_registry.metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("notice_id", BIGINT(unsigned=True), ForeignKey('notices.id'), nullable=False, index=True),
    Column("user_id", BIGINT(unsigned=True), ForeignKey('users.id'), nullable=False, index=True),
    Column("group", Integer, nullable=False, server_default=text("'0'")),
    Column("depth", TINYINT, nullable=False, server_default=text("'0'")),
    Column("comment", TEXT, nullable=False),
    Column("deleted_at", TIMESTAMP),
)
# endregion


# region notification
notifications = Table(
    "notifications",
    mapper_registry.metadata,
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


# region push
push_histories = Table(
    "push_histories",
    mapper_registry.metadata,
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


# region user
users = Table(
    "users",
    mapper_registry.metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True, nullable=False),
    Column("created_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("login_method", VARCHAR(32), default='email'),
    Column("sns_email", VARCHAR(255)),
    Column("email", VARCHAR(255), nullable=False),
    Column("email_verified_at", TIMESTAMP),
    Column("password", VARCHAR(255), nullable=False),
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
    mapper_registry.metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True),
    Column("created_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    Column("user_id", BIGINT(unsigned=True), ForeignKey('users.id'), nullable=False, index=True),
    Column("mission_category_id", BIGINT(unsigned=True), ForeignKey('mission_categories.id'), nullable=False, index=True)
)
# endregion


# region version
versions = Table(
    "versions",
    mapper_registry.metadata,
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

# region boards
def board_mappers():
    mapper_registry.map_imperatively(BoardCategory, board_categories)
    mapper_registry.map_imperatively(BoardComment, board_comments)
    mapper_registry.map_imperatively(BoardImage, board_images)
    mapper_registry.map_imperatively(File, files)
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


# def board_file_mappers():
#     mapper_registry.map_imperatively(Board, boards)
#     mapper_registry.map_imperatively(File, files)
#
#     mapper = mapper_registry.map_imperatively(
#         BoardImage,
#         board_files,
#         properties={
#             "boards": relationship(Board),
#             "files": relationship(File)
#         }
#     )
#     return mapper


def board_image_mappers():
    mapper_registry.map_imperatively(Board, boards)

    mapepr = mapper_registry.map_imperatively(
        BoardImage,
        board_images,
        properties={
            "boards": relationship(Board),
            "board_images": relationship(BoardImage)
        }
    )


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


# region common_coe
def common_code_mappers():
    mapper = mapper_registry.map_imperatively(
        CommonCode,
        common_codes,
        properties={"notifications": relationship(notifications)}
    )
    return mapper
# endregion


# region feed
def feed_mappers():
    mapper_registry.map_imperatively(User, users)
    mapper_registry.map_imperatively(FeedImage, feed_images)
    mapper = mapper_registry.map_imperatively(
        Feed,
        feeds,
        properties={
            "users": relationship(User),
            "feed_images": relationship(FeedImage)
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
    mapper_registry.map_imperatively(MissionStat, mission_stats)
    mapper = mapper_registry.map_imperatively(
        FeedMission,
        feed_missions,
        properties={
            "feeds": relationship(Feed),
            "missions": relationship(Mission),
            "mission_stats": relationship(MissionStat)
        }
    )
    return mapper

# endregion


# region file
# def file_mappers():
#     mapper_registry.map_imperatively(BoardFile, board_files)
#     mapper = mapper_registry.map_imperatively(
#         File,
#         files,
#         properties={
#             "board_files": relationship(BoardFile),
#         }
#     )
#     return mapper

# endregion


# region missions
def mission_mappers():
    mapper_registry.map_imperatively(MissionCategory, mission_categories)
    mapper_registry.map_imperatively(User, users)
    mapper = mapper_registry.map_imperatively(
        Mission,
        missions,
        properties={
            "mission_categories": relationship(MissionCategory),
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
    mapper = mapper_registry.map_imperatively(
        Notice,
        notices
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
# endregion


# region notification
def notification_mappers():
    mapper_registry.map_imperatively(BoardComment, board_comments)
    mapper_registry.map_imperatively(Board, boards)
    mapper_registry.map_imperatively(FeedComment, feed_comments)
    mapper_registry.map_imperatively(Feed, feeds)
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


# region users
def user_mappers():
    user_mapper = mapper_registry.map_imperatively(User, users)
    return user_mapper


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
# endregion


# region version
def version_mappers():
    version_mapper = mapper_registry.map_imperatively(Version, versions)
    return version_mapper
# endregion


# endregion
