from adapter.orm import areas, delete_users, feeds, feed_likes, follows, notifications, point_histories, user_stats, user_wallpapers
from domain.user import User, UserFavoriteCategory, UserStat

import abc
from sqlalchemy.sql import func
from sqlalchemy import and_, case, insert, select, text, update


class AbstractUserRepository(abc.ABC):
    @abc.abstractmethod
    def add(self,
            login_method: str,
            email: str,
            password: str or None,
            sns_email: str,
            phone_number: str,
            device_type: str,
            agree_terms_and_policy: bool,
            agree_privacy: bool,
            agree_location: bool,
            agree_email_marketing: bool,
            agree_sms_marketing: bool,
            agree_advertisement: bool,
            invite_code: str,
            ):
        pass

    @abc.abstractmethod
    def user_data(self, user_id: int):
        pass

    @abc.abstractmethod
    def get_one(self, user_id: int) -> User:
        pass

    @abc.abstractmethod
    def get_one_by_email(self, email: str) -> User:
        pass

    @abc.abstractmethod
    def get_one_by_invite_code(self, invite_code: str) -> User:
        pass

    @abc.abstractmethod
    def get_one_by_nickname(self, nickname: str) -> User:
        pass

    @abc.abstractmethod
    def get_list(self) -> User:
        pass

    @abc.abstractmethod
    def get_push_target(self, targets: list) -> list:
        pass

    @abc.abstractmethod
    def update(self, target_user: User):
        pass

    @abc.abstractmethod
    def update_current_point(self, target_user: User, point: int):
        pass

    @abc.abstractmethod
    def update_password(self, target_user: User, decoded_hashed_new_password: str):
        pass

    @abc.abstractmethod
    def update_profile_image(self, user_id: int, new_image: str or None):
        pass

    @abc.abstractmethod
    def update_info_when_email_login(self, user_id: int, client_ip: str, device_type: str):
        pass

    @abc.abstractmethod
    def update_info_when_sns_login(self, user_id: int, sns_email: str, phone_number: str, sns_name: str, client_ip: str, device_type: str):
        pass

    @abc.abstractmethod
    def delete(self, user_id: int, reason: str or None):
        pass


