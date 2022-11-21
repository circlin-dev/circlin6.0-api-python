# coding: utf-8
from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Index, Integer, JSON, String, TIMESTAMP, Table, Text, Time, text
from sqlalchemy.dialects.mysql import BIGINT, CHAR, INTEGER, LONGTEXT, TEXT, TINYINT, VARCHAR
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Area(Base):
    __tablename__ = 'areas'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    code = Column(VARCHAR(255), nullable=False, index=True)
    name = Column(VARCHAR(255), nullable=False)
    name_en = Column(VARCHAR(255))


class BoardCategory(Base):
    __tablename__ = 'board_categories'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    title = Column(String(255, 'utf8mb4_unicode_ci'), nullable=False)


class ChatRoom(Base):
    __tablename__ = 'chat_rooms'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    title = Column(VARCHAR(255))
    is_group = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    deleted_at = Column(TIMESTAMP)


class Area(Base):
    __tablename__ = 'areas'
    __table_args__ = {'schema': 'circlin'}

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    code = Column(VARCHAR(255), nullable=False, index=True)
    name = Column(VARCHAR(255), nullable=False)
    name_en = Column(VARCHAR(255))


class CommonCode(Base):
    __tablename__ = 'common_codes'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    ctg_lg = Column(VARCHAR(255))
    ctg_md = Column(VARCHAR(255))
    ctg_sm = Column(VARCHAR(255), nullable=False)
    content_ko = Column(VARCHAR(255), nullable=False)
    content_en = Column(VARCHAR(255))
    description = Column(VARCHAR(255))


class Content(Base):
    __tablename__ = 'contents'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    code = Column(VARCHAR(255), nullable=False, unique=True)
    type = Column(VARCHAR(255), nullable=False)
    title = Column(VARCHAR(255), nullable=False)
    description = Column(VARCHAR(255))
    channel = Column(VARCHAR(255), nullable=False)
    thumbnail_image = Column(VARCHAR(255))


class DeleteUser(Base):
    __tablename__ = 'delete_users'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    user_id = Column(BIGINT, nullable=False, index=True, comment='기존에는 user 삭제해서 fk 못검')
    reason = Column(TEXT, comment='탈퇴사유')


class FailedJob(Base):
    __tablename__ = 'failed_jobs'

    id = Column(BIGINT, primary_key=True)
    uuid = Column(VARCHAR(255), nullable=False, unique=True)
    connection = Column(TEXT, nullable=False)
    queue = Column(TEXT, nullable=False)
    payload = Column(LONGTEXT, nullable=False)
    exception = Column(LONGTEXT, nullable=False)
    failed_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))


class File(Base):
    __tablename__ = 'files'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    pathname = Column(String(255, 'utf8mb4_unicode_ci'), nullable=False)
    original_name = Column(String(255, 'utf8mb4_unicode_ci'), nullable=False)
    mime_type = Column(String(255, 'utf8mb4_unicode_ci'), nullable=False)
    size = Column(INTEGER)
    width = Column(INTEGER)
    height = Column(INTEGER)
    original_file_id = Column(BIGINT)

    food_ratings = relationship('FoodRating', secondary='food_rating_files')


class Flavor(Base):
    __tablename__ = 'flavors'
    __table_args__ = {'comment': '맛 태그_20220510(최건우)'}

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    value = Column(String(255, 'utf8mb4_unicode_ci'), nullable=False, unique=True)


class FoodBrand(Base):
    __tablename__ = 'food_brands'
    __table_args__ = {'comment': '식단 브랜드 테이블_20220510(최건우)'}

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    type = Column(String(255, 'utf8mb4_unicode_ci'), nullable=False, comment='4 Types: 레스토랑, 체인점 | 슈퍼마켓, 마트 | 인기 브랜드 | 내 요리')
    title = Column(String(255, 'utf8mb4_unicode_ci'), nullable=False, comment='type이 내 요리일 때는 기본값 적용, 그 외 세 가지 type일 때는 업체명을 입력 받음.')


class FoodCategory(Base):
    __tablename__ = 'food_categories'
    __table_args__ = {'comment': '식단 카테고리 테이블_20220510(최건우)'}

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    large = Column(String(255, 'utf8mb4_unicode_ci'), comment='식단 대분류')
    medium = Column(String(255, 'utf8mb4_unicode_ci'), comment='식단 중분류')
    small = Column(String(255, 'utf8mb4_unicode_ci'), comment='식단 소분류')


class Ingredient(Base):
    __tablename__ = 'ingredients'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    value = Column(String(255), nullable=False, unique=True)


class Job(Base):
    __tablename__ = 'jobs'

    id = Column(BIGINT, primary_key=True)
    queue = Column(VARCHAR(255), nullable=False, index=True)
    payload = Column(LONGTEXT, nullable=False)
    attempts = Column(TINYINT, nullable=False)
    reserved_at = Column(INTEGER)
    available_at = Column(INTEGER, nullable=False)
    created_at = Column(INTEGER, nullable=False)


class Keyword(Base):
    __tablename__ = 'keywords'
    __table_args__ = {'comment': '추천 검색어'}

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    type = Column(VARCHAR(255), nullable=False, comment='어디에 노출 : product/place')
    order = Column(Integer, nullable=False, server_default=text("'0'"), comment='정렬 (낮은게 우선)')
    area_code = Column(VARCHAR(255))
    keyword = Column(VARCHAR(255), nullable=False)
    deleted_at = Column(TIMESTAMP)


class Migration(Base):
    __tablename__ = 'migrations'

    id = Column(INTEGER, primary_key=True)
    migration = Column(VARCHAR(255), nullable=False)
    batch = Column(Integer, nullable=False)


class MissionCategory(Base):
    __tablename__ = 'mission_categories'
    __table_args__ = {'comment': '카테고리'}

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    mission_category_id = Column(ForeignKey('mission_categories.id'), index=True)
    title = Column(VARCHAR(255), nullable=False)
    emoji = Column(VARCHAR(255), comment='타이틀 앞의 이모지')
    description = Column(TEXT, comment='카테고리 설명')

    mission_category = relationship('MissionCategory', remote_side=[id])


class MissionEtc(Base):
    __tablename__ = 'mission_etc'
    __table_args__ = {'comment': 'missions에 사용되는 텍스트나 이미지 테이블'}

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    mission_id = Column(BIGINT, nullable=False, index=True)
    deleted_at = Column(TIMESTAMP)
    youtube = Column(VARCHAR(50), server_default=text("''"), comment='유튜브코드(링크)')
    youtube_text = Column(VARCHAR(500), server_default=text("''"), comment='유튜브코드(링크) 딱히안쓸거임')
    logo = Column(VARCHAR(150), server_default=text("''"), comment='파트너십 로고')
    apply_image1 = Column(VARCHAR(200), server_default=text("'='"), comment='신청시 안내이미지1')
    apply_image2 = Column(VARCHAR(200), server_default=text("'='"), comment='신청시 안내이미지1')
    apply_image3 = Column(VARCHAR(200), server_default=text("'='"), comment='신청시 안내이미지1')
    apply_image4 = Column(VARCHAR(200), server_default=text("'='"), comment='신청시 안내이미지1')
    apply_image5 = Column(VARCHAR(200), server_default=text("'='"), comment='신청시 안내이미지1')
    apply_image6 = Column(VARCHAR(200), server_default=text("'='"), comment='신청시 안내이미지1')
    apply_image7 = Column(VARCHAR(200), server_default=text("'='"), comment='신청시 안내이미지1')
    subtitle_1 = Column(VARCHAR(400), comment='신청시 안내텍스트')
    subtitle_2 = Column(VARCHAR(400), comment='신청시 안내텍스트')
    subtitle_3 = Column(VARCHAR(400), comment='신청시 안내텍스트')
    subtitle_4 = Column(VARCHAR(400), comment='신청시 안내텍스트')
    subtitle_5 = Column(VARCHAR(400), comment='신청시 안내텍스트')
    subtitle_6 = Column(VARCHAR(400), comment='신청시 안내텍스트')
    subtitle_7 = Column(VARCHAR(400), comment='신청시 안내텍스트')
    desc1 = Column(VARCHAR(400), comment='미션 운영유저1')
    desc2 = Column(VARCHAR(400), comment='미션 운영유저2')
    intro_image_1 = Column(VARCHAR(400), comment='미션 상세설명')
    intro_image_2 = Column(VARCHAR(400), comment='미션 상세설명')
    intro_image_3 = Column(VARCHAR(400), comment='미션 상세설명')
    intro_image_4 = Column(VARCHAR(400), comment='미션 상세설명')
    intro_image_5 = Column(VARCHAR(400), comment='미션 상세설명')
    intro_image_6 = Column(VARCHAR(400), comment='미션 상세설명')
    intro_image_7 = Column(VARCHAR(400), comment='미션 상세설명')
    intro_image_8 = Column(VARCHAR(400), comment='미션 상세설명')
    intro_image_9 = Column(VARCHAR(400), comment='미션 상세설명')
    intro_image_10 = Column(VARCHAR(400), comment='미션 상세설명')
    bg_image = Column(VARCHAR(400), comment='룸 배경이미지')
    video_1 = Column(VARCHAR(400), comment='신청페이지 동영상')
    info_image_1 = Column(VARCHAR(400), comment='룸 우측이미지1')
    info_image_2 = Column(VARCHAR(400), comment='룸 우측이미지2')
    info_image_3 = Column(VARCHAR(400), comment='이벤트탭 이미지1')
    info_image_4 = Column(VARCHAR(400), comment='이벤트탭 이미지2')
    info_image_5 = Column(VARCHAR(400), comment='이벤트탭 이미지3')
    info_image_6 = Column(VARCHAR(400), comment='이벤트탭 이미지4')
    info_image_7 = Column(VARCHAR(400), comment='백업용')
    ai_text1 = Column(JSON, comment='AiText (key:cond,value:text)')
    ai_text2 = Column(JSON, comment='AiText2 (key:cond,value:text)')


