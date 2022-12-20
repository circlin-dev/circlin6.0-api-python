from adapter.repository.chat_message import AbstractChatMessageRepository


def count_unread_messages_by_user(user_id: int, chat_message_repo: AbstractChatMessageRepository):
    unread_count = chat_message_repo.count_unread_messages(user_id)
    return unread_count
