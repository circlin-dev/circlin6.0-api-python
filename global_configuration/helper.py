import hashlib
import base64
import requests
import boto3
import cv2
import filetype
import json
import jwt
import os
from PIL import Image
import pyheif
import pymysql
from pypika import MySQLQuery as Query, functions as fn
import random
import shutil
import string
from werkzeug.utils import secure_filename

from global_configuration.constants import S3_BUCKET, JWT_SECRET_KEY, JWT_AUDIENCE, API_CIRCLIN, INVALID_MIMES, RESIZE_WIDTHS
from global_configuration.database import DATABASE
# from global_configuration.table import Sessions, User, File
from global_configuration.table import Files


def db_connection():
    connection = pymysql.connect(
        user=DATABASE['user'],
        passwd=DATABASE['password'],
        host=DATABASE['host'],
        db=DATABASE['scheme'],
        charset=DATABASE['charset'])

    return connection


def get_dict_cursor(connection):
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    return cursor


def authenticate(request, cursor):
    token = request.headers.get('token')
    user_id = {
        'user_id': int(jwt.decode(token, audience=JWT_AUDIENCE, options={"verify_signature": False})['uid'])  # Without secret key
    }
    # if request.cookies.get('circlinapi_session') is not None:
    #     #     cookie = request.cookies.get('circlinapi_session')
    #     #     sql = Query.from_(
    #     #         Sessions
    #     #     ).select(
    #     #         Sessions.user_id
    #     #     ).where(
    #     #         Sessions.id == cookie
    #     #     ).get_sql()
    #     #
    #     #     cursor.execute(sql)
    #     #     # user_id = json.dumps(cursor.fetchone(), indent=4, ensure_ascii=False)
    #     #     user_id = cursor.fetchone()
    #     # else:
    #     #     token = request.headers.get('token')
    #     #     user_id = {
    #     #         'user_id': int(jwt.decode(token, options={"verify_signature": False}))   # Without secret key
    #     #     }

    return user_id


def convert_timestamp_to_string(query_result: dict, keys: list):
    for data in query_result:
        for key in keys:
            if data[key] is None:
                pass
            else:
                data[key] = data[key].strftime('%Y-%m-%d %H:%M:%S')

    return query_result


def return_json(result: dict):
    return json.dumps(result, ensure_ascii=False)


def upload_single_file_to_s3(file, object_path):
    connection = db_connection()
    cursor = get_dict_cursor(connection)
    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=15))

    s3_client = boto3.client('s3')

    # 1. Save request image first.
    if type(file) != bytes:
        request_file = file.filename
    else:
        request_file = file['uri'].split('/')[-1]  # file path form from react-native client.
    secure_file = secure_filename(request_file)
    if not os.path.exists(secure_file):
        file.save(secure_file)

    request_path = os.path.join('./temp', request_file)
    if os.path.exists(secure_file):
        shutil.move(secure_file, request_path)

    # 2. Check image mime type & change if invalid.
    mime_type = check_mimetype(request_path)['mime_type'].split('/')[0]
    request_ext = check_mimetype(request_path)['mime_type'].split('/')[1]

    if request_ext in INVALID_MIMES['image']:  # or video
        original_file = heic_to_jpg(request_path)
    else:
        original_file = request_path

    original_file_name = original_file.split('/')[-1]  # Insert to DB
    hashed_file_name = f"{hashlib.sha256(original_file_name.split('.')[0].encode()).hexdigest()}_{random_string}.{original_file_name.split('.')[1]}"
    hashed_file = os.path.join('./temp', hashed_file_name)
    os.rename(original_file, hashed_file)

    hashed_object_name = os.path.join(object_path, hashed_file_name)
    hashed_mime_type = check_mimetype(hashed_file)['mime_type']  # Insert to DB
    hashed_size = get_file_information(hashed_file, 'image')['size']  # Insert to DB
    hashed_width = get_file_information(hashed_file, 'image')['width']  # Insert to DB
    hashed_height = get_file_information(hashed_file, 'image')['height']  # Insert to DB
    hashed_s3_pathname = os.path.join("https://circlin-app.s3.ap-northeast-2.amazonaws.com/", hashed_object_name)  # Insert to DB

    s3_client.upload_file(hashed_file, S3_BUCKET, hashed_object_name, ExtraArgs={'ContentType': hashed_mime_type})

    sql = Query.into(
        Files
    ).columns(
        Files.created_at,
        Files.updated_at,
        Files.pathname,
        Files.original_name,
        Files.mime_type,
        Files.size,
        Files.width,
        Files.height
    ).insert(
        fn.Now(),
        fn.Now(),
        hashed_s3_pathname,
        original_file_name,
        hashed_mime_type,
        hashed_size,
        hashed_width,
        hashed_height
    ).get_sql()

    cursor.execute(sql)
    connection.commit()
    original_file_id = cursor.lastrowid

    # 3. Generate resized image
    resized_file_list = generate_resized_file(hashed_file_name.split('.')[1], hashed_file, 'image')

    for resized_path in resized_file_list:
        object_name = os.path.join(object_path, resized_path.split('/')[-1])
        resized_mime_type = check_mimetype(resized_path)['mime_type']  # Insert to DB
        resized_size = get_file_information(resized_path, mime_type)['size']  # Insert to DB
        resized_width = get_file_information(resized_path, mime_type)['width']  # Insert to DB
        resized_height = get_file_information(resized_path, mime_type)['height']  # Insert to DB
        resized_s3_pathname = os.path.join("https://circlin-app.s3.ap-northeast-2.amazonaws.com/", object_name)  # Insert to DB

        s3_client.upload_file(resized_path, S3_BUCKET, object_name, ExtraArgs={'ContentType': resized_mime_type})

        sql = Query.into(
            Files
        ).columns(
            Files.created_at,
            Files.updated_at,
            Files.pathname,
            Files.original_name,
            Files.mime_type,
            Files.size,
            Files.width,
            Files.height,
            Files.original_file_id
        ).insert(
            fn.Now(),
            fn.Now(),
            resized_s3_pathname,
            original_file_name,
            resized_mime_type,
            resized_size,
            resized_width,
            resized_height,
            original_file_id
        ).get_sql()

        cursor.execute(sql)
        os.remove(resized_path)

    os.remove(hashed_file)
    connection.commit()
    connection.close()

    result = {'result': True, 'original_file_id': original_file_id}

    return result