class Notice(Base):
    __tablename__ = 'notices'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    title = Column(VARCHAR(255), nullable=False)
    content = Column(TEXT, nullable=False)
    link_text = Column(TEXT)
    link_url = Column(TEXT)
    is_show = Column(TINYINT(1), nullable=False, server_default=text("'1'"))
    deleted_at = Column(TIMESTAMP)


class OutsideProduct(Base):
    __tablename__ = 'outside_products'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    product_id = Column(BIGINT, comment='상품 고유 ID')
    brand = Column(VARCHAR(255))
    title = Column(VARCHAR(255), nullable=False)
    image = Column(VARCHAR(255))
    url = Column(VARCHAR(255), nullable=False, unique=True)
    price = Column(Integer, nullable=False)


class Place(Base):
    __tablename__ = 'places'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    address = Column(VARCHAR(255), nullable=False)
    title = Column(VARCHAR(255), nullable=False, index=True)
    description = Column(VARCHAR(255))
    image = Column(VARCHAR(500))
    lat = Column(Float(10, True), comment='위도')
    lng = Column(Float(10, True), comment='경도')
    url = Column(VARCHAR(255))
    is_important = Column(TINYINT(1), nullable=False, server_default=text("'0'"))


class ProductCategory(Base):
    __tablename__ = 'product_categories'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    title = Column(VARCHAR(255), nullable=False)
    deleted_at = Column(TIMESTAMP)


t_products_view = Table(
    'products_view', metadata,
    Column('id', Integer, server_default=text("'0'")),
    Column('생성일', Integer, server_default=text("'0'")),
    Column('브랜드', Integer, server_default=text("'0'")),
    Column('카테고리', Integer, server_default=text("'0'")),
    Column('제품코드', Integer, server_default=text("'0'")),
    Column('제품명', Integer, server_default=text("'0'")),
    Column('product_option_id', Integer, server_default=text("'0'")),
    Column('옵션그룹', Integer, server_default=text("'0'")),
    Column('옵션명', Integer, server_default=text("'0'")),
    Column('제품원가', Integer, server_default=text("'0'")),
    Column('제품판매가', Integer, server_default=text("'0'")),
    Column('배송비', Integer, server_default=text("'0'")),
    Column('옵션가', Integer, server_default=text("'0'")),
    Column('최종가격', Integer, server_default=text("'0'")),
    Column('제품노출여부', Integer, server_default=text("'0'")),
    Column('제품상태', Integer, server_default=text("'0'")),
    Column('옵션상태', Integer, server_default=text("'0'"))
)


class Session(Base):
    __tablename__ = 'sessions'

    id = Column(VARCHAR(255), primary_key=True)
    user_id = Column(BIGINT, index=True)
    ip_address = Column(VARCHAR(45))
    user_agent = Column(TEXT)
    payload = Column(TEXT, nullable=False)
    last_activity = Column(Integer, nullable=False, index=True)


class TelescopeEntry(Base):
    __tablename__ = 'telescope_entries'
    __table_args__ = (
        Index('telescope_entries_type_should_display_on_index_index', 'type', 'should_display_on_index'),
    )

    sequence = Column(BIGINT, primary_key=True)
    uuid = Column(CHAR(36), nullable=False, unique=True)
    batch_id = Column(CHAR(36), nullable=False, index=True)
    family_hash = Column(VARCHAR(255), index=True)
    should_display_on_index = Column(TINYINT(1), nullable=False, server_default=text("'1'"))
    type = Column(VARCHAR(20), nullable=False)
    content = Column(LONGTEXT, nullable=False)
    created_at = Column(DateTime, index=True)


t_telescope_monitoring = Table(
    'telescope_monitoring', metadata,
    Column('tag', VARCHAR(255), nullable=False)
)


class Version(Base):
    __tablename__ = 'versions'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    version = Column(VARCHAR(255), nullable=False, unique=True, comment='버전코드')
    type = Column(String(50, 'utf8mb4_unicode_ci'))
    description = Column(VARCHAR(255), comment='업데이트 내역')
    is_force = Column(TINYINT(1), nullable=False, comment='강제업데이트 여부')


class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'circlin', 'comment': '고객'}

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    login_method = Column(String(32, 'utf8mb4_unicode_ci'), server_default=text("'email'"), comment='회원가입 or 로그인 수단(default: email(이메일) | kakao(카카오톡) | naver(네이버) | facebook(페이스북) | apple(애플)')
    sns_email = Column(String(255, 'utf8mb4_unicode_ci'))
    email = Column(VARCHAR(255), nullable=False)
    email_verified_at = Column(TIMESTAMP, comment='이메일 인증 일시')
    password = Column(VARCHAR(255), nullable=False)
    nickname = Column(VARCHAR(255))
    family_name = Column(VARCHAR(255))
    given_name = Column(VARCHAR(255))
    name = Column(VARCHAR(255))
    gender = Column(VARCHAR(255))
    phone = Column(VARCHAR(255))
    phone_verified_at = Column(TIMESTAMP, comment='휴대폰 인증 일시')
    point = Column(Integer, nullable=False, server_default=text("'0'"))
    profile_image = Column(VARCHAR(255), comment='프로필 사진')
    greeting = Column(VARCHAR(255), comment='인사말')
    background_image = Column(VARCHAR(255), comment='배경 커버 이미지')
    area_code = Column(ForeignKey('circlin.areas.code'), index=True)
    area_updated_at = Column(TIMESTAMP, comment='지역 변경 일자')
    deleted_at = Column(TIMESTAMP)
    remember_token = Column(VARCHAR(100))
    device_type = Column(VARCHAR(255), comment='접속한 기기 종류(android/iphone)')
    socket_id = Column(VARCHAR(255), comment='채팅방 (nodejs) socket id')
    device_token = Column(VARCHAR(255), comment='푸시 전송 토큰')
    access_token = Column(VARCHAR(255))
    refresh_token = Column(VARCHAR(255))
    refresh_token_expire_in = Column(VARCHAR(255))
    last_login_at = Column(TIMESTAMP, comment='마지막 로그인 시점')
    last_login_ip = Column(VARCHAR(255), comment='마지막 로그인 IP')
    current_version = Column(VARCHAR(255), comment='마지막 접속 시점 버전')
    agree1 = Column(TINYINT(1), nullable=False, server_default=text("'0'"), comment='서비스 이용약관 동의')
    agree2 = Column(TINYINT(1), nullable=False, server_default=text("'0'"), comment='개인정보 수집 및 이용약관 동의')
    agree3 = Column(TINYINT(1), nullable=False, server_default=text("'0'"), comment='위치정보 이용약관 동의')
    agree4 = Column(TINYINT(1), nullable=False, server_default=text("'0'"), comment='이메일 마케팅 동의')
    agree5 = Column(TINYINT(1), nullable=False, server_default=text("'0'"), comment='SMS 마케팅 동의')
    agree_push = Column(TINYINT(1), nullable=False, server_default=text("'1'"), comment='푸시알림 동의')
    agree_push_mission = Column(TINYINT(1), nullable=False, server_default=text("'1'"), comment='미션알림 동의')
    agree_ad = Column(TINYINT(1), nullable=False, server_default=text("'1'"), comment='광고수신 동의')
    banner_hid_at = Column(TIMESTAMP, comment='배너 보지않기 시점')
    invite_code = Column(VARCHAR(255), comment='초대코드')
    recommend_user_id = Column(BIGINT)
    recommend_updated_at = Column(TIMESTAMP)
    lat = Column(Float(10, True), nullable=False, server_default=text("'37.4969117'"), comment='위도')
    lng = Column(Float(10, True), nullable=False, server_default=text("'127.0328342'"), comment='경도')

    area = relationship('Area')


class NoticeImage(Base):
    __tablename__ = 'notice_images'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    notice_id = Column(ForeignKey('notices.id'), nullable=False, index=True)
    order = Column(INTEGER, server_default=text("'0'"))
    type = Column(VARCHAR(255), nullable=False, comment='이미지인지 비디오인지 (image / video)')
    image = Column(VARCHAR(255), nullable=False)

    notice = relationship('Notice')


t_telescope_entries_tags = Table(
    'telescope_entries_tags', metadata,
    Column('entry_uuid', ForeignKey('telescope_entries.uuid', ondelete='CASCADE'), nullable=False),
    Column('tag', VARCHAR(255), nullable=False, index=True),
    Index('telescope_entries_tags_entry_uuid_tag_index', 'entry_uuid', 'tag')
)


