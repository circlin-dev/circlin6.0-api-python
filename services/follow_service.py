from adapter.repository.follow import AbstractFollowRepository
from domain.user import Follow
from helper.function import failed_response


def get_one_by_user_and_target(user_id: int, target_id: int, follow_repo: AbstractFollowRepository) -> Follow or None:
    exists = follow_repo.get_one(user_id, target_id)
    return True if exists == 1 else False


def follow(user_id: int, target_id: int, follow_repo: AbstractFollowRepository) -> dict:
    exist = get_one_by_user_and_target(user_id, target_id, follow_repo)
    if exist:
        error_message = '이미 팔로잉하는 유저입니다.'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    else:
        follow_repo.add(user_id, target_id)
        return {'result': True}


def unfollow(user_id: int, target_id: int, follow_repo: AbstractFollowRepository) -> dict:
    exist = get_one_by_user_and_target(user_id, target_id, follow_repo)
    if exist:
        follow_repo.delete(user_id, target_id)
        return {'result': True}
    else:
        error_message = '팔로잉하지 않은 유저입니다.'
        result = failed_response(error_message)
        result['status_code'] = 400
        return result


def get_followings(target_id: int, user_id: int, page_cursor: int, limit: int, follow_repo: AbstractFollowRepository):
    followings: list = follow_repo.get_following_list(target_id, user_id, page_cursor,limit)
    entries: list = [dict(
        id=following.id,
        nickname=following.nickname,
        gender=following.gender,
        area=following.area,
        followers=following.followers,
        followed=following.followed,
        cursor=following.cursor
    )for following in followings]
    return entries


def count_number_of_following(target_id: int, follow_repo: AbstractFollowRepository):
    total_count: int = follow_repo.count_number_of_following(target_id)
    return total_count


def get_followers(target_id: int, user_id: int, page_cursor: int, limit: int, follow_repo: AbstractFollowRepository):
    followers: list = follow_repo.get_follower_list(target_id, user_id, page_cursor, limit)
    entries: list = [dict(
        id=follower.id,
        nickname=follower.nickname,
        gender=follower.gender,
        area=follower.area,
        followers=follower.followers,
        followed=follower.followed,
        cursor=follower.cursor
    )for follower in followers]
    return entries


def count_number_of_follower(target_id: int, follow_repo: AbstractFollowRepository):
    total_count: int = follow_repo.count_number_of_follower(target_id)
    return total_count
