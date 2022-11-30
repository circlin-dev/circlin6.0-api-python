class Food:
    def __init__(
            self,
            id: int or None,
            brand: str,
            large_category_title: str,
            title: str,
            user_id: int,
            type: str,
            container: str,
            amount_per_serving: float,
            total_amount: float,
            unit: str,
            servings_per_container: float,
            price: [int, float, None],
            calorie: float,
            carbohydrate: float,
            protein: float,
            fat: float,
            sodium: float,
            sugar: float,
            trans_fat: float,
            saturated_fat: float,
            cholesterol: float,
            url: str,
            approved_at: str,
            original_data: dict or None,
            deleted_at: str or None
    ):
        self.id = id
        self.brand = brand
        self.large_category_title = large_category_title
        self.title = title
        self.price = price
        self.user_id = user_id
        self.type = type
        self.container = container
        self.amount_per_serving = amount_per_serving
        self.total_amount = total_amount
        self.unit = unit
        self.servings_per_container = servings_per_container
        self.calorie = calorie
        self.carbohydrate = carbohydrate
        self.protein = protein
        self.fat = fat
        self.sodium = sodium
        self.sugar = sugar
        self.trans_fat = trans_fat
        self.saturated_fat = saturated_fat
        self.cholesterol = cholesterol
        self.url = url
        self.approved_at = approved_at
        self.original_data = original_data
        self.deleted_at = deleted_at


class FoodBrand:
    def __init__(self, id: int or None, type: str, title: str):
        self.id = id
        self.type = type
        self.title = title


class FoodCategory:
    def __init__(self, id: int or None, large: str, medium: str or None, small: str or None):
        self.id = id
        self.large = large
        self.medium = medium
        self.small = small


class FoodFlavor:
    def __init__(self, food_id: int, flavors: str):
        self.food_id = food_id
        self.flavors = flavors


class FoodFoodCategory:
    def __init__(self, food_id: int, food_category_id: int):
        self.food_id = food_id
        self.food_category_id = food_category_id


class FoodImage:
    def __init__(
            self,
            id: int or None,
            food_id: int,
            type: str,
            path: str,
            file_name: str,
            mime_type: str,
            size: int,
            width: int,
            height: int,
            original_file_id: int or None
    ):
        self.id = id
        self.board_id = food_id
        self.type = type
        self.path = path
        self.file_name = file_name
        self.mime_type = mime_type
        self.size = size
        self.width = width
        self.height = height
        self.original_file_id = original_file_id


class FoodIngredient:
    def __init__(self, food_id: int, ingredient_id: int):
        self.food_id = food_id
        self.ingredient_id = ingredient_id


class FoodRating:
    def __init__(self, id: int or None, food_id: int, user_id: int, rating: int, body: str or None):
        self.id = id
        self.food_id = food_id
        self.user_id = user_id
        self.rating = rating
        self.body = body


class FoodRatingImage:
    def __init__(
            self,
            id: int or None,
            food_rating_id: int,
            path: str,
            file_name: str,
            mime_type: str,
            size: int,
            width: int,
            height: int,
            original_file_id: int or None
    ):
        self.id = id
        self.food_rating_id = food_rating_id
        self.path = path
        self.file_name = file_name
        self.mime_type = mime_type
        self.size = size
        self.width = width
        self.height = height
        self.original_file_id = original_file_id


class FoodRatingReview:
    def __init__(self, food_rating_id: int, food_review_id: int):
        self.food_rating_id = food_rating_id
        self.food_review_id = food_review_id


class FoodReview:
    def __init__(self, id: int or None, value: str, user_id: int):
        self.id = id
        self.value = value
        self.user_id = user_id


class Ingredient:
    def __init__(self, id: int or None, value: str):
        self.id = id
        self.value = value
