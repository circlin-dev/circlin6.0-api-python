from adapter.repository.food_category import AbstractFoodCategoryRepository
from adapter.repository.food_review import AbstractFoodReviewRepository
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


def get_food_review_tags(food_review_repo: AbstractFoodReviewRepository):
    tags: list = food_review_repo.get_list()
    entries = [dict(id=tag.id, value=tag.value) for tag in tags]
    return entries
