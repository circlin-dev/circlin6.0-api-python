from adapter.repository.block import AbstractBlockRepository
from domain.block import Block
from helper.function import failed_response
import json


def get_one_by_user_and_target(user_id: int, target_id: int, block_repo: AbstractBlockRepository) -> Block or None:
    exists = block_repo.get_one(user_id, target_id)
    return True if exists == 1 else False


def block(user_id: int, target_id: int, block_repo: AbstractBlockRepository) -> dict:
    exist = get_one_by_user_and_target(user_id, target_id, block_repo)
    if exist:
        error_message = '이미 차단한 유저입니다.'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    else:
        block_repo.add(user_id, target_id)
        return {'result': True}


def unblock(user_id: int, target_id: int, block_repo: AbstractBlockRepository) -> dict:
    exist = get_one_by_user_and_target(user_id, target_id, block_repo)
    if exist:
        block_repo.delete(user_id, target_id)
        return {'result': True}
    else:
        error_message = '차단되지 않은 유저입니다.'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result


def get_list(user_id: int, page_cursor: int, limit: int, block_repo: AbstractBlockRepository) -> list:
    block_list = block_repo.get_list(user_id, page_cursor, limit)
    entries = [dict(
        id=block_user.id,
        nickname=block_user.nickname,
        gender=block_user.gender,
        greeting=block_user.greeting,
        profile=block_user.profile_image,
        cursor=block_user.cursor
    ) for block_user in block_list]
    return entries


def count_number_of_blocked_user(user_id: int, block_repo: AbstractBlockRepository) -> int:
    total_count = block_repo.count_number_of_blocked_user(user_id)
    return total_count
