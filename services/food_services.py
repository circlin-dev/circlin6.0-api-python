from adapter.repository.food import AbstractFoodRepository
from adapter.repository.food_brand import AbstractFoodBrandRepository
from adapter.repository.food_category import AbstractFoodCategoryRepository
from adapter.repository.food_flavor import AbstractFoodFlavorRepository
from adapter.repository.food_image import AbstractFoodImageRepository
from adapter.repository.food_rating import AbstractFoodRatingRepository
from adapter.repository.food_review import AbstractFoodReviewRepository
from adapter.repository.food_rating_image import AbstractFoodRatingImageRepository
from adapter.repository.food_rating_review import AbstractFoodRatingReviewRepository
from adapter.repository.food_food_category import AbstractFoodFoodCategoryRepository
from adapter.repository.notification import AbstractNotificationRepository
from adapter.repository.point_history import AbstractPointHistoryRepository
from adapter.repository.user import AbstractUserRepository
from domain.food import Food, FoodBrand, FoodImage, FoodRating, FoodRatingImage
from domain.notification import Notification
from domain.point_history import PointHistory
from domain.user import User
from helper.constant import BASIC_COMPENSATION_AMOUNT_PER_REASON
from services import file_service, notification_service, point_service, user_service

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


# region food rating
def check_if_user_rate_this_food_for_the_first_time(food_rating: FoodRating, food_rating_repo: AbstractFoodRatingRepository):
    record = food_rating_repo.get_rating_list_by_food_and_user(food_rating.food_id, food_rating.user_id)
    print('len(record): ', len(record))
    return True if len(record) < 1 else False


def add_food_rating(
        new_food_rating: FoodRating,
        selected_tag_ids: list,
        new_tags_written_by_user: list,
        food_review_repo: AbstractFoodReviewRepository,
        food_rating_repo: AbstractFoodRatingRepository,
        food_rating_review_repo: AbstractFoodRatingReviewRepository,
        # notification_repo: AbstractNotificationRepository,
        point_history_repo: AbstractPointHistoryRepository,
        user_repo: AbstractUserRepository,
):
    rated_user: User = user_repo.get_one(new_food_rating.user_id)
    # 1. 태그 데이터 처리
    if len(new_tags_written_by_user) == 0:
        pass
    else:
        # 1-1. new_tags_written_by_user(food_reviews DB에 없는 새 태그) 배열이 비어있지 않은 경우
        # food_reviews에서 해당 단어를 검색하되, 존재하지 않는 값이면 테이블에 INSERT한 후
        # last_inserted_primarykey[0]를 selected_tag_ids 배열에 추가
        for word in new_tags_written_by_user:
            word = word.strip()
            existing_word = food_review_repo.get_one(word)

            if existing_word is None:
                new_review_tag_id = food_review_repo.add(word, rated_user.id)
                selected_tag_ids.append(new_review_tag_id)
            else:
                # 1-2. new_tags_written_by_user가 이미 food_reviews에 존재하는 값이면 id를 selected_tag_ids 배열에 추가
                selected_tag_ids.append(existing_word.id)

    # 리뷰 중복 등록으로 인한 포인트 중복 지급 방지 로직
    if check_if_user_rate_this_food_for_the_first_time(new_food_rating, food_rating_repo):
        this_is_first_rating: bool = True
    else:
        this_is_first_rating: bool = False

    # 2. FoodRating 테이블에 new_food_rating 저장
    new_food_rating.id = food_rating_repo.add(new_food_rating)

    # 3. FoodRatingReview에 selected_tag_ids배열 데이터와 new_food_rating id를 저장
    food_rating_review_repo.add(new_food_rating.id, selected_tag_ids)

    # 4. 5 포인트 지급 --> 원래는 이미지 저장 완료 후에 지급했는데, service 함수가 나뉘면서 고민중...
    if this_is_first_rating:
        reason_for_point = "review_food"
        foreign_key_value_of_point_history = {'food_rating_id': new_food_rating.id}
        point_service.give_point(
            rated_user,
            reason_for_point,
            BASIC_COMPENSATION_AMOUNT_PER_REASON[reason_for_point],
            foreign_key_value_of_point_history,
            point_history_repo,
            user_repo
        )

        # 5. 알림 => 설계되지 않은 사항
        # notification: Notification = Notification(
        #     id=None,
        #     target_id=rated_user.id,
        #     type=notification_type,
        #     user_id=new_board_comment.user_id,
        #     read_at=None,
        #     variables={f'{notification_type}': new_board_comment.comment},
        #     board_id=new_board_comment.board_id,
        #     board_comment_id=inserted_board_comment_id
        # )
        # notification_service.create_notification(notification, notification_repo)
    else:
        pass
    return {"result": True, "ratingId": new_food_rating.id}


def create_food_rating_images(food_rating_id: int, file, s3_object_path: str, food_rating_image_repo: AbstractFoodRatingImageRepository):
    food_rating_image_data: dict = file_service.upload_single_file_to_s3(file, s3_object_path)

    original_food_rating_image: dict = food_rating_image_data['original_file']
    resized_food_rating_images: [dict, None] = food_rating_image_data['resized_file']
    new_original_food_rating_image: FoodRatingImage = FoodRatingImage(
        id=None,
        food_rating_id=food_rating_id,
        path=original_food_rating_image['path'],
        file_name=original_food_rating_image['file_name'],
        mime_type=original_food_rating_image['mime_type'],
        size=original_food_rating_image['size'],
        width=original_food_rating_image['width'],
        height=original_food_rating_image['height'],
        original_file_id=None
    )

    original_file_id = food_rating_image_repo.add(new_original_food_rating_image)

    if resized_food_rating_images is []:
        pass
    else:
        for resized_file in resized_food_rating_images:
            resized_board_image: FoodRatingImage = FoodRatingImage(
                id=None,
                food_rating_id=food_rating_id,
                path=resized_file['path'],
                file_name=resized_file['file_name'],
                mime_type=resized_file['mime_type'],
                size=resized_file['size'],
                width=resized_file['width'],
                height=resized_file['height'],
                original_file_id=original_file_id
            )
            food_rating_image_repo.add(resized_board_image)

    return True
