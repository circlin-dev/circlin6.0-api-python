class DeleteUser:
    def __init__(self, user_id: int, reason: str or None):
        self.user_id = user_id
        self.reason = reason


class Follow:
    def __init__(self, user_id: int, target_id: int):
        self.user_id = user_id
        self.target_id = target_id


class User:
    def __init__(
            self,
            id: int or None,
            login_method: str,
            sns_email: str,
            email: str,
            nickname: str or None,
            greeting: str or None,
            gender: str or None,
            point: int,
            profile_image: str,
            invite_code: str,
            **kwargs
    ):
        self.id = id
        self.login_method = login_method
        self.sns_email = sns_email
        self.email = email
        self.nickname = nickname
        self.greeting = greeting
        self.gender = gender
        self.point = point
        self.profile_image = profile_image
        self.invite_code = invite_code
        self.device_type = kwargs.get('device_type')
        self.agree_terms_and_policy = kwargs.get('agree_terms_and_policy')
        self.agree_privacy = kwargs.get('agree_privacy')
        self.agree_location = kwargs.get('agree_location')
        self.agree_email_marketing = kwargs.get('agree_email_marketing')
        self.agree_sms_marketing = kwargs.get('agree_sms_marketing')

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


class UserStat:
    def __init__(
            self,
            user_id: int,
            birthday: str or None,
            height: float or None,
            weight: float or None,
            bmi: float or None,
            yesterday_feeds_count: int or None
    ):
        self.user_id = user_id
        self.birthday = birthday
        self.height = height
        self.weight = weight
        self.bmi = bmi
        self.yesterday_feeds_count: yesterday_feeds_count


class UserWallpaper:
    def __init__(self, id: int or None, created_at: str, user_id: int, title: str, image: str):
        self.id = id
        self.created_at = created_at
        self.user_id = user_id
        self.title = title
        self.image = image