class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'comment': '고객'}

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    login_method = Column(String(32, 'utf8mb4_unicode_ci'), server_default=text("'email'"), comment='회원가입 or 로그인 수단(default: email(이메일) | kakao(카카오톡) | naver(네이버) | facebook(페이스북) | apple(애플)')
    sns_email = Column(String(255, 'utf8mb4_unicode_ci'))
    email = Column(VARCHAR(255), nullable=False)
    email_verified_at = Column(TIMESTAMP, comment='이메일 인증 일시')
    password = Column(VARCHAR(255), nullable=False)
    nickname = Column(VARCHAR(255))
    family_name = Column(VARCHAR(255))
    given_name = Column(VARCHAR(255))
    name = Column(VARCHAR(255))
    gender = Column(VARCHAR(255))
    phone = Column(VARCHAR(255))
    phone_verified_at = Column(TIMESTAMP, comment='휴대폰 인증 일시')
    point = Column(Integer, nullable=False, server_default=text("'0'"))
    profile_image = Column(VARCHAR(255), comment='프로필 사진')
    greeting = Column(VARCHAR(255), comment='인사말')
    background_image = Column(VARCHAR(255), comment='배경 커버 이미지')
    area_code = Column(ForeignKey('areas.code'), index=True)
    area_updated_at = Column(TIMESTAMP, comment='지역 변경 일자')
    deleted_at = Column(TIMESTAMP)
    remember_token = Column(VARCHAR(100))
    device_type = Column(VARCHAR(255), comment='접속한 기기 종류(android/iphone)')
    socket_id = Column(VARCHAR(255), comment='채팅방 (nodejs) socket id')
    device_token = Column(VARCHAR(255), comment='푸시 전송 토큰')
    access_token = Column(VARCHAR(255))
    refresh_token = Column(VARCHAR(255))
    refresh_token_expire_in = Column(VARCHAR(255))
    last_login_at = Column(TIMESTAMP, comment='마지막 로그인 시점')
    last_login_ip = Column(VARCHAR(255), comment='마지막 로그인 IP')
    current_version = Column(VARCHAR(255), comment='마지막 접속 시점 버전')
    agree1 = Column(TINYINT(1), nullable=False, server_default=text("'0'"), comment='서비스 이용약관 동의')
    agree2 = Column(TINYINT(1), nullable=False, server_default=text("'0'"), comment='개인정보 수집 및 이용약관 동의')
    agree3 = Column(TINYINT(1), nullable=False, server_default=text("'0'"), comment='위치정보 이용약관 동의')
    agree4 = Column(TINYINT(1), nullable=False, server_default=text("'0'"), comment='이메일 마케팅 동의')
    agree5 = Column(TINYINT(1), nullable=False, server_default=text("'0'"), comment='SMS 마케팅 동의')
    agree_push = Column(TINYINT(1), nullable=False, server_default=text("'1'"), comment='푸시알림 동의')
    agree_push_mission = Column(TINYINT(1), nullable=False, server_default=text("'1'"), comment='미션알림 동의')
    agree_ad = Column(TINYINT(1), nullable=False, server_default=text("'1'"), comment='광고수신 동의')
    banner_hid_at = Column(TIMESTAMP, comment='배너 보지않기 시점')
    invite_code = Column(VARCHAR(255), comment='초대코드')
    recommend_user_id = Column(BIGINT)
    recommend_updated_at = Column(TIMESTAMP)
    lat = Column(Float(10, True), nullable=False, server_default=text("'37.4969117'"), comment='위도')
    lng = Column(Float(10, True), nullable=False, server_default=text("'127.0328342'"), comment='경도')

    area = relationship('Area')


class Admin(Base):
    __tablename__ = 'admins'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    description = Column(VARCHAR(255), nullable=False, comment='설명')
    type = Column(VARCHAR(255), nullable=False, comment='(ip,user)')
    ip = Column(VARCHAR(45), comment='허용할 IP 주소')
    user_id = Column(ForeignKey('users.id'), index=True, comment='허용할 유저 고유 ID')
    deleted_at = Column(TIMESTAMP)

    user = relationship('User')


class Block(Base):
    __tablename__ = 'blocks'
    __table_args__ = {'comment': '차단 기능을 위한 테이블. 차단의 대상은 오직 유저만'}

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    user_id = Column(ForeignKey('users.id'), ForeignKey('users.id'), index=True, comment='차단 요청자')
    target_id = Column(BIGINT, comment='user_id에 해당하는 유저가 차단하고자하는 상대 유저')

    user = relationship('User', primaryjoin='Block.user_id == User.id')
    user1 = relationship('User', primaryjoin='Block.user_id == User.id')


class Board(Base):
    __tablename__ = 'boards'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    user_id = Column(ForeignKey('users.id'), nullable=False, index=True)
    board_category_id = Column(ForeignKey('board_categories.id'), nullable=False, index=True)
    body = Column(Text(collation='utf8mb4_unicode_ci'), nullable=False)
    deleted_at = Column(TIMESTAMP)
    is_show = Column(TINYINT, nullable=False, server_default=text("'1'"))

    board_category = relationship('BoardCategory')
    user = relationship('User')


class Brand(Base):
    __tablename__ = 'brands'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    user_id = Column(ForeignKey('users.id'), index=True, comment='브랜드 소유자')
    name_ko = Column(VARCHAR(255), nullable=False, unique=True, server_default=text("''"), comment='브랜드명')
    name_en = Column(VARCHAR(255), comment='브랜드명')
    image = Column(VARCHAR(255))

    user = relationship('User')


class ErrorLog(Base):
    __tablename__ = 'error_logs'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    client_time = Column(TIMESTAMP)
    user_id = Column(ForeignKey('users.id'), index=True, comment='누가')
    ip = Column(VARCHAR(255))
    type = Column(VARCHAR(255), nullable=False, comment='에러 발생 플랫폼 (front, back)')
    message = Column(TEXT)
    stack_trace = Column(TEXT)

    user = relationship('User')


class Feed(Base):
    __tablename__ = 'feeds'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    user_id = Column(ForeignKey('users.id'), nullable=False, index=True)
    content = Column(TEXT, nullable=False)
    is_hidden = Column(TINYINT, nullable=False, server_default=text("'0'"), comment='비밀글 여부')
    deleted_at = Column(TIMESTAMP)
    distance = Column(Float(8, True), comment='달린 거리')
    laptime = Column(Integer, comment='달린 시간')
    distance_origin = Column(Float(8, True), comment='인식된 달린 거리')
    laptime_origin = Column(Integer, comment='인식된 달린 시간')

    user = relationship('User')


class Follow(Base):
    __tablename__ = 'follows'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    user_id = Column(ForeignKey('users.id'), nullable=False, index=True)
    target_id = Column(ForeignKey('users.id'), nullable=False, index=True)
    feed_notify = Column(TINYINT(1), nullable=False, server_default=text("'0'"))

    target = relationship('User', primaryjoin='Follow.target_id == User.id')
    user = relationship('User', primaryjoin='Follow.user_id == User.id')


class FoodReview(Base):
    __tablename__ = 'food_reviews'
    __table_args__ = {'comment': '식단 후기 리뷰 목록을 저장한 테이블(식단 카테고리의 자식 테이블)_20220510(최건우)'}

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    value = Column(String(255, 'utf8mb4_unicode_ci'), nullable=False, comment='식품 카테고리별 후기 태그값')
    user_id = Column(ForeignKey('users.id'), index=True)

    user = relationship('User')


class Food(Base):
    __tablename__ = 'foods'
    __table_args__ = {'comment': '식단(대표메뉴, 원물(재료), 제품) 테이블_20220510(최건우)'}

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    brand_id = Column(ForeignKey('food_brands.id'), index=True)
    large_category_title = Column(String(64, 'utf8mb4_unicode_ci'))
    title = Column(String(255, 'utf8mb4_unicode_ci'), nullable=False, comment='메뉴명, 재료명, 제품명')
    user_id = Column(ForeignKey('users.id'), nullable=False, index=True, comment='최초 작성자 id')
    type = Column(String(32, 'utf8mb4_unicode_ci'), comment='original(원물) | menu(대표메뉴), recipe(레시피), product(제품) => (원물의 조합)')
    barcode = Column(String(50, 'utf8mb4_unicode_ci'), comment='null이면 원물(재료) 또는 food_category=내 요리')
    container = Column(String(255, 'utf8mb4_unicode_ci'), comment='제공 용기 1단위: 1회제공량, 인분, 개, 컵, 조각, 접시, 봉지, 팩, 병, 캔, 그릇, 포\\n1용기당 제공량을 구한 후 쓴다.')
    amount_per_serving = Column(Float, comment='1container 당 제공량')
    total_amount = Column(Float, comment='총 제공량(중량, 포장 표기를 따름)')
    unit = Column(String(10, 'utf8mb4_unicode_ci'), comment='제공 단위: 그램(g) | 밀리리터(ml)')
    servings_per_container = Column(Float, server_default=text("'1'"), comment='1팩(번들) 당 제품 개수')
    price = Column(Float, comment='원본 판매처 정상가')
    calorie = Column(Float, comment='칼로리(총 내용량 기준, 포장 표기를 따름)')
    carbohydrate = Column(Float, comment='탄수화물 함유량(g)(포장 표기를 따름)')
    protein = Column(Float, comment='단백질 함유량(g)(포장 표기를 따름)')
    fat = Column(Float, comment='지방 함유량(g)(포장 표기를 따름)')
    sodium = Column(Float, comment='나트륨 함유량(mg)(포장 표기를 따름)')
    sugar = Column(Float, comment='당류 함유량(g)(포장 표기를 따름)')
    trans_fat = Column(Float, comment='트랜스 지방 함유량(g)(포장 표기를 따름)')
    saturated_fat = Column(Float, comment='포화 지방 함유량(g)(포장 표기를 따름)')
    cholesterol = Column(Float, comment='콜레스테롤 함유량(mg) (포장 표기를 따름)')
    url = Column(Text(collation='utf8mb4_unicode_ci'), comment='구매처 URL')
    approved_at = Column(TIMESTAMP, comment='관리자 승인 & 포인트 지급 일시')
    original_data = Column(JSON, comment='공공 API의 원본 데이터 값')
    deleted_at = Column(TIMESTAMP)

    brand = relationship('FoodBrand')
    user = relationship('User')
    ingredients = relationship('Ingredient', secondary='food_ingredients')


