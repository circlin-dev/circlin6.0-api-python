from adapter.repository.point_history import AbstractPointHistoryRepository
from adapter.repository.user import AbstractUserRepository
from domain.point_history import PointHistory
from domain.user import User

import json


def points_available_for_the_rest_of_the_day(user_id: int, reasons: list, point_history_repo: AbstractPointHistoryRepository) -> int:
    gathered_point: int = point_history_repo.calculate_daily_gathered_point_by_reasons(user_id, reasons)
    available_point: int = 500 - gathered_point
    return available_point


def get_users_point_history(user_id: int, point_history_repo: AbstractPointHistoryRepository) -> list:
    pass


def get_a_point_history(point_history_repo: AbstractPointHistoryRepository) -> PointHistory:
    pass