def heic_to_jpg(path):
    heif_file = pyheif.read(path)
    new_image = Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        "raw",
        heif_file.mode,
        heif_file.stride,
    )

    new_path = f"{path.split('/')[-1].split('.')[0]}.jpg"
    new_image.save(new_path, "JPEG")
    if os.path.exists(path):
        os.remove(path)

    return new_path


def check_mimetype(path):
    result = {'mime_type': filetype.guess(path).mime}

    return result


def get_file_information(path, file_type):
    if file_type == 'image':
        image = cv2.imread(path, cv2.IMREAD_COLOR)
        height, width, channel = image.shape
    else:
        video = cv2.VideoCapture(path)
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))

    result = {
        'size': int(os.path.getsize(path)),
        'width': width,
        'height': height
    }

    return result


def generate_resized_file(extension, original_file_path, file_type):
    resized_file_list = []
    if file_type == 'image':
        original_file = cv2.imread(original_file_path, cv2.IMREAD_COLOR)
        height, width, channel = original_file.shape

        for new_width in RESIZE_WIDTHS:
            new_height = int(new_width * height / width)
            resized_file = cv2.resize(original_file,
                                      dsize=(new_width, new_height),
                                      interpolation=cv2.INTER_LINEAR)
            # if new_width > width:  # 확대
            #     resized_image = cv2.resize(original_image,
            #                                dsize=(new_width, new_height),
            #                                interpolation=cv2.INTER_LINEAR)
            # else:                  # 축소(<) or 유지(=)
            #     resized_image = cv2.resize(original_image,
            #                                dsize=(new_width, new_height),
            #                                interpolation=cv2.INTER_AREA)

            temp_path = './temp'
            original_file_name = original_file_path.split('/')[-1]
            resized_file_name = f"{original_file_name.split('.')[0]}_w{str(new_width)}.{extension}"
            resized_file_path = os.path.join(temp_path, resized_file_name)

            cv2.imwrite(resized_file_path, resized_file)
            resized_file_list.append(resized_file_path)
        # return resized_image_list
    else:
        original_file = cv2.VideoCapture(original_file_path)
        height = int(original_file.get(cv2.CAP_PROP_FRAME_HEIGHT))
        width = int(original_file.get(cv2.CAP_PROP_FRAME_WIDTH))

        for new_width in RESIZE_WIDTHS:
            new_height = int(new_width * height / width)

            temp_path = './temp'
            original_file_name = original_file_path.split('/')[-1]
            resized_file_name = f"{original_file_name.split('.')[0]}_w{str(new_width)}.{extension}"
            resized_file_path = os.path.join(temp_path, resized_file_name)
            os.system(f"ffmpeg -i {original_file_path} -vf 'scale={new_width}x{new_height}' {resized_file_path}")

            resized_file_list.append(resized_file_path)

    return resized_file_list


def point_request(token, point: int, reason: string, type: string, food_rating_id: int):
    response = requests.post(
        f"{API_CIRCLIN}/point",
        headers={"token": token},
        json={
            "point": point,
            "reason": reason,
            "type": type,
            "id": food_rating_id
        }
    ).json()

    return response

    # result = {
    #     'result': response,
    #     'status_code': response['status_code']
    # }

   # return json.dumps(response, ensure_ascii=False)


def get_query_strings_from_request(request, param, init_value):
    if request.args.get(param) is None or request.args.get(param) == '':
        if param == 'word':
            result = init_value
        elif param == 'limit':
            result = init_value
        elif param == 'cursor':
            result = init_value
        else:
            result = ''
    else:
        if param == 'word':
            result = request.args.get(param)
        elif param == 'limit':
            result = int(request.args.get(param))
        elif param == 'cursor':
            result = int(request.args.get(param))
        else:
            result = ''

    return result
