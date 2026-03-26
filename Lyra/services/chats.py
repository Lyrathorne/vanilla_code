from db.fake_db import chats, users


def generate_chat_id():
    if not chats:
        return 1
    return max(chat["id"] for chat in chats) + 1


def get_chats():
    return chats


def get_chat(chat_id: int):
    for chat in chats:
        if chat["id"] == chat_id:
            return chat
    return None


def user_exists(user_id: int):
    for user in users:
        if user["id"] == user_id:
            return True
    return False


def create_chat(chat: dict):
    if not chat["member_ids"]:
        return {"Error": "Chat must have members"}

    for user_id in chat["member_ids"]:
        if not user_exists(user_id):
            return {"Error": f"User with id {user_id} not found"}

    if not chat["is_group"] and len(chat["member_ids"]) != 2:
        return {"Error": "Private chat must have exactly 2 members"}

    new_chat = {
        "id": generate_chat_id(),
        "title": chat["title"],
        "is_group": chat["is_group"],
        "member_ids": chat["member_ids"],
    }

    chats.append(new_chat)
    return new_chat


def delete_chat(chat_id: int):
    for i, chat in enumerate(chats):
        if chat["id"] == chat_id:
            deleted_chat = chats.pop(i)
            return deleted_chat
    return None


def add_member(chat_id: int, user_id: int):
    chat = get_chat(chat_id)
    if chat is None:
        return {"Error": "Chat not found"}

    if not user_exists(user_id):
        return {"Error": "User not found"}

    if not chat["is_group"]:
        return {"Error": "Cannot change members in private chat"}

    if user_id in chat["member_ids"]:
        return {"Error": "User already in chat"}

    chat["member_ids"].append(user_id)
    return chat


def remove_member(chat_id: int, user_id: int):
    chat = get_chat(chat_id)
    if chat is None:
        return {"Error": "Chat not found"}

    if not chat["is_group"]:
        return {"Error": "Cannot change members in private chat"}

    if user_id not in chat["member_ids"]:
        return {"Error": "User is not in chat"}

    chat["member_ids"].remove(user_id)
    return chat