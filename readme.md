## 🚀 UKNO – Образовательная платформа

UKNO (Ural Knowledge Network Online) — это современная образовательная платформа, разработанная для автоматизации и упрощения процесса организации и проведения мероприятий на площадке Уральского клуба нового образования. Платформа объединяет всех участников экосистемы: резидентов, модераторов и обычных пользователей, обеспечивая удобный интерфейс для создания, управления и посещения образовательных и культурных событий.

### 📚 Основные возможности

- **Управление событиями**: Резиденты могут создавать новые мероприятия (лекции, мастер-классы, семинары, выставки и другие форматы), указывая название, описание, дату, время и место проведения.
- **Запись участников**: Обычные пользователи могут регистрироваться на интересующие их события, отслеживать статус своей заявки и получать уведомления о предстоящих мероприятиях.
- **Администрирование резидентов**: Администраторы платформы имеют возможность добавлять, редактировать и удалять профиль резидентов, а также назначать им роли и права доступа.
- **Управление контентом**: Поддержка загрузки фотографий и материалов для каждого события, возможность сопровождать анонсы презентациями и документацией.
- **Аналитика и отчеты**: Собираются данные о посещаемости и активности пользователей, что позволяет резидентам и администраторам анализировать интерес и эффективность мероприятий.

---

### 🧰 Структура проекта
- **backend/**: Серверная часть приложения, реализованная с использованием Flask, PostgreSQL и SQLAlchemy.

- **frontend/**: Клиентская часть приложения, разработанная с использованием React.

- **infra/**: Инфраструктурные скрипты и конфигурации для развертывания приложения.

- **tests/**: Набор тестов для проверки функциональности приложения.

---
## 🛠️ Технологии

- **Flask** — бэкенд
- **PostgreSQL** — основная СУБД
- **SQLite** — опционально для отладки
- **Docker + Docker Compose** — контейнеризация
- **Nginx** — прокси-сервер
- **Gunicorn** — WSGI сервер
- **Flask-Migrate** — миграции базы данных
- **Brevo SMTP** — отправка почты
- **JWT** — авторизация

---

## ⚙️ .env (в корне проекта)

```env
SECRET_KEY=ural_club
JWT_SECRET_KEY=ural_club_jwt

SQLITE__URL=sqlite:///db.sqlite3
POSTGRES_URL=postgresql+psycopg2://ukno_user:ukno_pass@db:5432/ukno

MAIL_PASSWORD=
MAIL_SERVER=
MAIL_PORT=587
MAIL_USERNAME=
MAIL_DEFAULT_SENDER=
FRONTEND_URL=

POSTGRES_DB=ukno
POSTGRES_USER=ukno_user
POSTGRES_PASSWORD=ukno_pass
POSTGRES_HOST_AUTH_METHOD=md5

POSTGRES_HOST=db
POSTGRES_PORT=5432

PRODUCTION=True
USE_POSTGRESS=True

ACCOUNT_ID= 
YOOKASSA_SECRET_KEY=
```

---

## 🐳 Docker Compose

Файл `infra/docker-compose.yml` содержит конфигурацию трёх сервисов:

- **backend** — Flask-приложение
- **db** — PostgreSQL с volume `pgdata`
- **nginx** — Nginx-прокси

### Запуск

```bash
cd infra
docker compose up --build -d
```

### Остановка

```bash
docker compose down         # остановка без удаления данных
docker compose down -v      # остановка с удалением томов (⚠️ все данные будут удалены)
```

### Логи

```bash
docker logs -f flask-backend
```

### Shell в контейнере

```bash
docker exec -it flask-backend sh
docker exec -it postgres-db psql -U ukno_user -d ukno
```

---

## 👤 Суперпользователь

```bash
docker exec -it flask-backend sh
python -m backend.core.scripts.create_superuser
```

---

## 🧪 Миграции

```bash
docker exec -it flask-backend flask db migrate -m "описание"
docker exec -it flask-backend flask db upgrade
```

---

## 📖 API документация

Для получения подробной документации о доступных API, вы можете использовать Swagger.  
Откройте браузер и перейдите по адресу:

```
http://127.0.0.1:5000
```

---

## 📞 Контакты

Если у вас возникли вопросы, не стесняйтесь обращаться:

- Email: goshrenko@gmail.com
- GitHub: https://github.com/yuressa
- tg:
