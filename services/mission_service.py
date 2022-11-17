from adapter.repository.mission_category import AbstractMissionCategoryRepository
from domain.mission import MissionCategory


def get_mission_categories(repo, favorite_mission_categories: list):
    category_list = repo.get_list()

    entries = [dict(id=category.id,
                    key=str(category.id),
                    missionCategoryId=category.mission_category_id,
                    title=category.title,
                    emoji=category.emoji if category.emoji is not None else '',
                    description=category.description if category.description is not None else '',
                    isFavorite=True if category.id in favorite_mission_categories else False
                    ) for category in category_list]
    return entries
