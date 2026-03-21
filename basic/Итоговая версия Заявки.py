numbers_of_id = [i for i in range(1, 1000000)]
ids = []
orders = []
keys = ["ID", "Клиент", "Контакт", "Категория", "Приоритет", "Статус", "Стоимость", "Исполнитель", "Теги"]
order_names = []

def show_menu():
    print("1. Создать заявку")
    print("2. Показать все заявки")
    print("3. Редактировать заявку")
    print("4. Найти заявку по id")
    print("5. Удалить заявку")
    print("6. Фильтр заявок")
    print("7. Поиск по тексту")
    print("8. Выйти")

def generate_id():
    order_id = numbers_of_id.pop(0)
    ids.append(order_id)
    return order_id

def generate_order():
    order_name = input("Введите название вашей заявки: ")
    if order_name in order_names:
        print("Данное имя занято, введите другое: ")
        return generate_order()

    order_names.append(order_name)
    d = dict.fromkeys(keys, None)
    return d

def validate_priority():
    print("Выберите приоритет вашей заявки: ")
    print("1. Высокий")
    print("2. Средний")
    print("3. Низкий")

    while True:
        priority = input("Введите число: ")
        if priority == "1":
            return "high"
        elif priority == "2":
            return "middle"
        elif priority == "3":
            return "low"
        else:
            print("Введите число от 1 до 3")

def validate_status(order_id):
    if order_id == max(ids):
        return "new"
    else:
        return "old"

def create_order():
    order_id = generate_id()
    name = input("Введите ваше имя: ").lower()
    contact = input("Введите контактные данные: ").lower()
    category = input("Введите категорию вашей заявки: ").lower()
    priority = validate_priority()
    status = validate_status(order_id)
    price = int(input("Введите стоимость(в руб): "))
    contractor = input("Введите имя исполнителя: ").lower()
    tags = input("Введите теги через запятую: ").lower()

    d = generate_order()
    d["ID"] = order_id
    d["Клиент"] = name
    d["Категория"] = category
    d["Приоритет"] = priority
    d["Статус"] = status
    d["Стоимость"] = price
    d["Исполнитель"] = contractor
    d["Контакт"] = contact
    d["Теги"] = tags

    orders.append(d)

def show_orders():
    print(orders)

def find_order():
    order_id = int(input("Введите ID: "))
    for order in orders:
        if order.get("ID") == order_id:
            print(order)
            return
    print("Заявка не найдена")

def redact_order():
    order_id = int(input("Введите ID заявки: "))
    for order in orders:
        if order["ID"] == order_id:
            key = input("Введите параметр, который хотите исправить: ")
            if key not in keys:
                print("Такого параметра не существует")
                return
            order[key] = input("Введите исправление: ")                                          
            return order

    print("Заявка не найдена")

def delete_order():
    order_id = int(input("Введите ID заявки: "))
    for order in orders:
        if order["ID"] == order_id:
            orders.remove(order)
            print("Заявка удалена")
            return
    print("Заявка не найдена")

def filter_orders():
    print("Выберите вид сортировки: ")
    print("1. Сначала старые")
    print("2. Сначала новые")
    choose_sortion = int(input("Введите число: "))
    if choose_sortion == 1:
        print(orders)
    elif choose_sortion == 2:
        print(orders[::-1])
    else:
        print("Надо ввести 1 или 2")

def find_text():
    text = input("Введите текст который хотите найти: ").lower()
    for order in orders:
        for value in order.values():
            if text in str(value).lower():
                print(order)
                break

while True:
    show_menu()
    choice = int(input("Введите число от 1 до 8: "))
    if choice == 1:
        create_order()
    elif choice == 2:
        show_orders()
    elif choice == 3:
        redact_order()
    elif choice == 4:
        find_order()
    elif choice == 5:
        delete_order()
    elif choice == 6:
        filter_orders()
    elif choice == 7:
        find_text()
    elif choice == 8:
        break
    else:
        print("Введите число от 1 до 8: ")
        continue