class Mission(Base):
    __tablename__ = 'missions'
    __table_args__ = {'comment': '미션'}

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    user_id = Column(ForeignKey('users.id'), nullable=False, index=True, comment='미션 제작자')
    mission_category_id = Column(ForeignKey('mission_categories.id'), nullable=False, index=True, comment='카테고리')
    title = Column(VARCHAR(255), index=True, comment='이름')
    description = Column(TEXT, comment='상세 내용')
    thumbnail_image = Column(String(255), comment='썸네일')
    reserve_started_at = Column(TIMESTAMP, comment='사전예약 시작 일시')
    reserve_ended_at = Column(TIMESTAMP, comment='사전예약 종료 일시')
    started_at = Column(TIMESTAMP, comment='시작 일시')
    ended_at = Column(TIMESTAMP, comment='종료 일시')
    mission_type = Column(String(255), comment='식단(제품) 기록 챌린지가 등장하며 미션의 인증 유형을 구분하기 위해 만들어짐(20220616, 최건우)')
    is_show = Column(TINYINT(1), nullable=False, server_default=text("'1'"), comment='노출 여부')
    is_event = Column(TINYINT(1), nullable=False, server_default=text("'0'"), comment='이벤트(스페셜 미션) 탭에 노출 여부')
    is_ground = Column(TINYINT(1), nullable=False, server_default=text("'0'"), comment='운동장으로 입장 여부')
    late_bookmarkable = Column(TINYINT(1), nullable=False, server_default=text("'1'"), comment='도중 참여 가능 여부')
    subtitle = Column(VARCHAR(255), comment='운동장 내부에 활용하는 짧은 이름')
    is_refund = Column(TINYINT(1), nullable=False, server_default=text("'0'"), comment='제품 체험 챌린지 여부')
    is_ocr = Column(TINYINT(1), nullable=False, server_default=text("'0'"), comment='OCR 필요한 미션인지')
    is_require_place = Column(TINYINT(1), nullable=False, server_default=text("'0'"), comment='장소 인증 필수 여부')
    is_not_duplicate_place = Column(TINYINT(1), nullable=False, server_default=text("'0'"), comment='일일 장소 중복 인증 불가 여부')
    is_tutorial = Column(TINYINT(1), nullable=False, server_default=text("'0'"), comment='맨 처음 가입 시 관심 카테고리로 설정하면 기본적으로 담길 미션 여부')
    event_order = Column(Integer, nullable=False, server_default=text("'0'"), comment='이벤트 페이지 정렬')
    deleted_at = Column(TIMESTAMP)
    event_type = Column(TINYINT(1), comment='~5.0 미션룸 구분')
    reward_point = Column(Integer, nullable=False, server_default=text("'0'"), comment='이벤트 성공 보상')
    success_count = Column(Integer, nullable=False, server_default=text("'0'"), comment='x회 인증 시 성공 팝업 (지금은 1,0으로 운영)')
    user_limit = Column(Integer, nullable=False, server_default=text("'0'"), comment='최대 참여자 수(0은 무제한)')
    treasure_started_at = Column(TIMESTAMP, comment='보물찾기 포인트 지급 시작일자')
    treasure_ended_at = Column(TIMESTAMP, comment='보물찾기 포인트 지급 종료일자')
    week_duration = Column(Integer, comment='총 주차')
    week_min_count = Column(Integer, comment='주당 최소 인증 횟수')

    mission_category = relationship('MissionCategory')
    user = relationship('User')


class NoticeComment(Base):
    __tablename__ = 'notice_comments'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    notice_id = Column(ForeignKey('notices.id'), nullable=False, index=True)
    user_id = Column(ForeignKey('users.id'), nullable=False, index=True)
    group = Column(Integer, nullable=False, server_default=text("'0'"))
    depth = Column(TINYINT, nullable=False, server_default=text("'0'"))
    comment = Column(TEXT, nullable=False)
    deleted_at = Column(TIMESTAMP)

    notice = relationship('Notice')
    user = relationship('User')


class Order(Base):
    __tablename__ = 'orders'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    order_no = Column(VARCHAR(255), nullable=False, unique=True)
    user_id = Column(ForeignKey('users.id'), nullable=False, index=True)
    total_price = Column(Integer, nullable=False, comment='결제금액')
    use_point = Column(Integer, nullable=False, comment='사용한 포인트')
    deleted_at = Column(TIMESTAMP, comment="주문 취소 시점(refund에 관한 테이블, 컬럼이 없어 현재는 이것이 refund 역할을 함)\\n주문 취소 시 주문 취소 커맨드를 입력하고(노션 '써클인 인수인계' 참조), 아임포트 어드민에서도 취소해줘야 한다.")
    imp_id = Column(VARCHAR(40), comment='결제 식별번호(아임포트 키)')
    merchant_id = Column(VARCHAR(40))

    user = relationship('User')


class PushHistory(Base):
    __tablename__ = 'push_histories'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    target_id = Column(ForeignKey('users.id'), nullable=False, index=True, comment='푸시 받은 사람')
    device_token = Column(VARCHAR(255))
    title = Column(VARCHAR(255))
    message = Column(TEXT, nullable=False)
    type = Column(VARCHAR(255), comment='tag')
    result = Column(TINYINT(1), nullable=False)
    json = Column(JSON, comment='전송한 데이터')
    result_json = Column(JSON, comment='반환 데이터')

    target = relationship('User')


class SearchHistory(Base):
    __tablename__ = 'search_histories'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    user_id = Column(ForeignKey('users.id'), nullable=False, index=True)
    keyword = Column(VARCHAR(255), nullable=False)
    deleted_at = Column(TIMESTAMP)

    user = relationship('User')


class SortUser(Base):
    __tablename__ = 'sort_users'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    user_id = Column(ForeignKey('users.id'), nullable=False, index=True)
    order = Column(Integer, nullable=False)

    user = relationship('User')


class UserFavoriteCategory(Base):
    __tablename__ = 'user_favorite_categories'
    __table_args__ = {'comment': '고객 관심 카테고리'}

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    user_id = Column(ForeignKey('users.id'), nullable=False, index=True)
    mission_category_id = Column(ForeignKey('mission_categories.id'), nullable=False, index=True)

    mission_category = relationship('MissionCategory')
    user = relationship('User')


class UserStat(Base):
    __tablename__ = 'user_stats'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    user_id = Column(ForeignKey('users.id'), nullable=False, index=True)
    birthday = Column(DateTime, comment='생년월일')
    height = Column(Float(8, True))
    weight = Column(Float(8, True))
    bmi = Column(Float(8, True))
    yesterday_feeds_count = Column(INTEGER, nullable=False, server_default=text("'0'"), comment='어제 체크해야했던 피드 수')

    user = relationship('User')


class UserWallpaper(Base):
    __tablename__ = 'user_wallpapers'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    user_id = Column(ForeignKey('users.id'), nullable=False, index=True)
    title = Column(VARCHAR(255), comment='스킨 이름')
    image = Column(VARCHAR(255), nullable=False)
    thumbnail_image = Column(VARCHAR(255))
    deleted_at = Column(TIMESTAMP)

    user = relationship('User')


class BoardComment(Base):
    __tablename__ = 'board_comments'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    board_id = Column(ForeignKey('boards.id'), nullable=False, index=True)
    user_id = Column(ForeignKey('users.id'), nullable=False, index=True)
    group = Column(Integer, nullable=False, server_default=text("'0'"))
    depth = Column(TINYINT, nullable=False, server_default=text("'0'"))
    comment = Column(Text(collation='utf8mb4_unicode_ci'), nullable=False)
    deleted_at = Column(TIMESTAMP)

    board = relationship('Board')
    user = relationship('User')


class BoardFile(Base):
    __tablename__ = 'board_files'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    board_id = Column(ForeignKey('boards.id'), nullable=False, index=True)
    order = Column(TINYINT, server_default=text("'0'"))
    type = Column(String(255, 'utf8mb4_unicode_ci'), nullable=False, comment='이미지인지 비디오인지 (image / video)')
    file_id = Column(ForeignKey('files.id'), nullable=False, index=True, comment='원본 이미지')

    board = relationship('Board')
    file = relationship('File')


class BoardImage(Base):
    __tablename__ = 'board_images'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    board_id = Column(ForeignKey('boards.id'), nullable=False, index=True)
    order = Column(TINYINT, server_default=text("'0'"))

    path = Column(String(255, 'utf8mb4_unicode_ci'))
    file_name = Column(String(255, 'utf8mb4_unicode_ci'))
    mime_type = Column(String(255, 'utf8mb4_unicode_ci'))

    size = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
    original_file_id = Column(BIGINT(unsigned=True), ForeignKey('board_images.id'), index=True)

    board = relationship('Board')
    board_images = relationship('BoardImage')
    # file = relationship('File')


class BoardLike(Base):
    __tablename__ = 'board_likes'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    board_id = Column(ForeignKey('boards.id'), nullable=False, index=True)
    user_id = Column(ForeignKey('users.id'), nullable=False, index=True)

    board = relationship('Board')
    user = relationship('User')


class ChatMessage(Base):
    __tablename__ = 'chat_messages'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    chat_room_id = Column(ForeignKey('chat_rooms.id'), nullable=False, index=True)
    user_id = Column(ForeignKey('users.id'), nullable=False, index=True)
    type = Column(VARCHAR(255), comment='채팅 종류 (chat|chat_image|feed|feed_emojimission|mission_invite)')
    message = Column(TEXT, comment='메시지')
    image_type = Column(VARCHAR(255), comment='image/video')
    image = Column(VARCHAR(255), comment='이미지 url')
    feed_id = Column(ForeignKey('feeds.id'), index=True, comment='피드 공유 및 이모지')
    mission_id = Column(BIGINT, comment='미션 초대')
    deleted_at = Column(TIMESTAMP)

    chat_room = relationship('ChatRoom')
    feed = relationship('Feed')
    user = relationship('User')


