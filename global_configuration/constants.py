# region local path config
APP_ROOT = "/home/ubuntu/circlin6.0-api-python"
APP_TEMP = f"{APP_ROOT}/temp"
API_ROOT = "api-python-circlin6.circlin.co.kr"
API_CIRCLIN = "https://api.circlin.co.kr/v1_1"

FFMPEG_PATH1 = "/home/ubuntu/anaconda3/envs/circlin60_py38/bin/ffmpeg"  #whereis ffmpeg
FFMPEG_PATH2 = "/usr/bin/ffmpeg"
FFMPEG_PATH3 = "/usr/share/ffmpeg"
# endregion


# region Amazon
AMAZON_URL = "https://circlin-app.s3.ap-northeast-2.amazonaws.com"
S3_BUCKET = "circlin-app"
BUCKET_IMAGE_PATH_FOOD = "food"  # food/{food_id}/{file_name}'
BUCKET_IMAGE_PATH_WORKOUT = "workout"  # food/{workout_id}/{file_name}'
# endregion


# region Naver API
NAVER_CLIENT_ID = "RIlhqldSpYbrDGHh4leX"
NAVER_CLIENT_SECRET = "cixe4ECPyg"
# endregion


# region public API
PUBLIC_API_SUPPLEMENT = "http://apis.data.go.kr/1471000/HtfsTrgetInfoService01/getHtfsInfoList01"
PUBLIC_API_SUPPLEMENT_ENCODING_KEY = 'G8Fa%2Br69TLfqBJ%2FzHb8Lxsvl9%2F1cgOhvvjjwb1ty2LhAujVOkdq96lfoCwOykpuGHCZPnf2NkrV6gZLR9BYl%2Bw%3D%3D'
PUBLIC_API_SUPPLEMENT_DECODING_KEY = 'G8Fa+r69TLfqBJ/zHb8Lxsvl9/1cgOhvvjjwb1ty2LhAujVOkdq96lfoCwOykpuGHCZPnf2NkrV6gZLR9BYl+w=='
# endregion


# region third-party
# Slack
SLACK_NOTIFICATION_WEBHOOK = "https://hooks.slack.com/services/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?"

# Firebase push authorization key
FIREBASE_AUTHORIZATION_KEY = 'key=AAAALKBQqQQ:APA91bHBUnrkt4QVKuO6FR0ZikkWMQ2zvr_2k7JCkIo4DVBUOB3HUZTK5pH-Rug8ygfgtjzb2lES3SaqQ9Iq8YhmU-HwdbADN5dvDdbq0IjrOPKzqNZ2tTFDWgMQ9ckPVQiBj63q9pGq'
# endregion

# Admin
ADMIN_USER_ID_CALEB = 64477
# endregion


# regin App
# JWT Token
JWT_SECRET_KEY = "circlin2019890309890909"
JWT_AUDIENCE = "https://www.circlin.co.kr"

# File processing
LOCAL_TEMP_DIR = f"{APP_ROOT}/temp"
INVALID_MIMES = {
    'image': ['heic', 'HEIC', 'heif', 'HEIF'],
    'video': ['quicktime', 'mov', 'MOV']
}
RESIZE_WIDTHS_IMAGE = [1080, 840, 750, 640, 480, 320, 240, 150]  # 16:9 모니터에 대해서라면: [1080, 900, 720, 630, 540, 450, 360, 270, 180]
RESIZE_WIDTHS_VIDEO = [640, 480]

# Cursor paging(infinite scroll)
INITIAL_DESCENDING_PAGE_CURSOR = 900000000000000
INITIAL_ASCENDING_PAGE_CURSOR = 00000000000000
INITIAL_PAGE_LIMIT = 30
INITIAL_PAGE = 1

# Push message title
BOARD_PUSH_TITLE = "써클인 게시판 알림"
# endregion
