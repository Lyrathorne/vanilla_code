from models.user import User
from models.chat import Chat
import models.chat
import models.message
import models.user
def main() -> None:
    users = [
        User(username="Alex123", online=True, age=20, phone_number="111111"),
        User(username="Mira7", online=True, age=19, phone_number="222222"),
        User(username="Dan9", online=False, age=21, phone_number="333333"),
    ]

    chat = Chat()

    while True:
        models.chat.print_menu()
        choice = input("Выбери действие: ").strip()

        if choice == "1":
            chat.show_chat()

        elif choice == "2":
            models.chat.send_message_menu(chat, users)

        elif choice == "3":
            print(f"\nКоличество сообщений: {chat.count_messages()}\n")

        elif choice == "4":
            models.chat.show_last_message(chat)

        elif choice == "5":
            models.chat.show_messages_by_user(chat, users)

        elif choice == "6":
            models.chat.show_users(users)

        elif choice == "7":
            models.chat.change_user_status(users)

        elif choice == "8":
            new_user = models.chat.create_user()
            if new_user is not None:
                users.append(new_user)

        elif choice == "9":
            print("Выход из программы.")
            break

        else:
            print("Неизвестная команда.\n")


if __name__ == "__main__":
    main()