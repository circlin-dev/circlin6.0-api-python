class ChatMessage:
    def __init__(
            self,
            created_at: str,
            chat_room_id: int,
            user_id: int,
            type: str,
            message: str,
            image_type: str,
            image: str,
            **kwargs
    ):
        self.created_at = created_at
        self.chat_room_id = chat_room_id
        self.user_id = user_id
        self.type = type
        self.message = message
        self.image_type = image_type
        self.image = image
        self.feed_id = kwargs.get("feed_id")
        self.mission_id = kwargs.get("mission_id")


class ChatRoom:
    def __init__(
            self,
            created_at: str,
            title: str,
            is_group: int
    ):
        self.created_at = created_at
        self.title = title
        self.is_group = is_group


class ChatUser:
    def __init__(
            self,
            chat_room_id: int,
            user_id: int,
            is_block: bool or int,
            message_notify: bool or int,
            enter_message_id: int or None,
            read_message_id: int or None
    ):
        self.chat_room_id = chat_room_id
        self.user_id = user_id
        self.is_block = is_block
        self.message_notify = message_notify
        self.enter_message_id = enter_message_id
        self.read_message_id = read_message_id
