shopping_list = []
while True:
    print("Меню:""\n1.Добавить товар" "\n2.Удалить товар" "\n3.Показать список товаров" "\n4.Выйти")   
    a = int(input("Выберите действие 1 - 4: "))
    if a == 1:
        b = input("Введите название товара, который вы хотите добавить: ")
        shopping_list.append(b)
            
            
    if a == 2:
        c = input("Введите название товара, который вы хотите удалить: ")
        if c in shopping_list:
            shopping_list.remove(c)
        else:
            print("Товар не найден")
    if a == 3:
        for i , item in enumerate(shopping_list, 1):
            print(i, item)
    if a == 4:
        for i , item in enumerate(shopping_list, 1):
            print(i, item)
        break


    