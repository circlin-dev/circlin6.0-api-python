from helper.constant import AMAZON_URL, INVALID_MIMES, RESIZE_WIDTHS_IMAGE, RESIZE_WIDTHS_VIDEO, S3_BUCKET_NAME

from werkzeug.utils import secure_filename
import boto3
import cv2
import filetype
import hashlib
from moviepy.editor import VideoFileClip
import os
from PIL import Image
import pyheif
import random
import shutil
import string


def get_filename_and_secure_filename(file):
    if type(file) != bytes:
        request_file = file.filename
    else:
        request_file = file['uri'].split('/')[-1]  # file path form from react-native client.

    filename_secure_version = secure_filename(request_file)
    return request_file, filename_secure_version


def set_temp_path_of_file(request_file):
    return os.path.join(os.getcwd(), 'temp', request_file)


def save_secure_file_and_move_to_temp_path(file, secured_filename, temp_path):
    file.save(secured_filename)
    shutil.move(secured_filename, temp_path)


def save_file_as_secure_filename_and_move_to_temp_folder(file):
    request_file_name, secured_filename = get_filename_and_secure_filename(file)
    temp_path = set_temp_path_of_file(request_file_name)
    save_secure_file_and_move_to_temp_path(file, secured_filename, temp_path)

    return temp_path


def convert_temp_file_into_valid_extension(temp_path):
    mime_type, request_ext = check_mimetype(temp_path)['mime_type'].split('/')

    if request_ext in INVALID_MIMES['image']:  # or video
        valid_temp_file_path = heic_to_jpg(temp_path)
    elif request_ext in INVALID_MIMES['video']:
        valid_temp_file_path = video_to_mp4(temp_path)
    else:
        valid_temp_file_path = temp_path

    validated_mime_type, validated_extension = check_mimetype(valid_temp_file_path)['mime_type'].split('/')
    return valid_temp_file_path, validated_mime_type, validated_extension


def rename_validated_temp_file_as_hashed_name(valid_temp_file):
    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=15))
    original_name = valid_temp_file.split('/')[-1]
    hashed_file_name = f"{hashlib.sha256(original_name.split('.')[0].encode()).hexdigest()}_{random_string}.{original_name.split('.')[1]}"
    hashed_file_path = os.path.join(os.getcwd(), 'temp', hashed_file_name)
    os.rename(valid_temp_file, hashed_file_path)

    return hashed_file_name, hashed_file_path


# region file processing
def upload_single_file_to_s3(file, s3_object_path):
    s3_client = boto3.client('s3')
    temp_path = save_file_as_secure_filename_and_move_to_temp_folder(file)

    validated_temp_file_path, validated_mime_type, validated_extension = convert_temp_file_into_valid_extension(temp_path)
    hashed_file_name, hashed_file_path = rename_validated_temp_file_as_hashed_name(validated_temp_file_path)
    hashed_object_name = os.path.join(s3_object_path, hashed_file_name)
    hashed_file_info = get_file_information(hashed_file_path, validated_mime_type)

    s3_client.upload_file(hashed_file_path, S3_BUCKET_NAME, hashed_object_name, ExtraArgs={'ContentType': validated_mime_type})
    saved_s3_url = os.path.join(AMAZON_URL, hashed_object_name)

    result = {
        'original_file': {
            'path': saved_s3_url,
            'file_name': validated_temp_file_path.split('/')[-1],
            'mime_type': f'{validated_mime_type}/{validated_extension}',
            'size': hashed_file_info['size'],
            'width': hashed_file_info['width'],
            'height': hashed_file_info['height'],
        },
        'resized_file': []
    }

    # 3. Generate resized image
    if validated_mime_type == 'image':
        resized_files = generate_resized_file(hashed_file_name.split('.')[1], hashed_file_path, validated_mime_type)

        for resized_path in resized_files:
            object_name = os.path.join(s3_object_path, resized_path.split('/')[-1])
            # resized_mime_type = check_mimetype(resized_path)['mime_type']
            resized_file_info = get_file_information(resized_path, validated_mime_type)
            resized_saved_s3_url = os.path.join(AMAZON_URL, object_name)

            s3_client.upload_file(resized_path, S3_BUCKET_NAME, object_name, ExtraArgs={'ContentType': f'{validated_mime_type}/{validated_extension}'})

            os.remove(resized_path)

            result['resized_file'].append({
                'path': resized_saved_s3_url,
                'file_name': validated_temp_file_path.split('/')[-1],
                'mime_type': f'{validated_mime_type}/{validated_extension}',
                'size': resized_file_info['size'],
                'width': resized_file_info['width'],
                'height': resized_file_info['height'],
            })
    os.remove(hashed_file_path)

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


