shopping_list = []
while True:
    a = input("Введите название товара: ")
    
    if a == "Удалить":
        
        i = input("Введите название товара для удаления: ")
        if i in shopping_list:
            shopping_list.remove(i)
            
        
    elif a == "Конец":
        
        for i, item in enumerate(shopping_list, 1):
            print(i, item)
        break
    elif a == "проверка":
        x = input("Введите название: ")
        if x in shopping_list:
            print("Товар присутствует")
        else:
            print("Товар отсутствует")
        
    else:
        shopping_list.append(a)
    
    for i, item in enumerate(shopping_list, 1):
        print(i, item)