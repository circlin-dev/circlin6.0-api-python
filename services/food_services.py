from adapter.repository.food import AbstractFoodRepository
from adapter.repository.food_brand import AbstractFoodBrandRepository
from adapter.repository.food_category import AbstractFoodCategoryRepository
from adapter.repository.food_flavor import AbstractFoodFlavorRepository
from adapter.repository.food_image import AbstractFoodImageRepository
from adapter.repository.food_rating import AbstractFoodRatingRepository
from adapter.repository.food_review import AbstractFoodReviewRepository
from adapter.repository.food_food_category import AbstractFoodFoodCategoryRepository
from domain.food import Food, FoodBrand, FoodImage
from services import file_service

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


def add_food(
        new_food: Food,
        food_brand: FoodBrand,
        food_category: dict,
        flavor_tags: list,
        food_repo: AbstractFoodRepository,
        food_brand_repo: AbstractFoodBrandRepository,
        food_category_repo: AbstractFoodCategoryRepository,
        food_food_category_repo: AbstractFoodFoodCategoryRepository,
        food_flavor_repo: AbstractFoodFlavorRepository
):
    # 1. new_food가 이미 등록된 제품인지 확인
    target_food = food_repo.get_one(new_food)

    if target_food is not None:
        result = {'result': False, 'error': f"'{target_food.title}'은 이미 등록된 식품입니다. 다른 이름의 식품을 등록해 보세요.", 'status_code': 400}
        return result
    else:
        # 2. food_brands에 존재하지 않는 브랜드명은 새로 등록 후 id SELECT
        food_brand_repo.add_if_not_exists(food_brand)
        food_brand = food_brand_repo.get_one(food_brand)

        new_food.brand_id = None if food_brand is None else food_brand.id

        # 3. Food 데이터 저장
        new_food_id = food_repo.add_one(new_food)

        # 4. food_category 검색한 후 food_food_category에 데이터 등록
        category = food_category_repo.get_one(food_category)
        category_id = category.id if category is not None else 145  # 145: large == '기타', medium == null, small == null

        food_food_category_repo.add(new_food_id, category_id)
        # 5. flavor tags 등록
        if len(flavor_tags) == 0:
            pass
        else:
            food_flavor_repo.add(new_food_id, flavor_tags)

        # 6. return
        result = {'result': True, 'foodId': new_food_id}
        return result


def create_food_images(food_id: int, type: str, file, s3_object_path: str, food_image_repo: AbstractFoodImageRepository):
    food_image_data: dict = file_service.upload_single_file_to_s3(file, s3_object_path)

    original_food_image: dict = food_image_data['original_file']
    resized_food_images: [dict, None] = food_image_data['resized_file']
    new_original_food_image: FoodImage = FoodImage(
        id=None,
        food_id=food_id,
        type=type,
        path=original_food_image['path'],
        file_name=original_food_image['file_name'],
        mime_type=original_food_image['mime_type'],
        size=original_food_image['size'],
        width=original_food_image['width'],
        height=original_food_image['height'],
        original_file_id=None
    )

    original_file_id = food_image_repo.add(type, new_original_food_image)

    if resized_food_images is []:
        pass
    else:
        for resized_file in resized_food_images:
            resized_board_image: FoodImage = FoodImage(
                id=None,
                food_id=food_id,
                type=type,
                path=resized_file['path'],
                file_name=resized_file['file_name'],
                mime_type=resized_file['mime_type'],
                size=resized_file['size'],
                width=resized_file['width'],
                height=resized_file['height'],
                original_file_id=original_file_id
            )
            food_image_repo.add(type, resized_board_image)

    return True

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