class UserRepository(AbstractUserRepository):
    def __init__(self, session):
        self.session = session

    def add(self,
            login_method: str,
            email: str,
            password: str or None,
            sns_email: str or None,
            phone_number: str or None,
            device_type: str,
            agree_terms_and_policy: bool,
            agree_privacy: bool,
            agree_location: bool,
            agree_email_marketing: bool,
            agree_sms_marketing: bool,
            agree_advertisement: bool,
            invite_code: str,
            ):
        sql = insert(
            User
        ).values(
            login_method=login_method,
            email=email,
            password=password,
            sns_email=sns_email,
            phone=phone_number,
            device_type=device_type,
            agree1=agree_terms_and_policy,
            agree2=agree_privacy,
            agree3=agree_location,
            agree4=agree_email_marketing,
            agree5=agree_sms_marketing,
            agree_push=True,
            agree_push_mission=True,
            agree_ad=agree_advertisement,
            invite_code=invite_code,
        )
        result = self.session.execute(sql)
        return result.inserted_primary_key[0]

    def user_data(self, user_id: int):
        area = select(
            areas.c.name
        ).where(
            areas.c.code == func.concat(func.substring(User.area_code, 1, 5), '00000')
        ).limit(1)

        number_of_checks_user_did_yesterday = select(
            func.count(feed_likes.c.id)
        ).where(
            and_(
                feed_likes.c.user_id == User.id,
                feed_likes.c.deleted_at == None,
                func.TIMESTAMPDIFF(text("DAY"), func.now(), func.DATE(feed_likes.c.created_at)) == -1,
            )
        )

        number_of_checks_user_received_yesterday = select(
            func.count(feed_likes.c.id)
        ).join(
            feeds, feed_likes.c.feed_id == feeds.c.id
        ).where(
            and_(
                feeds.c.user_id == User.id,
                feed_likes.c.deleted_at == None,
                func.TIMESTAMPDIFF(text("DAY"), func.now(), func.DATE(feed_likes.c.created_at)) == -1
            )
        )

        unread_notifications_count = select(
            func.count(notifications.c.id)
        ).where(
            and_(
                notifications.c.target_id == User.id,
                notifications.c.read_at == None
            )
        )

        sql = select(
            User.id,
            User.agree1,  # agreeTermsAndPolicy - 서비스 이용약관
            User.agree2,  # agreePrivacy - 개인정보 이용 약관
            User.agree3,  # agreeLocation - 위치정보 이용
            User.agree4,  # agreeEmailMarketing - 이메일 마케팅 수신
            User.agree5,  # agreeSmsMarketing - SMS 마케팅 수신
            User.agree_push,
            User.agree_push_mission,
            User.agree_ad,
            area.label('area'),
            func.date_format(user_stats.c.birthday, '%Y/%m/%d').label('birthday'),
            User.gender,
            User.greeting,
            User.invite_code,
            User.nickname,
            User.point,
            User.profile_image,
            func.json_arrayagg(
                func.json_object(
                    'id', user_wallpapers.c.id,
                    'createdAt', func.date_format(user_wallpapers.c.created_at, '%Y/%m/%d %H:%i:%s'),
                    'title', user_wallpapers.c.title,
                    'path', user_wallpapers.c.image
                )
            ).label('wallpapers'),
            unread_notifications_count.label('unread_notifications_count'),
            number_of_checks_user_did_yesterday.label('number_of_checks_user_did_yesterday'),
            number_of_checks_user_received_yesterday.label('number_of_checks_user_received_yesterday')
        ).select_from(
            User
        ).join(
            user_stats, user_stats.c.user_id == User.id, isouter=True
        ).join(
            user_wallpapers, user_wallpapers.c.user_id == User.id, isouter=True
        ).where(
            and_(
                User.id == user_id,
                User.deleted_at == None,
            )
        ).limit(1)
        result = self.session.execute(sql).first()
        return result

    def get_one(self, user_id: int) -> User:
        area = select(
            areas.c.name
        ).where(
            areas.c.code == func.concat(func.substring(User.area_code, 1, 5), '00000')
        ).limit(1)

        sql = select(
            User.id,
            area.label('area'),
            User.area_code,
            User.greeting,
            User.invite_code,
            User.login_method,
            User.email,
            User.sns_email,
            User.gender,
            User.nickname,
            User.password,
            User.profile_image,
            User.point,
            User.device_type,
            User.agree1,  # agree_terms_and_policy
            User.agree2,  # agree_privacy,
            User.agree3,  # agree_location,
            User.agree4,  # agree_email_marketing,
            User.agree5,  # agree_sms_marketing,
            User.agree_push,
            User.agree_push_mission,
            User.agree_ad,  # agree_advertisement,
        ).where(
            and_(User.id == user_id, User.deleted_at == None)
        ).limit(1)
        user = self.session.execute(sql).first()
        return user

    def get_one_by_email(self, email: str) -> User:
        sql = select(
            User
        ).where(
            and_(User.email == email, User.deleted_at == None)
        ).limit(1)
        user = self.session.execute(sql).scalars().first()
        return user

    def get_one_by_invite_code(self, invite_code: str) -> User:
        sql = select(
            User
        ).where(
            and_(User.invite_code == invite_code, User.deleted_at == None)
        ).limit(1)
        user = self.session.execute(sql).scalars().first()
        return user

    def get_one_by_nickname(self, nickname: str) -> User:
        sql = select(
            User
        ).where(
            and_(User.nickname == nickname, User.deleted_at == None)
        ).limit(1)
        user = self.session.execute(sql).scalars().first()
        return user

    def get_list(self):
        sql = select(User).limit(10)
        users = self.session.execute(sql).scalars().all()
        return users

    def get_push_target(self, targets: list) -> list:
        sql = select(
            User.id,
            User.nickname,
            User.device_token,
            User.device_type
        ).where(
            and_(
                User.id.in_(targets),
                User.device_token != None,
                User.device_token != '',
                User.agree_push == 1
            )
        )

        push_targets: list = self.session.execute(sql).all()
        return push_targets

    def update(self, target_user: User):
        # service에서 유저 class를 만들어서 새 값들로 변경한 다음, 여기서 업데이트 일괄 하면 될듯..
        return self.session.query(User).filter_by(id=target_user.id).update(
            {
                "nickname": target_user.nickname,
                "area_code": target_user.area_code,
                "greeting": target_user.greeting,
                "gender": target_user.gender,
                "agree4": target_user.agree_email_marketing,
                "agree5": target_user.agree_sms_marketing,
                "agree_push": target_user.agree_push,
                "agree_push_mission": target_user.agree_push_mission,
                "agree_ad": target_user.agree_advertisement
            },
            synchronize_session="fetch"
        )

    def update_current_point(self, target_user: User, point: int):
        sql = update(
            User
        ).where(
            User.id == target_user.id
        ).values(
            point=point
        )
        return self.session.execute(sql)

    def update_password(self, target_user: User, decoded_hashed_new_password: str):
        sql = update(
            User
        ).where(
            User.id == target_user.id
        ).values(
            password=decoded_hashed_new_password
        )
        return self.session.execute(sql)

    def update_profile_image(self, user_id: int, new_image: str or None):
        sql = update(User).where(User.id == user_id).values(profile_image=new_image)
        return self.session.execute(sql)

    def update_info_when_email_login(self, user_id: int, client_ip: str, device_type: str):
        sql = update(
            User
        ).where(
            User.id == user_id
        ).values(
            last_login_ip=client_ip,
            last_login_at=func.now(),
            device_type=device_type
        )
        return self.session.execute(sql)

    def update_info_when_sns_login(self, user_id: int, sns_email: str, phone_number: str, sns_name: str, client_ip: str, device_type: str):
        sql = update(
            User
        ).where(
            User.id == user_id
        ).values(
            sns_email=sns_email,
            phone=phone_number,
            login_method=sns_name,
            last_login_ip=client_ip,
            last_login_at=func.now(),
            device_type=device_type
        )
        return self.session.execute(sql)

    def delete(self, user_id: int, reason: str or None):
        sql = update(User).where(User.id == user_id).values(deleted_at=func.now())
        self.session.execute(sql)

        sql = insert(delete_users).values(user_id=user_id, reason=reason)
        self.session.execute(sql)
        return True
