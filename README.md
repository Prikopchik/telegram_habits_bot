Установка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd habits_tracker
```

2. Создайте виртуальное окружение:
```bash
venv\Scripts\activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` в корне проекта на основе `env.example`:
```bash
cp env.example .env
```
Затем отредактируйте `.env` файл, заменив значения:
```env
SECRET_KEY=your_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
REDIS_URL=redis://localhost:6379/0
```

5. Выполните миграции:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

## Запуск

1. Запустите Django сервер:
```bash
python manage.py runserver
```

2. Запустите Celery worker:
```bash
celery -A habits_tracker worker -l info
```

3. Запустите Celery beat для периодических задач:
```bash
celery -A habits_tracker beat -l info
```

## API Документация

После запуска сервера документация доступна по адресам:
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/

## Эндпоинты

### Пользователи
- `POST /api/v1/users/register/` - Регистрация пользователя
- `GET /api/v1/users/` - Список пользователей

### Привычки
- `GET /api/v1/habits/my_habits/` - Мои привычки
- `GET /api/v1/habits/public_habits/` - Публичные привычки
- `POST /api/v1/habits/` - Создать привычку
- `GET /api/v1/habits/{id}/` - Получить привычку
- `PUT /api/v1/habits/{id}/` - Обновить привычку
- `DELETE /api/v1/habits/{id}/` - Удалить привычку
- `POST /api/v1/habits/{id}/complete/` - Отметить как выполненную
- `GET /api/v1/habits/{id}/logs/` - Логи выполнения

## Тестирование

Запуск тестов:
```bash
pytest
```

Запуск тестов с покрытием:
```bash
pytest --cov=habits --cov=telegram_bot --cov-report=html
```

## Проверка кода

Проверка с помощью Flake8:
```bash
flake8
```