class FeedComment(Base):
    __tablename__ = 'feed_comments'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    feed_id = Column(ForeignKey('feeds.id'), nullable=False, index=True)
    user_id = Column(ForeignKey('users.id'), nullable=False, index=True)
    group = Column(Integer, nullable=False, server_default=text("'0'"))
    depth = Column(TINYINT, nullable=False, server_default=text("'0'"))
    comment = Column(TEXT, nullable=False)
    deleted_at = Column(TIMESTAMP)

    feed = relationship('Feed')
    user = relationship('User')


class FeedImage(Base):
    __tablename__ = 'feed_images'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    feed_id = Column(ForeignKey('feeds.id'), nullable=False, index=True)
    order = Column(TINYINT)
    type = Column(VARCHAR(255), nullable=False, comment='이미지인지 비디오인지 (image / video)')
    image = Column(VARCHAR(255), nullable=False, comment='원본 이미지')
    thumbnail_image = Column(VARCHAR(255), comment='미리 작게 보여줄 이미지')

    feed = relationship('Feed')


class FeedLike(Base):
    __tablename__ = 'feed_likes'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    feed_id = Column(ForeignKey('feeds.id'), nullable=False, index=True)
    user_id = Column(ForeignKey('users.id'), nullable=False, index=True)
    point = Column(Integer, nullable=False, server_default=text("'0'"), comment='대상에게 포인트 지급 여부')
    deleted_at = Column(TIMESTAMP)

    feed = relationship('Feed')
    user = relationship('User')


class FeedPlace(Base):
    __tablename__ = 'feed_places'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    feed_id = Column(ForeignKey('feeds.id'), nullable=False, index=True)
    place_id = Column(ForeignKey('places.id'), nullable=False, index=True)

    feed = relationship('Feed')
    place = relationship('Place')


t_food_flavors = Table(
    'food_flavors', metadata,
    Column('food_id', ForeignKey('foods.id'), nullable=False, index=True),
    Column('flavors', String(255, 'utf8mb4_unicode_ci'), nullable=False, index=True),
    comment='식단(food)과 맛 태그(flavor)의 연결 테이블_20220510(최건우)'
)


class FoodFoodCategory(Base):
    __tablename__ = 'food_food_categories'
    __table_args__ = {'comment': '식단 ~ 식단 카테고리 연결 테이블_20220614(최건우)'}

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    food_id = Column(ForeignKey('foods.id'), nullable=False, unique=True)
    food_category_id = Column(ForeignKey('food_categories.id'), nullable=False, index=True)

    food_category = relationship('FoodCategory')
    food = relationship('Food')


t_food_images = Table(
    'food_images', metadata,
    Column('food_id', ForeignKey('foods.id'), nullable=False, index=True),
    Column('file_id', ForeignKey('files.id'), nullable=False, index=True, comment='food_id 1개 당 5개의 이미지가 등록되어야 함(type 컬럼 참조).'),
    Column('type', String(50, 'utf8mb4_unicode_ci'), nullable=False, comment='6 Types:\\n- 유저가 업로드 하는 경우는 5가지 사진을 수급(package(포장) | nutrition(영양정보 표기란) | ingredient(원재료 표기란) | content(내용물) | barcode(바코드))\\n- 제품체험 미션용인 이미지의 경우 mission'),
    comment='식단 이미지 테이블_20220510(최건우)'
)


t_food_ingredients = Table(
    'food_ingredients', metadata,
    Column('food_id', ForeignKey('foods.id'), nullable=False, index=True),
    Column('ingredient_id', ForeignKey('ingredients.id', ondelete='CASCADE'), index=True),
    comment='식단 - 재료 연결 테이블 테스트(자식 테이블의 2개 컬럼이 같은 food id를 참조)_20220517(최건우)'
)


class FoodRating(Base):
    __tablename__ = 'food_ratings'
    __table_args__ = {'comment': '유저별 음식 평점(유저마다 음식 최초 인증 시 해당 음식에 평점, 후기 태그 부여)_20220510(최건우)'}

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    food_id = Column(ForeignKey('foods.id'), nullable=False, index=True)
    user_id = Column(ForeignKey('users.id'), nullable=False, index=True)
    rating = Column(BIGINT, nullable=False, comment='1~5점(클수록 높은 평점)의 범위 내에서 평점 부여하며 1점 단위')
    body = Column(Text(collation='utf8mb4_unicode_ci'))
    deleted_at = Column(TIMESTAMP)

    food = relationship('Food')
    user = relationship('User')
    food_reviews = relationship('FoodReview', secondary='food_rating_reviews')


class MissionArea(Base):
    __tablename__ = 'mission_areas'
    __table_args__ = {'comment': '미션이 노출될 지역 코드 기록'}

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    mission_id = Column(ForeignKey('missions.id'), nullable=False, index=True)
    area_code = Column(VARCHAR(255), nullable=False, index=True)
    deleted_at = Column(TIMESTAMP)

    mission = relationship('Mission')


class MissionCalendarVideo(Base):
    __tablename__ = 'mission_calendar_videos'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    mission_id = Column(ForeignKey('missions.id'), nullable=False, index=True)
    day = Column(Date, nullable=False)
    url = Column(VARCHAR(255), nullable=False)

    mission = relationship('Mission')


class MissionComment(Base):
    __tablename__ = 'mission_comments'
    __table_args__ = {'comment': '미션 댓글'}

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    mission_id = Column(ForeignKey('missions.id'), nullable=False, index=True)
    user_id = Column(ForeignKey('users.id'), nullable=False, index=True)
    group = Column(INTEGER, nullable=False, server_default=text("'0'"))
    depth = Column(TINYINT, nullable=False, server_default=text("'0'"))
    comment = Column(TEXT, nullable=False)
    deleted_at = Column(TIMESTAMP)

    mission = relationship('Mission')
    user = relationship('User')


class MissionContent(Base):
    __tablename__ = 'mission_contents'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    mission_id = Column(ForeignKey('missions.id'), nullable=False, index=True)
    content_id = Column(ForeignKey('contents.id'), nullable=False, index=True)

    content = relationship('Content')
    mission = relationship('Mission')


class MissionGroundText(Base):
    __tablename__ = 'mission_ground_texts'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    mission_id = Column(ForeignKey('missions.id'), nullable=False, index=True)
    tab = Column(VARCHAR(255), nullable=False, comment='ground/record')
    order = Column(TINYINT, nullable=False, comment='체크 순서 (높을수록 우선 출력)')
    type = Column(VARCHAR(255), nullable=False, comment='조건')
    value = Column(Integer, nullable=False, server_default=text("'0'"), comment='값')
    message = Column(VARCHAR(255), nullable=False, comment='출력될 내용')

    mission = relationship('Mission')


