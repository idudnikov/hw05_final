<h2 align="center">Портал для блогов Yatube</h2>

Yatube - это портал, который позволяет пользователям создавать, изменять и удалять записи, . Он позволяет работать с данными портала Yatube (получать, создавать, изменять и удалять) через API.  

## Установка и использование

### Установка

Клонируйте файлы проекта в локальное хранилище и перейдите в папку с проектом:

`git clone https://github.com/idudnikov/hw05_final.git`

Создайте и активируйте виртуальное окружение:

`python3 -m venv venv`

`source env/bin/activate`

Установите зависимости:

`python3 -m pip install --upgrade pip`

`pip install -r requirements.txt`

Выполните миграции:

`python3 manage.py migrate`

Запустите проект:

`python3 manage.py runserver`

### Использование

Проект доступен по адресу http://127.0.0.1/.<br/>
Админ-панель django доступна по адресу http://127.0.0.1/admin/.
