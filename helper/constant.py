# region third-party
SLACK_NOTIFICATION_WEBHOOK = "https://hooks.slack.com/services/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?"

FIREBASE_AUTHORIZATION_KEY: str = 'key=AAAALKBQqQQ:APA91bHBUnrkt4QVKuO6FR0ZikkWMQ2zvr_2k7JCkIo4DVBUOB3HUZTK5pH-Rug8ygfgtjzb2lES3SaqQ9Iq8YhmU-HwdbADN5dvDdbq0IjrOPKzqNZ2tTFDWgMQ9ckPVQiBj63q9pGq'

# region Naver API
NAVER_CLIENT_ID = "RIlhqldSpYbrDGHh4leX"
NAVER_CLIENT_SECRET = "cixe4ECPyg"
# endregion

# region public API
PUBLIC_API_SUPPLEMENT = "http://apis.data.go.kr/1471000/HtfsTrgetInfoService01/getHtfsInfoList01"
PUBLIC_API_SUPPLEMENT_ENCODING_KEY = 'G8Fa%2Br69TLfqBJ%2FzHb8Lxsvl9%2F1cgOhvvjjwb1ty2LhAujVOkdq96lfoCwOykpuGHCZPnf2NkrV6gZLR9BYl%2Bw%3D%3D'
PUBLIC_API_SUPPLEMENT_DECODING_KEY = 'G8Fa+r69TLfqBJ/zHb8Lxsvl9/1cgOhvvjjwb1ty2LhAujVOkdq96lfoCwOykpuGHCZPnf2NkrV6gZLR9BYl+w=='
# endregion

# region Authentication
JWT_SECRET_KEY = "circlin2019890309890909"
JWT_AUDIENCE: str = "https://www.circlin.co.kr"
# endregion
# endregion

# region File processing
# region local path config
APP_ROOT = "/home/ubuntu/circlin6.0-api-python"
APP_TEMP = "./temp"
API_ROOT = "api-python-circlin6.circlin.co.kr"
API_CIRCLIN = "https://api.circlin.co.kr/v1_1"
LOCAL_TEMP_DIR = f"{APP_ROOT}/temp"

FFMPEG_PATH1 = "/home/ubuntu/anaconda3/envs/circlin60_py38/bin/ffmpeg"  #whereis ffmpeg
FFMPEG_PATH2 = "/usr/bin/ffmpeg"
FFMPEG_PATH3 = "/usr/share/ffmpeg"
# endregion


# region Amazon
AMAZON_URL = "https://circlin-app.s3.ap-northeast-2.amazonaws.com"
S3_BUCKET_NAME = "circlin-app"
BUCKET_IMAGE_PATH_FOOD = "food"  # food/{food_id}/{file_name}'
BUCKET_IMAGE_PATH_WORKOUT = "workout"  # food/{workout_id}/{file_name}'
# endregion

# region file type, file size
INVALID_MIMES = {
    'image': ['heic', 'HEIC', 'heif', 'HEIF'],
    'video': ['quicktime', 'mov', 'MOV', '3gp', '3GP']
}
RESIZE_WIDTHS_IMAGE = [1080, 840, 750, 640, 480, 320, 240, 150]  # 16:9 모니터에 대해서라면: [1080, 900, 720, 630, 540, 450, 360, 270, 180]
RESIZE_WIDTHS_VIDEO = [640, 480]
# endregion
# endregion


# region application constant
# Cursor paging(infinite scroll)
INITIAL_DESCENDING_PAGE_CURSOR: int = 900000000000000
INITIAL_ASCENDING_PAGE_CURSOR: int = 00000000000000
INITIAL_PAGE_LIMIT: int = 20
INITIAL_PAGE: int = 1

# push
PUSH_TITLE_BOARD: str = "써클인 커뮤니티"
PUSH_TITLE_NOTICE: str = "써클인 공지사항"
PUSH_TITLE_FEED: str = "써클인 피드 알림"

# Error message
ERROR_RESPONSE: dict = {
    400: '필수 데이터가 누락되었거나, 올바르지 않습니다.',
    401: '요청을 보낸 사용자는 알 수 없는 사용자입니다.',
    403: '해당 요청사항을 수행할 권한이 없는 사용자입니다.',
    500: '서버 오류로 요청을 수행할 수 없습니다. 계속 발생할 경우 카카오톡 채널 "써클인"으로 문의해 주세요.'
}

# Point reward logic
BASIC_COMPENSATION_AMOUNT_PER_REASON: dict = {
    'feed_check': 10,
    'feed_check_reward': 10,
    'feed_comment_reward': 1,
    'feed_comment_delete': -1,
    'feed_upload_product': 50,
    'feed_upload_place': 50,

    'invite_reward': 500,
    'recommended_reward': 500,

    'review_food': 5
}

DAILY_POINT_LIMIT_FOR_FEED_CHECK_FEED_COMMENT: int = 500

# 아래 지급 사유는 일일 최대 지급 한도(500p)에 따라 지급액이 줄어야 할 수도 있다.
# 예를 들어, 현재까지 아래 4가지 이유로 496p를 획득한 상태에서 feed_check_reward를 받으면, 기본 지급액인 10p 대신 500p-496p = 4p 를 받는다.
REASONS_HAVE_DAILY_REWARD_RESTRICTION: list = ["feed_check", "feed_check_reward", "feed_comment_reward", "feed_comment_delete"]
# endregion