class MissionGround(Base):
    __tablename__ = 'mission_grounds'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    mission_id = Column(ForeignKey('missions.id'), nullable=False, unique=True)
    intro_video = Column(VARCHAR(255), comment='소개 페이지 상단 동영상')
    logo_image = Column(VARCHAR(255), comment='상단 고정 로고')
    code_type = Column(VARCHAR(255), comment='코드 타입')
    code_title = Column(VARCHAR(255), comment='입장코드 라벨')
    code = Column(VARCHAR(255), comment='입장코드 (있으면 비교, 없으면 입력 받기만)')
    code_placeholder = Column(VARCHAR(255), comment='입장코드 입력란 placeholder')
    code_image = Column(VARCHAR(255), comment='입장코드 룸 상단 이미지')
    goal_distance_title = Column(VARCHAR(255), comment='참가하기 전 목표 거리 타이틀')
    goal_distance_type = Column(VARCHAR(255), nullable=False, server_default=text("'goal'"), comment='성공 조건 (goal/min)')
    goal_distances = Column(JSON, comment='참가하기 전 설정할 목표 거리 (km)')
    goal_distance_text = Column(VARCHAR(255), comment='참가하기 전 설정할 목표 거리 접미사')
    distance_min = Column(Float(7), comment='인증 시 최소 거리')
    distance_max = Column(Integer, comment='인증 시 최대 거리')
    distance_placeholder = Column(VARCHAR(255), comment='입력란 placeholder')
    background_image = Column(VARCHAR(255), comment='운동장 전체 fixed 배경 이미지')
    ground_title = Column(VARCHAR(255), nullable=False, server_default=text("'운동장'"), comment='운동장 탭 타이틀')
    record_title = Column(VARCHAR(255), nullable=False, server_default=text("'내기록'"), comment='내기록 탭 타이틀')
    cert_title = Column(VARCHAR(255), nullable=False, server_default=text("'인증서'"), comment='인증서 탭 타이틀')
    feeds_title = Column(VARCHAR(255), server_default=text("'모아보기'"), comment='피드 탭 타이틀 (null 일 경우 노출 X)')
    rank_title = Column(VARCHAR(255), nullable=False, server_default=text("'랭킹'"), comment='랭킹 탭 타이틀')
    ground_is_calendar = Column(TINYINT, nullable=False, server_default=text("'0'"), comment='운동장 탭 캘린더 형태 여부')
    ground_background_image = Column(VARCHAR(255), comment='운동장 탭 배경이미지')
    ground_progress_type = Column(VARCHAR(255), nullable=False, server_default=text("'feed'"), comment='운동장 탭 진행상황 타입 (feed/distance)')
    ground_progress_max = Column(Integer, nullable=False, server_default=text("'0'"), comment='운동장 탭 진행상황 최대치')
    ground_progress_background_image = Column(VARCHAR(255), comment='운동장 탭 진행상황 배경이미지')
    ground_progress_image = Column(VARCHAR(255), comment='운동장 탭 진행상황 차오르는 이미지')
    ground_progress_complete_image = Column(VARCHAR(255), comment='운동장 탭 진행상황 완료됐을 때 이미지')
    ground_progress_title = Column(VARCHAR(255), server_default=text("'총 참가자 누적'"), comment='운동장 탭 진행상황 타이틀')
    ground_progress_text = Column(VARCHAR(255), nullable=False, server_default=text("'{%%feeds_count}'"), comment='운동장 탭 진행상황 텍스트')
    ground_box_users_count_text = Column(VARCHAR(255), nullable=False, server_default=text("'{%%users_count}명'"), comment='운동장 탭 참가중인 유저 수 텍스트')
    ground_box_users_count_title = Column(VARCHAR(255), nullable=False, server_default=text("'참가자'"), comment='운동장 탭 참가중인 유저 수 타이틀')
    ground_box_summary_text = Column(VARCHAR(255), nullable=False, server_default=text("'{%%today_all_distance} L'"), comment='운동장 탭 피드 수 텍스트')
    ground_box_summary_title = Column(VARCHAR(255), nullable=False, server_default=text("'금일 누적'"), comment='운동장 탭 피드 수 타이틀')
    ground_banner_image = Column(VARCHAR(255), comment='운동장 탭 배너 이미지 URL')
    ground_banner_type = Column(VARCHAR(255), comment='운동장 탭 배너 타입 (url)')
    ground_banner_link = Column(VARCHAR(255), comment='운동장 탭 배너 링크 URL')
    ground_users_type = Column(VARCHAR(255), nullable=False, server_default=text("'recent_bookmark'"), comment='운동장 탭 유저 목록 타입')
    ground_users_title = Column(VARCHAR(255), nullable=False, server_default=text("'실시간 참여자'"), comment='운동장 탭 유저 목록 타이틀')
    ground_users_text = Column(VARCHAR(255), nullable=False, server_default=text("'아직 참여자가 없습니다! 어서 참여해보세요.'"), comment='운동장 탭 유저 목록 비었을 때 텍스트')
    record_progress_is_show = Column(TINYINT(1), nullable=False, server_default=text("'1'"), comment='내기록 탭 진행상황 노출 여부')
    record_background_image = Column(VARCHAR(255), comment='내기록 탭 배경이미지')
    record_progress_image_count = Column(TINYINT, nullable=False, server_default=text("'9'"), comment='내기록 탭 진행상황 뱃지 개수')
    record_progress_images = Column(JSON, comment='내기록 탭 진행상황 이미지')
    record_progress_type = Column(VARCHAR(255), nullable=False, server_default=text("'feeds_count'"), comment='내기록 탭 진행상황 타입')
    record_progress_title = Column(VARCHAR(255), comment='내기록 탭 진행상황 타이틀')
    record_progress_text = Column(VARCHAR(255), server_default=text("'{%%remaining_day}'"), comment='내기록 탭 진행상황 텍스트')
    record_progress_description = Column(VARCHAR(255), comment='내기록 탭 진행상황 텍스트 옆 설명')
    record_box_is_show = Column(TINYINT(1), nullable=False, server_default=text("'1'"), comment='내기록 탭 박스 노출 여부')
    record_box_left_title = Column(VARCHAR(255), server_default=text("'NO. {%%entry_no}'"), comment='내기록 탭 박스 왼쪽 타이틀')
    record_box_left_text = Column(VARCHAR(255), server_default=text("'참가번호'"), comment='내기록 탭 박스 왼쪽 텍스트')
    record_box_center_title = Column(VARCHAR(255), server_default=text("'{%%feeds_count}회'"), comment='내기록 탭 박스 가운데 타이틀')
    record_box_center_text = Column(VARCHAR(255), server_default=text("'미션 인증횟수'"), comment='내기록 탭 박스 가운데 텍스트')
    record_box_right_title = Column(VARCHAR(255), server_default=text("'{%%feeds_count}회'"), comment='내기록 탭 박스 오른쪽 타이틀')
    record_box_right_text = Column(VARCHAR(255), server_default=text("'누적 인증'"), comment='내기록 탭 박스 오른쪽 텍스트')
    record_box_description = Column(VARCHAR(255), comment='내기록 탭 박스 하단 설명')
    cert_subtitle = Column(VARCHAR(255), nullable=False, server_default=text("'모바일 인증서'"), comment='인증서 탭 인증서 타이틀')
    cert_description = Column(VARCHAR(255), comment='인증서 탭 내용')
    cert_background_image = Column(JSON, comment='인증서 탭 인증서 배경 이미지')
    cert_custom_cert = Column(JSON)
    cert_details = Column(JSON, comment='인증서 탭 인증서 상세내용')
    cert_images = Column(JSON, comment='인증서 탭 하단 이미지')
    cert_disabled_text = Column(VARCHAR(255), comment='인증서 탭 비활성화 상태 멘트')
    cert_enabled_feeds_count = Column(TINYINT, nullable=False, server_default=text("'1'"), comment='인증서 탭 인증서 활성화될 피드 수')
    rank_subtitle = Column(VARCHAR(255), comment='랭킹 탭 부제목')
    rank_value_text = Column(VARCHAR(255), comment='랭킹 탭 피드 수 포맷')
    feeds_filter_title = Column(VARCHAR(255), nullable=False, server_default=text("'필터 보기'"), comment='전체 피드 탭 필터 타이틀')

    mission = relationship('Mission')


class MissionImage(Base):
    __tablename__ = 'mission_images'
    __table_args__ = {'comment': '미션 상세 이미지\\nmission_id pk'}

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    mission_id = Column(ForeignKey('missions.id'), nullable=False, index=True)
    order = Column(TINYINT)
    type = Column(VARCHAR(255), nullable=False, comment='이미지인지 비디오인지 (image / video)')
    image = Column(VARCHAR(255), nullable=False)
    thumbnail_image = Column(VARCHAR(255))

    mission = relationship('Mission')


