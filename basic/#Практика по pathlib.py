 #Практика по pathlib
#Задание: “Анализатор папки проекта”
#Напиши программу, которая анализирует указанную папку на компьютере.
#Что должно уметь:
#Пользователь вводит путь к папке
#Программа выводит:
#существует ли папка
#сколько в ней файлов
#сколько подпапок
#список файлов с расширением .py
#Отдельно покажи:
#все .txt файлы
#все пустые файлы
#самый большой файл в папке
from pathlib import Path


def input_path():
    path = input("Введите путь к папке: ")
    folder = Path(path)
    return folder


def path_check(folder):
    if folder.exists() and folder.is_dir():
        print("Папка существует")
        return True
    else:
        print("Папка не существует")
        return False


def count_files(folder):
    files = 0
    for item in folder.iterdir():
        if item.is_file():
            files += 1
    print("Файлов:", files)


def count_folders(folder):
    folders = 0
    for item in folder.iterdir():
        if item.is_dir():
            folders += 1
    print("Подпапок:", folders)


def find_py(folder):
    print(".py файлы:")
    for item in folder.iterdir():
        if item.is_file() and item.suffix == ".py":
            print(item.name)


def others(folder):
    print(".txt файлы:")
    for item in folder.iterdir():
        if item.is_file() and item.suffix == ".txt":
            print(item.name)

    print("Пустые файлы:")
    for item in folder.iterdir():
        if item.is_file() and item.stat().st_size == 0:
            print(item.name)

    largest_size = -1
    largest_file = None

    for item in folder.iterdir():
        if item.is_file():
            size = item.stat().st_size
            if size > largest_size:
                largest_size = size
                largest_file = item

    if largest_file is not None:
        print("Самый большой файл:", largest_file.name)
    else:
        print("В папке нет файлов")


folder = input_path()

if path_check(folder):
    count_files(folder)
    count_folders(folder)
    find_py(folder)
    others(folder)
        



          
