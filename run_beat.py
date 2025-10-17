#!/usr/bin/env python
"""
Скрипт для запуска Celery beat
"""
import os
import sys
from celery import Celery

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Устанавливаем переменную окружения для Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'habits_tracker.settings')

# Импортируем Django
import django
django.setup()

# Создаем экземпляр Celery
app = Celery('habits_tracker')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

if __name__ == '__main__':
    app.start()
