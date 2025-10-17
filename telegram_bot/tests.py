from django.test import TestCase
from unittest.mock import patch, MagicMock
from .bot import TelegramBot
from .tasks import send_habit_reminders, check_habit_completion, send_daily_summary
from habits.models import Habit, HabitLog
from django.contrib.auth.models import User
from datetime import time
from django.utils import timezone


class TelegramBotTest(TestCase):
    """Тесты для Telegram бота"""
    
    def setUp(self):
        self.bot = TelegramBot()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @patch('telegram_bot.bot.bot.send_reminder')
    def test_send_reminder(self, mock_send_reminder):
        """Тест отправки напоминания"""
        message = "Тестовое напоминание"
        chat_id = "123456789"
        
        # Мокаем асинхронный метод
        import asyncio
        asyncio.run(self.bot.send_reminder(message, chat_id))
        
        # Проверяем, что метод был вызван
        mock_send_reminder.assert_called_once()


class TelegramTasksTest(TestCase):
    """Тесты для задач Telegram"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.habit = Habit.objects.create(
            user=self.user,
            place='Дома',
            time=time(9, 0),
            action='Читать книгу',
            estimated_time=60,
            is_pleasant=False
        )
    
    @patch('telegram_bot.tasks.bot.send_reminder')
    def test_send_habit_reminders(self, mock_send_reminder):
        """Тест отправки напоминаний о привычках"""
        # Мокаем время
        with patch('telegram_bot.tasks.timezone.now') as mock_now:
            mock_now.return_value = timezone.datetime(2024, 1, 1, 9, 0, 0)
            
            # Выполняем задачу
            send_habit_reminders.delay()
            
            # Проверяем, что напоминание было отправлено
            mock_send_reminder.assert_called()
    
    @patch('telegram_bot.tasks.bot.send_reminder')
    def test_check_habit_completion(self, mock_send_reminder):
        """Тест проверки выполнения привычек"""
        # Выполняем задачу
        check_habit_completion.delay()
        
        # Проверяем, что проверка была выполнена
        mock_send_reminder.assert_called()
    
    @patch('telegram_bot.tasks.bot.send_reminder')
    def test_send_daily_summary(self, mock_send_reminder):
        """Тест отправки ежедневной сводки"""
        # Создаем лог выполнения
        HabitLog.objects.create(
            habit=self.habit,
            is_completed=True
        )
        
        # Выполняем задачу
        send_daily_summary.delay()
        
        # Проверяем, что сводка была отправлена
        mock_send_reminder.assert_called()