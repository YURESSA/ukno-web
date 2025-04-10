# UKNO Backend

Это серверная часть проекта **UKNO**. Она предоставляет API для регистрации, аутентификации и работы с пользователями. В проекте используется **Flask** для создания веб-приложения, **MySQL** для базы данных, **JWT** для аутентификации и **Flasgger** для генерации документации API.

## Технологии

- **Python 3.x**
- **Flask** — веб-фреймворк
- **Flask-SQLAlchemy** — для работы с базой данных
- **Flask-JWT-Extended** — для аутентификации с помощью JWT
- **Flask-RestX** — для документации API
- **MySQL** — реляционная база данных
- **Alembic** — для миграций базы данных
- **Werkzeug** — для хеширования паролей

## Установка и настройка

### Шаг 1: Клонирование репозитория

Склонируйте репозиторий на свою машину:

```bash
    git clone https://github.com/your-username/ukno.git
    cd ukno
```

### Шаг 2: Создание виртуального окружения

Создайте виртуальное окружение и активируйте его:

```bash
    python -m venv .venv
```

На Windows:

```bash
    .venv\Scripts\activate
```

На macOS и Linux:

```bash
    source .venv/bin/activate
```

### Шаг 3: Установка зависимостей

Создайте виртуальное окружение и активируйте его

```bash
    pip install -r requirements.txt
```

### Шаг 4: Миграции базы данных

Процесс миграции для инициализации базы данных:

```bash
    flask db init
    flask db migrate
    flask db upgrade
```

### Шаг 5: Запуск приложения

Запустите приложение:

```bash
    flask run
```

## Документация API

Для получения подробной документации о доступных API, вы можете использовать Swagger. Просто откройте браузер и перейдите по следующему URL:

http://127.0.0.1:5000

Документация будет доступна для следующих эндпоинтов:

POST /auth/register — Регистрация нового пользователя.

POST /auth/login — Аутентификация пользователя и получение JWT.

GET /auth/protected — Защищенный маршрут, доступный только для авторизованных пользователей.

## Контакты
Если у вас возникли вопросы, не стесняйтесь обращаться:

Email: youremail@example.com

GitHub: https://github.com/your-username