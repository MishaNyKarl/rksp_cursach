# article_review_service

Учебное клиент-серверное веб-приложение на Django для публикации и рецензирования статей. Проект сделан как минимально работоспособный MVP для курсовой работы: есть роли пользователей, авторизация, статьи, категории, рецензии, админ-панель, демонстрационные данные и подготовка к деплою.

## Стек технологий

- Python 3.11+
- Django 5
- SQLite для локальной разработки
- PostgreSQL-ready настройки через `DATABASE_URL`
- HTML, CSS, Bootstrap 5, Django Templates
- WhiteNoise для static files
- Docker, docker-compose
- Gunicorn

## Архитектура

Проект реализует трехуровневую клиент-серверную архитектуру:

1. Клиентская часть: браузер, HTML-шаблоны, Bootstrap 5.
2. Сервер приложений: Django views, forms, модели и проверки прав.
3. Сервер базы данных: SQLite локально, PostgreSQL через `DATABASE_URL`.

## Роли пользователей

- `author`: создает статьи, редактирует свои черновики и статьи на доработке, отправляет их на рецензирование, смотрит рецензии.
- `reviewer`: видит назначенные ему статьи, открывает их, оставляет рецензии и принимает решение.
- `admin`: через Django admin управляет пользователями, профилями, категориями, статьями, рецензентами и статусами.

## Функциональность

- регистрация, вход и выход;
- профиль пользователя с ролью;
- создание и редактирование статей;
- отправка статьи на рецензирование;
- назначение рецензента через админ-панель;
- список статей автора;
- список статей рецензента;
- создание рецензии с решением: принять, отправить на доработку, отклонить;
- автоматическое обновление статуса статьи после рецензии;
- Bootstrap-интерфейс для скриншотов в отчёт.

## Локальный запуск

```bash
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

На Windows PowerShell активация окружения:

```powershell
venv\Scripts\Activate.ps1
```

Если нужно использовать конкретно Python 3.11:

```bash
py -3.11 -m venv venv
source venv/Scripts/activate
```

После запуска приложение доступно по адресу: `http://127.0.0.1:8000/`.

## Тестовые аккаунты

После выполнения `python manage.py seed_data` создаются:

| Роль | Логин | Пароль |
| --- | --- | --- |
| Администратор | `admin` | `admin12345` |
| Автор | `author` | `author12345` |
| Рецензент | `reviewer` | `reviewer12345` |

## Основные URL

- `/` — главная страница;
- `/accounts/register/` — регистрация;
- `/accounts/login/` — вход;
- `/accounts/dashboard/` — личный кабинет;
- `/articles/` — мои статьи;
- `/articles/create/` — создание статьи;
- `/articles/reviewer/` — статьи, назначенные рецензенту;
- `/admin/` — админ-панель Django.

## Работа сценария

1. Войти под `author`.
2. Создать статью.
3. Открыть статью и нажать «Отправить».
4. Войти в `/admin/` под `admin`.
5. Назначить статье рецензента `reviewer` и при необходимости статус `На рецензировании`.
6. Войти под `reviewer`.
7. Открыть раздел «Рецензирование».
8. Оставить рецензию и выбрать решение.
9. Войти под `author` и увидеть обновленный статус и рецензию.

## Docker

Сборка и запуск только веб-приложения:

```bash
docker build -t article_review_service .
docker run --rm -p 8000:8000 --env-file .env.example article_review_service
```

Запуск с PostgreSQL:

```bash
docker compose up --build
```

После старта с `docker-compose.yml` миграции и `seed_data` выполняются автоматически.

## Переменные окружения

Пример находится в `.env.example`:

```env
SECRET_KEY=
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=
```

Если `DATABASE_URL` пустой, используется SQLite `db.sqlite3`. Для PostgreSQL можно указать строку вида:

```env
DATABASE_URL=postgres://user:password@localhost:5432/dbname
```

## Структура проекта

```text
article_review_service/
  manage.py
  requirements.txt
  README.md
  Dockerfile
  docker-compose.yml
  Procfile
  .env.example
  article_review_service/
    settings.py
    urls.py
    wsgi.py
    asgi.py
  accounts/
  articles/
  reviews/
  core/
  templates/
  static/
```

## Подготовка к деплою

В проекте есть:

- `Procfile` для Render/Railway: `web: gunicorn article_review_service.wsgi:application`;
- поддержка `DATABASE_URL`;
- WhiteNoise для раздачи статических файлов;
- `ALLOWED_HOSTS` из переменной окружения;
- Dockerfile.
