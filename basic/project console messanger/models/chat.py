from dataclasses import dataclass
from datetime import datetime
import string
from models.message import Message
from models.user import User
class Chat:
    def __init__(self):
        self._messages = []

    def add_message(self, message: Message) -> None:
        self._messages.append(message)

    def send_message(self, user: User, text: str) -> Message:
        if not user.online:
            raise ValueError(f"Пользователь '{user.username}' оффлайн и не может отправлять сообщения.")

        if not text.strip():
            raise ValueError("Нельзя отправить пустое сообщение.")

        timestamp = datetime.now().strftime("%H:%M:%S")
        message = Message(sender=user, text=text, timestamp=timestamp)
        self._messages.append(message)
        return message

    def show_chat(self) -> None:
        if not self._messages:
            print("\nЧат пуст.\n")
            return

        print("\n--- Чат ---")
        for message in self._messages:
            print(message)
        print("------------\n")

    def get_messages_by_user(self, user: User) -> list[Message]:
        result = []

        for message in self._messages:
            if message.sender == user:
                result.append(message)

        return result

    def get_all_messages(self) -> list[Message]:
        return self._messages.copy()

    def count_messages(self) -> int:
        return len(self._messages)

    def last_message(self) -> Message | None:
        if not self._messages:
            return None
        return self._messages[-1]


def show_users(users: list[User]) -> None:
    print("\nПользователи:")
    for index, user in enumerate(users, start=1):
        status = "online" if user.online else "offline"
        print(f"{index}. {user.username} ({status})")
    print()


def choose_user(users: list[User]) -> User | None:
    show_users(users)

    choice = input("Выбери номер пользователя: ").strip()

    if not choice.isdigit():
        print("Нужно ввести число.")
        return None

    index = int(choice) - 1

    if index < 0 or index >= len(users):
        print("Такого пользователя нет.")
        return None

    return users[index]


def create_user() -> User | None:
    print("\n--- Создание пользователя ---")
    username = input("Введите username (только латиница и цифры): ").strip()

    if not User.validate_username(username):
        print("Некорректный username.")
        return None

    age_text = input("Введите возраст: ").strip()
    if not age_text.isdigit():
        print("Возраст должен быть числом.")
        return None

    phone_number = input("Введите номер телефона: ").strip()

    online_text = input("Пользователь онлайн? (yes/no): ").strip().lower()
    if online_text == "yes":
        online = True
    elif online_text == "no":
        online = False
    else:
        print("Нужно ввести yes или no.")
        return None

    user = User(
        username=username,
        online=online,
        age=int(age_text),
        phone_number=phone_number
    )

    print(f"Пользователь {user.username} создан.\n")
    return user


def show_messages_by_user(chat: Chat, users: list[User]) -> None:
    user = choose_user(users)
    if user is None:
        return

    messages = chat.get_messages_by_user(user)

    if not messages:
        print(f"\nУ пользователя {user.username} пока нет сообщений.\n")
        return

    print(f"\nСообщения пользователя {user.username}:")
    for message in messages:
        print(message)
    print()


def change_user_status(users: list[User]) -> None:
    user = choose_user(users)
    if user is None:
        return

    print(f"\nТекущий статус {user.username}: {'online' if user.online else 'offline'}")
    action = input("Введи 'on' чтобы сделать online, 'off' чтобы сделать offline: ").strip().lower()

    if action == "on":
        user.go_online()
        print(f"{user.username} теперь online.\n")
    elif action == "off":
        user.go_offline()
        print(f"{user.username} теперь offline.\n")
    else:
        print("Неизвестная команда.\n")


def send_message_menu(chat: Chat, users: list[User]) -> None:
    user = choose_user(users)
    if user is None:
        return

    text = input("Введите текст сообщения: ")

    try:
        message = chat.send_message(user, text)
        print("Сообщение отправлено:")
        print(message)
        print()
    except ValueError as error:
        print("Ошибка:", error)
        print()


def show_last_message(chat: Chat) -> None:
    message = chat.last_message()

    if message is None:
        print("\nВ чате пока нет сообщений.\n")
        return

    print("\nПоследнее сообщение:")
    print(message)
    print()


def print_menu() -> None:
    print("=== Консольный мессенджер ===")
    print("1 - Показать чат")
    print("2 - Отправить сообщение")
    print("3 - Показать количество сообщений")
    print("4 - Показать последнее сообщение")
    print("5 - Показать сообщения конкретного пользователя")
    print("6 - Показать пользователей")
    print("7 - Изменить статус пользователя")
    print("8 - Создать нового пользователя")
    print("9 - Выход")