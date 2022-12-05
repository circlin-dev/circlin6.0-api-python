from adapter.repository.food import AbstractFoodRepository
from adapter.repository.food_category import AbstractFoodCategoryRepository
from adapter.repository.food_rating import AbstractFoodRatingRepository
from adapter.repository.food_review import AbstractFoodReviewRepository
from domain.food import Food

import json


# region food
def get_food_list(word: str, page_cursor: int, limit: int, food_repo: AbstractFoodRepository):
    foods = food_repo.get_list(word, page_cursor, limit)
    entries = [dict(
        id=food.id,
        largeCategoryTitle=food.large_category_title,
        title=food.title,
        brand=food.brand,
        nutrition=json.loads(food.nutrition),
        price=food.price,
        totalAmount=food.total_amount,
        unit=food.unit,
        amountPerServing=food.amount_per_serving,
        container=food.container,
        images=json.loads(food.images) if food.images is not None else [],
        cursor=food.cursor
    ) for food in foods] if foods is not None else []

    return entries


def get_count_of_foods(word: str, food_repo: AbstractFoodRepository) -> int:
    return food_repo.count_number_of_food(word)


def add_food(new_food: Food, food_repo: AbstractFoodRepository):
    pass

# endregion







# region food category
def get_food_categories(food_category_repo: AbstractFoodCategoryRepository):
    categories = food_category_repo.get_list()
    entries = [dict(
        id=category.id,
        large=category.large,
        medium=category.medium,
        small=category.small
    ) for category in categories]
    return entries
# endregion


# region food rating
def get_rating_list_by_food_and_user(food_id: int, user_id: int, food_rating_repo: AbstractFoodRatingRepository):
    ratings = food_rating_repo.get_rating_list_by_food_and_user(food_id, user_id)
    return ratings


def get_food_review_tags(food_review_repo: AbstractFoodReviewRepository):
    tags: list = food_review_repo.get_list()
    entries = [dict(id=tag.id, value=tag.value) for tag in tags]
    return entries
# endregion


