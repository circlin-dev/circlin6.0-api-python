class Follow:
    def __init__(self, user_id: int, target_id: int):
        self.user_id = user_id
        self.target_id = target_id


class User:
    def __init__(
            self,
            id: int or None,
            nickname: str or None,
            greeting: str or None,
            gender: str or None,
            point: int,
            profile_image: str,
            invite_code: str,

    ):
        self.id = id
        self.nickname = nickname
        self.greeting = greeting
        self.gender = gender
        self.point = point
        self.profile_image = profile_image
        self.invite_code = invite_code

    def __eq__(self, other) -> bool:
        if not isinstance(other, User):
            return False
        return self.id == other.id


class UserFavoriteCategory:
    def __init__(
            self,
            id: int or None,
            user_id: int,
            mission_category_id: int
    ):
        self.id = id
        self.user_id = user_id
        self.mission_category_id = mission_category_id
