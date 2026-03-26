from datetime import datetime
from db.fake_db import messages, users, chats


def generate_message_id():
    if not messages:
        return 1
    return max(message["id"] for message in messages) + 1


def get_messages():
    return messages


def get_message(message_id: int):
    for message in messages:
        if message["id"] == message_id:
            return message
    return None


def get_chat(chat_id: int):
    for chat in chats:
        if chat["id"] == chat_id:
            return chat
    return None


def get_user(user_id: int):
    for user in users:
        if user["id"] == user_id:
            return user
    return None


def create_message(message: dict):
    chat = get_chat(message["chat_id"])
    if chat is None:
        return {"Error": "Chat not found"}

    user = get_user(message["sender_id"])
    if user is None:
        return {"Error": "User not found"}

    if not user["is_active"]:
        return {"Error": "User is offline"}

    if message["sender_id"] not in chat["member_ids"]:
        return {"Error": "User is not a member of this chat"}

    if not message["text"].strip():
        return {"Error": "Message text cannot be empty"}

    new_message = {
        "id": generate_message_id(),
        "chat_id": message["chat_id"],
        "sender_id": message["sender_id"],
        "text": message["text"],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "is_read": False,
    }

    messages.append(new_message)
    return new_message


def delete_message(message_id: int):
    for i, message in enumerate(messages):
        if message["id"] == message_id:
            deleted_message = messages.pop(i)
            return deleted_message
    return None


def get_messages_by_chat(chat_id: int):
    result = []

    for message in messages:
        if message["chat_id"] == chat_id:
            result.append(message)

    return result


def get_messages_by_user(user_id: int):
    result = []

    for message in messages:
        if message["sender_id"] == user_id:
            result.append(message)

    return result


def count_messages_in_chat(chat_id: int):
    count = 0

    for message in messages:
        if message["chat_id"] == chat_id:
            count += 1

    return count


def get_last_message(chat_id: int):
    chat_messages = get_messages_by_chat(chat_id)

    if not chat_messages:
        return None

    return chat_messages[-1]


def mark_as_read(message_id: int):
    for i, message in enumerate(messages):
        if message["id"] == message_id:
            messages[i]["is_read"] = True
            return messages[i]
    return None