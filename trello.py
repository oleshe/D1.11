"""
TODO:
+ Добавьте рядом с названием колонки цифру, отражающую количество задач в ней.
+ Реализуйте создание колонок.
+ Обработайте совпадающие имена задач *
Как вы думаете, что случится, если у нас появится две задачи с одинаковым именем? Реализуйте обработку такой ситуации.
Пользователь должен иметь возможность управлять всеми задачами вне зависимости от того, как он их называет.

Сейчас при работе с задачей мы перебираем все задачи и работаем с первой найденной по имени. Нужно проверять,
имеются ли еще задачи с таким именем и выводить их в консоль. Помимо имени должны быть указаны: колонка,
в которой находится эта задача, и другие параметры, по которым можно было бы отличить одну задачу от другой.
Пользователю должно быть предложено дополнительно ввести (при помощи функции input) номер для выбора задачи
из полученного списка. Наш клиент должен работать с выбранной задачей.

Загрузка ключа, токена и идентификатора доски выполняется из json файла "data_file.json"
Пожалуйста, прежде чем запускать trello.py заполните этот файл!!!
"""
import sys
import requests
import json

with open("data_file.json", "r") as write_file:
    DLoad = json.load(write_file)

# Данные авторизации в API Trello
auth_params = {
    'key': DLoad['key'],
    'token': DLoad['token'], }

# Идентификатор доски
board_id = DLoad['board_id']

# Адрес, на котором расположен API Trello, # Именно туда мы будем отправлять HTTP запросы.
base_url = DLoad['base_url'] #"https://api.trello.com/1/{}"

def read():
    # Получим данные всех колонок на доске:
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()

    # Теперь выведем название каждой колонки и всех заданий, которые к ней относятся:
    for column in column_data:
        # Получим данные всех задач в колонке и перечислим все названия
        task_data = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        # print(column['name'], len(task_data))
        print('Колонка "%s" (кол-во задач - %s) ' % (column['name'], len(task_data)))
        if not task_data:
            print('\t' + 'Нет задач!')
            continue
        for task in task_data:
            print('\t' + task['name'])

def createcol(column_name):
    # Создание колонки с именем column_name на доске board_id
    requests.post(base_url.format('boards') + '/' + board_id + '/lists', data={'name':column_name, 'pos':"top", **auth_params})

def create(name, column_name):
    # Получим данные всех колонок на доске
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()

    # Переберём данные обо всех колонках, пока не найдём ту колонку, которая нам нужна
    for column in column_data:
        if column['name'] == column_name:
            # Создадим задачу с именем _name_ в найденной колонке
            requests.post(base_url.format('cards'), data={'name': name, 'idList': column['id'], **auth_params})
            break

def coin_name(name, column_name):
    """
    При перемещении задачи провести проверку на существование одноименной задачи
    При существовании одноименных задач - вывести порядковый номер  + колонку в которой находится + dateLastActivity
    Запросить с какой работать по порядковому номеру
    :param name: имя задачи
    :param column_name: колонка куда перемещается задача
    :return: task_id
    """
    # Получим данные всех колонок на доске
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()

    # Среди всех колонок нужно найти задачу по имени и получить её id
    task_id = []
    for column in column_data:
        # Пропускаем колонку в котору собираемся перемещать, саму в себя нет смысла перемещать
        if column['name'] == column_name : continue
        column_tasks = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        for task in column_tasks:
            if task['name'] == name :
                task_id.append((task['id'], task['dateLastActivity'], column['id'], column['name']))
    if len(task_id) == 1 :
        return task_id[0][0]
    if len(task_id) > 1 :
        print("Найдено больше одной задачи, выбирете которую переносить?")
        for index, item in enumerate(task_id) :
            print(index, 'Задача "%s" найдена в колонке "%s", с датой последней активности "%s"' % (name, item[3], item[1]))
        item = int(input())
        return task_id[item][0]
    return task_id

def move(name, column_name):
    # Получим данные всех колонок на доске
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
    task_id = coin_name(name, column_name)
    if not task_id :
        print("Такой задачи не найдено")
        return
    # Теперь, когда у нас есть id задачи, которую мы хотим переместить
    # Переберём данные обо всех колонках, пока не найдём ту, в которую мы будем перемещать задачу
    for column in column_data:
        if column['name'] == column_name:
            # И выполним запрос к API для перемещения задачи в нужную колонку
            requests.put(base_url.format('cards') + '/' + task_id + '/idList',
                         data={'value': column['id'], **auth_params})
            break

if __name__ == "__main__":
    if len(sys.argv) <= 2:
        read()
    elif sys.argv[1] == 'create':
        create(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'createcol':
        createcol(sys.argv[2])
    elif sys.argv[1] == 'move':
        move(sys.argv[2], sys.argv[3])
