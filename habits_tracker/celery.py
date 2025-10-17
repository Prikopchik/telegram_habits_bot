import os
from celery import Celery
from django.conf import settings

# Устанавливаем переменную окружения для Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'habits_tracker.settings')

# Создаем экземпляр Celery
app = Celery('habits_tracker')

# Настройка Celery из настроек Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическое обнаружение задач в приложениях Django
app.autodiscover_tasks()

# Настройка расписания для периодических задач
app.conf.beat_schedule = {
    'send-habit-reminders': {
        'task': 'telegram_bot.tasks.send_habit_reminders',
        'schedule': 60.0,  # Каждую минуту
    },
    'check-habit-completion': {
        'task': 'telegram_bot.tasks.check_habit_completion',
        'schedule': 3600.0,  # Каждый час
    },
    'send-daily-summary': {
        'task': 'telegram_bot.tasks.send_daily_summary',
        'schedule': 86400.0,  # Каждый день в полночь
    },
}

app.conf.timezone = 'Europe/Moscow'


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
