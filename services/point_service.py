from adapter.repository.point_history import AbstractPointHistoryRepository
from adapter.repository.user import AbstractUserRepository
from helper.constant import BASIC_COMPENSATION_AMOUNT_PER_REASON, DAILY_POINT_LIMIT_FOR_FEED_CHECK_FEED_COMMENT, REASONS_HAVE_DAILY_REWARD_RESTRICTION
from domain.point_history import PointHistory
from domain.user import User


def get_point_history_of_user(user_id: int, point_history_repo: AbstractPointHistoryRepository) -> list:
    pass


def get_a_point_history(point_history: PointHistory, point_history_repo: AbstractPointHistoryRepository) -> PointHistory:
    record = point_history_repo.get_one(point_history)
    return None if record.id is None else record


def does_the_reason_have_upper_limit_on_receiving_per_day(reason: str):
    return True if reason in REASONS_HAVE_DAILY_REWARD_RESTRICTION else False


def points_available_to_receive_for_the_rest_of_the_day(user_id: int, reasons: list, point_history_repo: AbstractPointHistoryRepository):
    """
    :param user_id:
    :param reasons: 포인트 지급/회수 사유
    :param point_history_repo:
    :return: 오늘 하루 reasons 배열에 해당하는 사유로 획득할 수 있는 남은 금액, 획득한 포인트의 총합(current_gathered_point)
    """
    current_gathered_point: int = point_history_repo.calculate_daily_gathered_point_by_reasons(user_id, reasons)
    available_point: int = DAILY_POINT_LIMIT_FOR_FEED_CHECK_FEED_COMMENT - current_gathered_point
    return available_point, current_gathered_point


def determine_foreign_key_by_reason(target_user: User, reason: str, amount: int, foreign_key_value: dict) -> PointHistory:
    # feed
    if reason in ["feed_check", "feed_check_reward", "feed_upload_product", "feed_upload_place"]:
        foreign_key: str = "feed_id"
        new_point_history: PointHistory = PointHistory(
            user_id=target_user.id,
            point=amount,
            reason=reason,
            result=int(target_user.point) + amount,
            feed_id=foreign_key_value["feed_id"]
        )
    # feed_comment
    elif reason in ["feed_comment_reward", "feed_comment_delete"]:
        new_point_history: PointHistory = PointHistory(
            user_id=target_user.id,
            point=amount,
            reason=reason,
            result=int(target_user.point) + amount,
            feed_id=foreign_key_value["feed_id"],
            feed_comment_id=foreign_key_value["feed_comment_id"]
        )
    # order
    elif reason in ["order_use_point", "order_cancel"]:
        new_point_history: PointHistory = PointHistory(
            user_id=target_user.id,
            point=amount,
            reason=reason,
            result=int(target_user.point) + amount,
            order_id=foreign_key_value["order_id"]
        )
    # mission
    elif reason in ["mission_reward", "challenge_reward"]:
        new_point_history: PointHistory = PointHistory(
            user_id=target_user.id,
            point=amount,
            reason=reason,
            result=int(target_user.point) + amount,
            mission_id=foreign_key_value["mission_id"]
        )
    # food_rating
    elif reason in ["review_food"]:
        new_point_history: PointHistory = PointHistory(
            user_id=target_user.id,
            point=amount,
            reason=reason,
            result=int(target_user.point) + amount,
            food_rating_id=foreign_key_value["food_rating_id"]
        )
    else:
        new_point_history: PointHistory = PointHistory(
            user_id=target_user.id,
            point=amount,
            reason=reason,
            result=int(target_user.point) + amount,
        )

    return new_point_history


def calculate_real_compensate_amount_with_daily_limit(current_available_amount: int, current_gathered_point, nominal_point: int) -> int:
    if current_gathered_point < DAILY_POINT_LIMIT_FOR_FEED_CHECK_FEED_COMMENT:
        if current_gathered_point + nominal_point > DAILY_POINT_LIMIT_FOR_FEED_CHECK_FEED_COMMENT:
            real_point = current_available_amount
        else:
            real_point = nominal_point
    else:
        real_point = 0

    return real_point


def give_point(target_user: User, reason: str, request_point: int or None, foreign_key_value: dict, point_history_repo: AbstractPointHistoryRepository, user_repo: AbstractUserRepository):
    # 당일 지급액 상한선이 걸려있는 지급 사유의 경우, 현재 기준으로 획득 가능한 포인트 금액으로 조정
    if reason in BASIC_COMPENSATION_AMOUNT_PER_REASON.keys():
        if does_the_reason_have_upper_limit_on_receiving_per_day(reason):
            current_available_amount, current_gathered_point = points_available_to_receive_for_the_rest_of_the_day(target_user.id, REASONS_HAVE_DAILY_REWARD_RESTRICTION, point_history_repo)
            amount = calculate_real_compensate_amount_with_daily_limit(current_available_amount, current_gathered_point, BASIC_COMPENSATION_AMOUNT_PER_REASON[reason])
        else:
            amount = BASIC_COMPENSATION_AMOUNT_PER_REASON[reason]
    else:
        amount = request_point

    if amount > 0:
        data = determine_foreign_key_by_reason(target_user, reason, amount, foreign_key_value)
        point_history_repo.add(data)
        user_repo.update_current_point(target_user, data.result)
    else:
        pass

    return amount


def deduct_point(target_user: User, reason: str, request_point: int or None, foreign_key_value: dict, point_history_repo: AbstractPointHistoryRepository, user_repo: AbstractUserRepository):
    if reason in BASIC_COMPENSATION_AMOUNT_PER_REASON.keys():
        amount = BASIC_COMPENSATION_AMOUNT_PER_REASON[reason]
    else:
        amount = request_point

    data = determine_foreign_key_by_reason(target_user, reason, amount, foreign_key_value)
    point_history_repo.add(data)
    user_repo.update_current_point(target_user, data.result)
