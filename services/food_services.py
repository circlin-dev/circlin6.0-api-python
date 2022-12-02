from adapter.repository.food_category import AbstractFoodCategoryRepository
import json


def get_food_categories(food_category_repo: AbstractFoodCategoryRepository):
    categories = food_category_repo.get_list()
    entries = [dict(
        id=category.id,
        large=category.large,
        medium=category.medium,
        small=category.small
    ) for category in categories]
    return entries