def video_to_mp4(path):
    # new_path = os.path.join(os.getcwd(), 'temp', f"{path.split('/')[-1].split('.')[0]}.mp4")
    # original_clip = VideoFileClip(path)
    # original_clip.write_videofile(new_path,
    #                               codec='libx264',
    #                               audio_codec='aac',  # Super important for sound
    #                               remove_temp=True)
    original_file = cv2.VideoCapture(path)
    height = int(original_file.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width = int(original_file.get(cv2.CAP_PROP_FRAME_WIDTH))

    if width % 2 != 0:
        width += 1
    else:
        pass

    if height % 2 != 0:
        height += 1
    else:
        pass

    new_path = os.path.join(os.getcwd(), 'temp', f"{path.split('/')[-1].split('.')[0]}.mp4")
    original_clip = VideoFileClip(path)
    original_clip.resize(
        (width, height)
    ).write_videofile(
        new_path,
        codec='libx264',
        audio_codec='aac',  # Super important for sound
        remove_temp=True
    )
    original_clip.close()
    if os.path.exists(path):
        os.remove(path)

    return new_path


def check_mimetype(path):
    result = {'mime_type': filetype.guess(path).mime}
    return result


def get_file_information(path, file_type):
    if file_type.__contains__('image'):
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
    if file_type.__contains__('image'):
        original_file = cv2.imread(original_file_path, cv2.IMREAD_COLOR)
        height, width, channel = original_file.shape

        for new_width in RESIZE_WIDTHS_IMAGE:
            new_height = int(new_width * height / width)
            resized_file = cv2.resize(original_file, dsize=(new_width, new_height), interpolation=cv2.INTER_LINEAR)
            temp_path = './temp'
            original_file_name = original_file_path.split('/')[-1]
            resized_file_name = f"{original_file_name.split('.')[0]}_w{str(new_width)}.{extension}"
            resized_file_path = os.path.join(temp_path, resized_file_name)
            cv2.imwrite(resized_file_path, resized_file)
            resized_file_list.append(resized_file_path)
    else:
        pass
        # original_file = cv2.VideoCapture(original_file_path)
        # height = int(original_file.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # width = int(original_file.get(cv2.CAP_PROP_FRAME_WIDTH))
        #
        # for new_width in RESIZE_WIDTHS_VIDEO:
        #     if new_width % 2 != 0:
        #         new_width += 1
        #     else:
        #         pass
        #
        #     new_height = int(new_width * height / width)
        #     if new_height % 2 != 0:
        #         new_height += 1
        #     else:
        #         pass
        #
        #     temp_path = './temp'
        #     original_file_name = original_file_path.split('/')[-1]
        #     resized_file_name = f"{original_file_name.split('.')[0]}_w{str(new_width)}.{extension}"
        #     resized_file_path = os.path.join(temp_path, resized_file_name)
        #
        #     os.system(f"ffmpeg -i {original_file_path} -vf scale={new_width}x{new_height} {resized_file_path}")
        #     # mp.VideoFileClip(original_file_path).resize((new_width, new_height)).write_videofile(resized_file_path,
        #     #                                                                                      codec='libx264',
        #     #                                                                                      audio_codec='aac', # Super important for sound
        #     #                                                                                      remove_temp=True)
        #
        #     resized_file_list.append(resized_file_path)

    return resized_file_list
# endregion
