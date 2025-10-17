import os
import django
from django.conf import settings

# Настройка Django для тестов
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'habits_tracker.settings')
django.setup()
