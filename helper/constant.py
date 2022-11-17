# region local path config
APP_ROOT = "/home/ubuntu/circlin6.0-api-python"
APP_TEMP = "./temp"
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
SLACK_NOTIFICATION_WEBHOOK = "https://hooks.slack.com/services/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?"
FIREBASE_AUTHORIZATION_KEY: str = 'key=AAAALKBQqQQ:APA91bHBUnrkt4QVKuO6FR0ZikkWMQ2zvr_2k7JCkIo4DVBUOB3HUZTK5pH-Rug8ygfgtjzb2lES3SaqQ9Iq8YhmU-HwdbADN5dvDdbq0IjrOPKzqNZ2tTFDWgMQ9ckPVQiBj63q9pGq'
# endregion

# Admin
ADMIN_USER_ID_CALEB = 64477
# endregion


# regin Authentication
JWT_SECRET_KEY = "circlin2019890309890909"
JWT_AUDIENCE: str = "https://www.circlin.co.kr"
# endregion

# File processing
LOCAL_TEMP_DIR = f"{APP_ROOT}/temp"
INVALID_MIMES = {
    'image': ['heic', 'HEIC', 'heif', 'HEIF'],
    'video': ['quicktime', 'mov', 'MOV', '3gp', '3GP']
}
RESIZE_WIDTHS_IMAGE = [1080, 840, 750, 640, 480, 320, 240, 150]  # 16:9 모니터에 대해서라면: [1080, 900, 720, 630, 540, 450, 360, 270, 180]
RESIZE_WIDTHS_VIDEO = [640, 480]

# Cursor paging(infinite scroll)
INITIAL_DESCENDING_PAGE_CURSOR: int = 900000000000000
INITIAL_ASCENDING_PAGE_CURSOR: int = 00000000000000
INITIAL_PAGE_LIMIT: int = 20
INITIAL_PAGE: int = 1

# Push message title
PUSH_TITLE_BOARD: str = "써클인 커뮤니티"

# Error message
ERROR_RESPONSE: dict = {
    400: '필수 데이터가 누락되었거나, 올바르지 않습니다.',
    401: '요청을 보낸 사용자는 알 수 없는 사용자입니다.',
    403: '해당 요청사항을 수행할 권한이 없는 사용자입니다.',
    500: '서버 오류로 요청을 수행할 수 없습니다. 계속 발생할 경우 카카오톡 채널 "써클인"으로 문의해 주세요.'
}
# endregion
