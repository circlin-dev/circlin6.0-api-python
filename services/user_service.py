from adapter.repository.user_favorite_category import AbstractUserFavoriteCategoryRepository
from adapter.repository.user import AbstractUserRepository
from domain.user import UserFavoriteCategory, User


def get_a_user(user_id: int, repo: AbstractUserRepository) -> User:
    user: User = repo.get_one(user_id)
    return user


def chosen_category(category_id: int, my_category_list: list) -> bool:
    return category_id in my_category_list


def get_favorite_mission_categories(user_id: int, repo) -> list:
    my_category_list = repo.get_favorites(user_id)
    return my_category_list


def add_to_favorite_mission_category(new_mission_category: UserFavoriteCategory, repo: AbstractUserFavoriteCategoryRepository) -> dict:
    my_category_list = repo.get_favorites(new_mission_category.user_id)

    if chosen_category(new_mission_category.mission_category_id, my_category_list):
        return {'result': False, 'error': '이미 내 목표로 설정한 목표를 중복 추가할 수 없습니다!'}
    else:
        repo.add(new_mission_category)
        return {'result': True}


def delete_from_favorite_mission_category(mission_category_to_delete: UserFavoriteCategory, repo: AbstractUserFavoriteCategoryRepository) -> dict:
    my_category_list = repo.get_favorites(mission_category_to_delete.user_id)

    if not chosen_category(mission_category_to_delete.mission_category_id, my_category_list):
        return {'result': False, 'error': '내 목표로 설정하지 않은 목표를 삭제할 수 없습니다!'}
    else:
        repo.delete(mission_category_to_delete)
        return {'result': True}
