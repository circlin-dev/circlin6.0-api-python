# region local path config
APP_ROOT = "/home/ubuntu/circlin6.0-api-python"
API_ROOT = "api-python-circlin6.circlin.co.kr"
API_CIRCLIN = "https://api.circlin.co.kr/v1_1"
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
##Slack
SLACK_NOTIFICATION_WEBHOOK = "https://hooks.slack.com/services/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?"
# endregion

# Admin
ADMIN_USER_ID_CALEB = 64477
# endregion


# regin App
## JWT Token
JWT_SECRET_KEY = "circlin2019890309890909"
JWT_AUDIENCE = "https://www.circlin.co.kr"

## File(image) processing
LOCAL_TEMP_DIR = f"{APP_ROOT}/temp"
invalid_mimes = ['heic', 'HEIC', 'heif', 'HEIF']

## Cursor paging(infinite scroll)
INITIAL_PAGE_CURSOR = 900000000000000
# endregion