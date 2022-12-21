from adapter.orm import chat_messages, chat_rooms, chat_users
from domain.chat import ChatMessage, ChatRoom, ChatUser
from domain.user import User

import abc
from sqlalchemy import and_, desc, func, select, text
from sqlalchemy.orm import aliased


class AbstractChatMessageRepository(abc.ABC):
    @abc.abstractmethod
    def count_unread_messages(self, user_id: int) -> int:
        pass


class ChatMessageRepository(AbstractChatMessageRepository):
    def __init__(self, session):
        self.session = session

    def count_unread_messages(self, user_id: int) -> int:
        cu = aliased(chat_users)
        cr = aliased(chat_rooms)
        cm = aliased(chat_messages)
        cu_sub = aliased(chat_users)
        cu_me = aliased(chat_users)
        cu_me_ = aliased(chat_users)

        user_who_is_chatting_with_me = select(
            cu
        ).join(
            cr, cu.c.chat_room_id == cr.c.id
        ).where(
            and_(
                cu.c.chat_room_id.in_(
                    select(
                        cu_sub.c.chat_room_id
                    ).where(
                        and_(
                            cu_sub.c.user_id == user_id,
                            cu_sub.c.deleted_at == None
                        )
                    )
                ),  # 내가 나가지 않은 채팅방 목록
                cu.c.user_id != user_id
            )
        ).group_by(cu.c.user_id).alias("t")

        sql = select(
            func.sum(
                select(
                    func.count(cm.c.id)
                ).where(
                    and_(
                        cm.c.chat_room_id == text("t.chat_room_id"),  # 내가 대화중인 채팅방
                        select(
                            func.ifnull(cu_me_.c.read_message_id, 0)
                        ).where(
                            and_(
                                cu_me_.c.chat_room_id == text("t.chat_room_id"),
                                cu_me_.c.user_id == user_id
                            )
                            # ).order_by(
                            #     desc(cu_sub.id)   # 불필요한듯??
                        ).limit(1) < cm.c.id,
                        cm.c.created_at >= text("t.created_at"),  # user_who_is_chatting_with_me.c.created_at,  # 메시지의 생성 시각이 내가 대화중인 채팅방의 생성시간보다 크거나 같음
                        cm.c.user_id != user_id
                    )
                )
            )
        ).select_from(
            user_who_is_chatting_with_me
        ).join(
            cu_me, cu_me.c.chat_room_id == text("t.chat_room_id")  # user_who_is_chatting_with_me.c.chat_room_id  # 나
        ).join(
            User, text("t.user_id") == User.id # user_who_is_chatting_with_me.c.user_id == User.id  # for 대화 상대의 프로필 - 지금은 JOIN이 없어도 되나, 다른 채팅 데이터 구현할 때는 필요함
        ).where(
            and_(
                cu_me.c.user_id == user_id,
                cu_me.c.deleted_at == None,
                User.deleted_at == None
            )
        )

        unread_count = self.session.execute(sql).scalar()
        return 0 if unread_count is None else int(unread_count)