class MissionNotice(Base):
    __tablename__ = 'mission_notices'

    id = Column(BIGINT, primary_key=True)
    mission_id = Column(ForeignKey('missions.id'), nullable=False, index=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    title = Column(String(255, 'utf8mb4_unicode_ci'), nullable=False)
    body = Column(Text(collation='utf8mb4_unicode_ci'), nullable=False)
    deleted_at = Column(TIMESTAMP)

    mission = relationship('Mission')


class MissionPlace(Base):
    __tablename__ = 'mission_places'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    mission_id = Column(ForeignKey('missions.id'), nullable=False, index=True)
    place_id = Column(ForeignKey('places.id'), nullable=False, index=True)

    mission = relationship('Mission')
    place = relationship('Place')


class MissionPush(Base):
    __tablename__ = 'mission_pushes'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    mission_id = Column(ForeignKey('missions.id'), nullable=False, index=True)
    type = Column(VARCHAR(255), nullable=False, comment='조건 (bookmark,feed_upload,first_feed_upload,users_count,feeds_count)')
    value = Column(Integer, nullable=False, comment='값')
    target = Column(VARCHAR(255), nullable=False, comment='푸시 수신 대상 (self,mission,all)')
    message = Column(VARCHAR(255), nullable=False, comment='푸시 메시지')
    is_disposable = Column(TINYINT(1), nullable=False, server_default=text("'0'"), comment='일회용 여부')
    count = Column(Integer, nullable=False, server_default=text("'0'"), comment='사용된 횟수')

    mission = relationship('Mission')


class MissionRank(Base):
    __tablename__ = 'mission_ranks'

    id = Column(BIGINT, primary_key=True)
    mission_id = Column(ForeignKey('missions.id'), nullable=False, index=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    mission = relationship('Mission')


class MissionReward(Base):
    __tablename__ = 'mission_rewards'
    __table_args__ = {'comment': '미션 보상'}

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    mission_id = Column(ForeignKey('missions.id'), nullable=False, index=True)
    title = Column(VARCHAR(255), nullable=False)
    image = Column(VARCHAR(255), nullable=False)

    mission = relationship('Mission')


class MissionStat(Base):
    __tablename__ = 'mission_stats'
    __table_args__ = {'comment': '미션 진행현황, 목표, 결과'}

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    user_id = Column(ForeignKey('users.id'), nullable=False, index=True)
    mission_id = Column(ForeignKey('missions.id'), nullable=False, index=True)
    ended_at = Column(TIMESTAMP, comment='미션 콤보 마지막 기록 일시')
    completed_at = Column(TIMESTAMP, comment='이벤트 미션 성공 일시')
    code = Column(VARCHAR(255), comment='이벤트 미션 참가할 때 입력한 코드')
    entry_no = Column(INTEGER, comment='미션 참여 순번')
    goal_distance = Column(Float(8, True), comment='이벤트 미션 목표 거리')
    certification_image = Column(VARCHAR(255), comment='인증서에 업로드한 이미지 URL')

    mission = relationship('Mission')
    user = relationship('User')


class MissionTreasurePoint(Base):
    __tablename__ = 'mission_treasure_points'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    mission_id = Column(ForeignKey('missions.id'), nullable=False, index=True)
    point_min = Column(Integer, nullable=False, comment='최소 지급 포인트(서버가 min ~ max 범위 내에서 랜덤의 정수값으로 포인트 지급함)')
    point_max = Column(Integer, nullable=False, comment='최대 지급 포인트')
    qty = Column(Integer, nullable=False, comment='남은 수량 \\nis_stock == 1 => (qty + count = 총 보물 수량)\\nis_stock == 0 => (count에 관계없이 qty = 총 보물 수량)')
    count = Column(Integer, nullable=False, server_default=text("'0'"), comment='지급 횟수')
    is_stock = Column(TINYINT, nullable=False, server_default=text("'1'"), comment='뽑힐 때마다 하나씩 빠질지')
    deleted_at = Column(TIMESTAMP)

    mission = relationship('Mission')


class NoticeMission(Base):
    __tablename__ = 'notice_missions'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    notice_id = Column(ForeignKey('notices.id'), nullable=False, index=True)
    mission_id = Column(ForeignKey('missions.id'), nullable=False, index=True)

    mission = relationship('Mission')
    notice = relationship('Notice')


class OrderDestination(Base):
    __tablename__ = 'order_destinations'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    order_id = Column(ForeignKey('orders.id'), nullable=False, index=True)
    post_code = Column(VARCHAR(255), nullable=False, comment='우편번호')
    address = Column(VARCHAR(255), nullable=False, comment='주소')
    address_detail = Column(VARCHAR(255), comment='상세 주소')
    recipient_name = Column(VARCHAR(255), nullable=False, comment='받는사람 이름')
    phone = Column(VARCHAR(255), comment='휴대폰번호')
    comment = Column(VARCHAR(255), comment='요청사항')

    order = relationship('Order')


class Product(Base):
    __tablename__ = 'products'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    code = Column(VARCHAR(255), nullable=False, unique=True)
    name_ko = Column(VARCHAR(255), nullable=False)
    name_en = Column(VARCHAR(255))
    thumbnail_image = Column(VARCHAR(255), nullable=False)
    brand_id = Column(ForeignKey('brands.id'), nullable=False, index=True)
    product_category_id = Column(ForeignKey('product_categories.id'), index=True)
    is_show = Column(TINYINT(1), nullable=False, server_default=text("'1'"))
    status = Column(VARCHAR(255), nullable=False, server_default=text("'sale'"), comment='현재 상태 (sale / soldout)')
    order = Column(Integer, nullable=False, server_default=text("'0'"), comment='정렬 (높을수록 우선)')
    price = Column(Integer, nullable=False, comment='정상가')
    sale_price = Column(Integer, nullable=False, server_default=text("'0'"), comment='판매가')
    shipping_fee = Column(Integer, nullable=False, comment='배송비')
    deleted_at = Column(TIMESTAMP)

    brand = relationship('Brand')
    product_category = relationship('ProductCategory')


class Banner(Base):
    __tablename__ = 'banners'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    type = Column(VARCHAR(255), nullable=False, comment='어디에 노출되는 광고인지 (float|local|shop)')
    sort_num = Column(Integer, nullable=False, server_default=text("'0'"), comment='정렬 순서 (높을수록 우선)')
    name = Column(VARCHAR(255), nullable=False, comment='배너명')
    description = Column(TEXT, comment='배너 상세설명')
    started_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='배너 시작 일시')
    ended_at = Column(TIMESTAMP, comment='배너 종료 일시')
    deleted_at = Column(TIMESTAMP)
    image = Column(VARCHAR(255), nullable=False, comment='배너 이미지')
    link_type = Column(VARCHAR(255), comment='링크 형태 (mission|product|notice|url)')
    mission_id = Column(ForeignKey('missions.id'), index=True)
    feed_id = Column(ForeignKey('feeds.id'), index=True)
    product_id = Column(ForeignKey('products.id'), index=True)
    notice_id = Column(ForeignKey('notices.id'), index=True)
    link_url = Column(VARCHAR(255))

    feed = relationship('Feed')
    mission = relationship('Mission')
    notice = relationship('Notice')
    product = relationship('Product')


class Cart(Base):
    __tablename__ = 'carts'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    user_id = Column(ForeignKey('users.id'), nullable=False, index=True)
    product_id = Column(ForeignKey('products.id'), nullable=False, index=True)
    qty = Column(Integer, nullable=False)

    product = relationship('Product')
    user = relationship('User')


class ChatUser(Base):
    __tablename__ = 'chat_users'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    chat_room_id = Column(ForeignKey('chat_rooms.id'), nullable=False, index=True)
    user_id = Column(ForeignKey('users.id'), nullable=False, index=True)
    is_block = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    message_notify = Column(TINYINT(1), nullable=False, server_default=text("'1'"))
    enter_message_id = Column(BIGINT, comment='입장할 때 마지막 메시지 id')
    read_message_id = Column(ForeignKey('chat_messages.id'), index=True, comment='마지막으로 읽은 메시지 id')
    deleted_at = Column(TIMESTAMP)

    chat_room = relationship('ChatRoom')
    read_message = relationship('ChatMessage')
    user = relationship('User')


class FeedMission(Base):
    __tablename__ = 'feed_missions'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    feed_id = Column(ForeignKey('feeds.id'), nullable=False, index=True)
    mission_stat_id = Column(ForeignKey('mission_stats.id'), index=True)
    mission_id = Column(ForeignKey('missions.id'), nullable=False, index=True)

    feed = relationship('Feed')
    mission = relationship('Mission')
    mission_stat = relationship('MissionStat')


class FeedProduct(Base):
    __tablename__ = 'feed_products'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    feed_id = Column(ForeignKey('feeds.id'), nullable=False, index=True)
    type = Column(VARCHAR(255), nullable=False, comment='내부상품인지 외부상품인지 (inside|outside)')
    product_id = Column(ForeignKey('products.id'), index=True)
    outside_product_id = Column(ForeignKey('outside_products.id'), index=True)

    feed = relationship('Feed')
    outside_product = relationship('OutsideProduct')
    product = relationship('Product')


t_food_rating_files = Table(
    'food_rating_files', metadata,
    Column('food_rating_id', ForeignKey('food_ratings.id'), index=True),
    Column('file_id', ForeignKey('files.id'), index=True),
    comment='음식 리뷰별 파일_20220603(최건우)'
)


t_food_rating_reviews = Table(
    'food_rating_reviews', metadata,
    Column('food_rating_id', ForeignKey('food_ratings.id'), nullable=False, index=True),
    Column('food_review_id', ForeignKey('food_reviews.id'), nullable=False, index=True),
    comment='식단 후기 리뷰 목록과 식단 후기의 연결 테이블_20220510(최건우)'
)


class Log(Base):
    __tablename__ = 'logs'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    user_id = Column(ForeignKey('users.id'), nullable=False, index=True, comment='누가')
    ip = Column(VARCHAR(45), nullable=False)
    type = Column(VARCHAR(255), nullable=False, comment='어디서 무엇을')
    feed_id = Column(ForeignKey('feeds.id'), index=True)
    feed_comment_id = Column(ForeignKey('feed_comments.id'), index=True)
    mission_id = Column(ForeignKey('missions.id'), index=True)
    mission_comment_id = Column(ForeignKey('mission_comments.id'), index=True)
    notice_id = Column(ForeignKey('notices.id'), index=True)
    notice_comment_id = Column(ForeignKey('notice_comments.id'), index=True)

    feed_comment = relationship('FeedComment')
    feed = relationship('Feed')
    mission_comment = relationship('MissionComment')
    mission = relationship('Mission')
    notice_comment = relationship('NoticeComment')
    notice = relationship('Notice')
    user = relationship('User')


class MissionNoticeImage(Base):
    __tablename__ = 'mission_notice_images'

    id = Column(BIGINT, primary_key=True)
    mission_notice_id = Column(ForeignKey('mission_notices.id'), nullable=False, index=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    order = Column(INTEGER, nullable=False)
    type = Column(String(255, 'utf8mb4_unicode_ci'), nullable=False, comment='이미지인지 비디오인지 (image / video)')
    image = Column(String(255, 'utf8mb4_unicode_ci'), nullable=False)

    mission_notice = relationship('MissionNotice')


class MissionProduct(Base):
    __tablename__ = 'mission_products'
    __table_args__ = {'comment': '미션 준비물\\nMission_id\\nproduct_id\\n제품의 인증 또는 리뷰 작성을 위해 필요한, 제품 세부옵션 단위(ex. 맛)의 테이블'}

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    mission_id = Column(ForeignKey('missions.id'), nullable=False, index=True)
    type = Column(VARCHAR(255), nullable=False, comment='내부상품인지 외부상품인지 (inside|outside)')
    product_id = Column(ForeignKey('products.id'), index=True)
    outside_product_id = Column(ForeignKey('outside_products.id'), index=True)
    food_id = Column(BIGINT)

    mission = relationship('Mission')
    outside_product = relationship('OutsideProduct')
    product = relationship('Product')


class MissionRankUser(Base):
    __tablename__ = 'mission_rank_users'

    id = Column(BIGINT, primary_key=True)
    mission_rank_id = Column(ForeignKey('mission_ranks.id'), nullable=False, index=True)
    user_id = Column(ForeignKey('users.id'), nullable=False, index=True)
    rank = Column(INTEGER, nullable=False, comment='feeds_count를 높은 순으로 랭킹을 매기되, 필요 시 거리나 횟수 등을 summation에 저장하고 이를 순위에 사용하게 될 수도 있다(마라톤 챌린지에서 사용한 바 있음).')
    feeds_count = Column(INTEGER, nullable=False)
    summation = Column(INTEGER, nullable=False)

    mission_rank = relationship('MissionRank')
    user = relationship('User')


class MissionRefundProduct(Base):
    __tablename__ = 'mission_refund_products'
    __table_args__ = {'comment': '제품의 구매를 위해 필요한, 번들 단위의 제품(ex. 혼합)'}

    id = Column(BIGINT, primary_key=True)
    mission_id = Column(ForeignKey('missions.id'), nullable=False, index=True)
    product_id = Column(ForeignKey('products.id'), nullable=False, index=True)
    limit = Column(TINYINT, nullable=False, comment='제품 최대 구매 수량')
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    food_id = Column(BIGINT)

    mission = relationship('Mission')
    product = relationship('Product')


class Notification(Base):
    __tablename__ = 'notifications'
    __table_args__ = {'comment': '알림'}

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    target_id = Column(ForeignKey('users.id'), nullable=False, index=True, comment='알림 받는 사람')
    type = Column(VARCHAR(255), nullable=False, comment='알림 구분 (출력 내용은 common_codes)')
    user_id = Column(ForeignKey('users.id'), index=True, comment='알림 발생시킨 사람')
    feed_id = Column(ForeignKey('feeds.id'), index=True, comment='알림 발생한 게시물')
    feed_comment_id = Column(ForeignKey('feed_comments.id'), index=True)
    mission_id = Column(ForeignKey('missions.id'), index=True)
    mission_comment_id = Column(ForeignKey('mission_comments.id'), index=True)
    mission_stat_id = Column(ForeignKey('mission_stats.id'), index=True)
    notice_id = Column(ForeignKey('notices.id'), index=True)
    notice_comment_id = Column(ForeignKey('notice_comments.id'), index=True)
    board_id = Column(ForeignKey('boards.id'), index=True)
    board_comment_id = Column(ForeignKey('board_comments.id'), index=True)
    read_at = Column(TIMESTAMP, comment='읽은 일시')
    variables = Column(JSON)

    board_comment = relationship('BoardComment')
    board = relationship('Board')
    feed_comment = relationship('FeedComment')
    feed = relationship('Feed')
    mission_comment = relationship('MissionComment')
    mission = relationship('Mission')
    mission_stat = relationship('MissionStat')
    notice_comment = relationship('NoticeComment')
    notice = relationship('Notice')
    target = relationship('User', primaryjoin='Notification.target_id == User.id')
    user = relationship('User', primaryjoin='Notification.user_id == User.id')


class OrderProduct(Base):
    __tablename__ = 'order_products'
    __table_args__ = {'comment': 'product_id : 상품주문, brand_id : 브랜드별 배송비'}

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    order_id = Column(ForeignKey('orders.id'), nullable=False, index=True)
    product_id = Column(ForeignKey('products.id'), index=True, comment='상품')
    brand_id = Column(BIGINT, comment='배송비')
    qty = Column(Integer, server_default=text("'0'"))
    price = Column(INTEGER, nullable=False, comment='구매 당시 단일 가격 or 배송비')

    order = relationship('Order')
    product = relationship('Product')


class PointHistory(Base):
    __tablename__ = 'point_histories'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    user_id = Column(ForeignKey('users.id'), nullable=False, index=True)
    point = Column(Integer, nullable=False, comment='변경된 포인트')
    result = Column(Integer, comment='잔여 포인트')
    reason = Column(VARCHAR(255), nullable=False, comment='지급차감 사유 (like,mission 등) 출력될 내용은 common_codes')
    feed_id = Column(ForeignKey('feeds.id'), index=True)
    order_id = Column(ForeignKey('orders.id'), index=True)
    mission_id = Column(ForeignKey('missions.id'), index=True)
    food_rating_id = Column(ForeignKey('circlin_65.food_rating.id'), index=True)
    feed_comment_id = Column(ForeignKey('feed_comments.id'), index=True)

    feed_comment = relationship('FeedComment')
    feed = relationship('Feed')
    food_rating = relationship('FoodRating')
    mission = relationship('Mission')
    order = relationship('Order')
    user = relationship('User')


class ProductImage(Base):
    __tablename__ = 'product_images'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    product_id = Column(ForeignKey('products.id'), index=True)
    order = Column(TINYINT)
    type = Column(VARCHAR(255), nullable=False, comment='이미지인지 비디오인지 (image / video)')
    image = Column(VARCHAR(255))
    thumbnail_image = Column(VARCHAR(255))

    product = relationship('Product')


class ProductOption(Base):
    __tablename__ = 'product_options'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    product_id = Column(ForeignKey('products.id'), index=True)
    group = Column(INTEGER, nullable=False, server_default=text("'0'"))
    name_ko = Column(VARCHAR(255), nullable=False)
    name_en = Column(VARCHAR(255))
    price = Column(Integer, nullable=False)
    status = Column(VARCHAR(255), nullable=False, server_default=text("'sale'"), comment='현재 상태 (sale / soldout)')
    stock = Column(Integer, nullable=False, server_default=text("'-1'"), comment='재고')
    deleted_at = Column(TIMESTAMP)
    temp = Column(VARCHAR(255), server_default=text("''"), comment='현재 상태 (sale / soldout)')
    tempprice = Column(VARCHAR(200), server_default=text("''"))

    product = relationship('Product')


class PushReservation(Base):
    __tablename__ = 'push_reservations'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    target = Column(VARCHAR(255), nullable=False, comment='푸시 대상')
    target_ids = Column(TEXT, comment='구분자 : |')
    description = Column(VARCHAR(255), comment='푸시 설명')
    title = Column(VARCHAR(255), nullable=False, comment='푸시 타이틀')
    message = Column(VARCHAR(255), nullable=False, comment='푸시 내용')
    send_date = Column(Date, comment='발송 일자 (없으면 매일)')
    send_time = Column(Time, nullable=False, comment='발송 시간')
    link_type = Column(VARCHAR(255), comment='푸시 링크')
    feed_id = Column(ForeignKey('feeds.id'), index=True)
    mission_id = Column(ForeignKey('missions.id'), index=True)
    notice_id = Column(ForeignKey('notices.id'), index=True)
    product_id = Column(ForeignKey('products.id'), index=True)
    url = Column(VARCHAR(50))
    deleted_at = Column(TIMESTAMP)

    feed = relationship('Feed')
    mission = relationship('Mission')
    notice = relationship('Notice')
    product = relationship('Product')


class Report(Base):
    __tablename__ = 'reports'
    __table_args__ = {'comment': '신고 기능을 위한 테이블'}

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    user_id = Column(ForeignKey('users.id'), index=True, comment='신고자 user id')
    target_feed_id = Column(ForeignKey('feeds.id'), index=True, comment='피드 신고 시 feed id값')
    target_user_id = Column(ForeignKey('users.id'), index=True, comment='유저 신고 시 user id값')
    target_mission_id = Column(ForeignKey('missions.id'), index=True, comment='미션 신고 시 mission id값')
    target_feed_comment_id = Column(ForeignKey('feed_comments.id'), index=True, comment='피드 댓글 신고 시 feed_comment id값')
    target_notice_comment_id = Column(ForeignKey('notice_comments.id'), index=True, comment='공지사항 댓글 신고 시 notice_comment id값')
    target_mission_comment_id = Column(ForeignKey('mission_comments.id'), index=True, comment='미션 댓글 신고 시 mission_comment id값')
    reason = Column(Text(collation='utf8mb4_unicode_ci'))

    target_feed_comment = relationship('FeedComment')
    target_feed = relationship('Feed')
    target_mission_comment = relationship('MissionComment')
    target_mission = relationship('Mission')
    target_notice_comment = relationship('NoticeComment')
    target_user = relationship('User', primaryjoin='Report.target_user_id == User.id')
    user = relationship('User', primaryjoin='Report.user_id == User.id')


class BannerLog(Base):
    __tablename__ = 'banner_logs'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    user_id = Column(ForeignKey('users.id'), nullable=False, index=True)
    banner_id = Column(ForeignKey('banners.id'), nullable=False, index=True)
    device_type = Column(VARCHAR(255), comment='기기 구분')
    ip = Column(VARCHAR(45), nullable=False, comment='배너 불러온 IP')
    type = Column(VARCHAR(255), nullable=False, comment='open/view/click')

    banner = relationship('Banner')
    user = relationship('User')


class CartOption(Base):
    __tablename__ = 'cart_options'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    cart_id = Column(ForeignKey('carts.id'), nullable=False, index=True)
    product_option_id = Column(ForeignKey('product_options.id'), nullable=False, index=True)
    price = Column(Integer, nullable=False, comment='옵션가로 보인다만 큰 의미는 없는 컬럼')

    cart = relationship('Cart')
    product_option = relationship('ProductOption')


class OrderProductDelivery(Base):
    __tablename__ = 'order_product_deliveries'
    __table_args__ = {'comment': 'delivery: 배송중, complete: 배송완료'}

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    order_product_id = Column(ForeignKey('order_products.id'), nullable=False, index=True)
    qty = Column(Integer, nullable=False)
    company = Column(VARCHAR(255), nullable=False)
    tracking_no = Column(VARCHAR(255), nullable=False, comment='송장번호')
    status = Column(VARCHAR(255), comment='배송현황')
    completed_at = Column(TIMESTAMP)

    order_product = relationship('OrderProduct')


class OrderProductOption(Base):
    __tablename__ = 'order_product_options'

    id = Column(BIGINT, primary_key=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    order_product_id = Column(ForeignKey('order_products.id'), nullable=False, index=True)
    product_option_id = Column(ForeignKey('product_options.id'), nullable=False, index=True)
    price = Column(Integer, nullable=False)

    order_product = relationship('OrderProduct')
    product_option = relationship('ProductOption')
