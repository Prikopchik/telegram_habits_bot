from celery import shared_task
from django.utils import timezone
from datetime import datetime, timedelta
from .bot import bot
from habits.models import Habit
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_habit_reminders():
    """Отправка напоминаний о привычках"""
    try:
        current_time = timezone.now().time()
        current_date = timezone.now().date()
        
        # Получаем все привычки, которые нужно выполнить сейчас
        habits_to_remind = Habit.objects.filter(
            time__hour=current_time.hour,
            time__minute=current_time.minute,
            is_pleasant=False  # Напоминаем только о полезных привычках
        )
        
        for habit in habits_to_remind:
            # Проверяем, не напоминали ли уже сегодня
            last_reminder = habit.logs.filter(
                completed_at__date=current_date
            ).first()
            
            if not last_reminder:
                message = f"⏰ Напоминание о привычке!\n\n"
                message += f"Действие: {habit.action}\n"
                message += f"Место: {habit.place}\n"
                message += f"Время: {habit.time.strftime('%H:%M')}\n"
                message += f"Время на выполнение: {habit.estimated_time} сек.\n"
                
                if habit.reward:
                    message += f"Вознаграждение: {habit.reward}\n"
                elif habit.related_habit:
                    message += f"Связанная привычка: {habit.related_habit.action}\n"
                
                # Отправляем напоминание
                bot.send_reminder(message, str(habit.user.id))
                logger.info(f"Reminder sent for habit {habit.id}")
        
        logger.info("Habit reminders task completed successfully")
        
    except Exception as e:
        logger.error(f"Error in send_habit_reminders task: {e}")


@shared_task
def check_habit_completion():
    """Проверка выполнения привычек"""
    try:
        current_date = timezone.now().date()
        
        # Получаем все привычки пользователей
        habits = Habit.objects.filter(is_pleasant=False)
        
        for habit in habits:
            # Проверяем, была ли привычка выполнена сегодня
            today_log = habit.logs.filter(
                completed_at__date=current_date,
                is_completed=True
            ).first()
            
            if not today_log:
                # Если привычка не была выполнена, отправляем напоминание
                message = f"⚠️ Вы не выполнили привычку сегодня!\n\n"
                message += f"Действие: {habit.action}\n"
                message += f"Место: {habit.place}\n"
                message += f"Время: {habit.time.strftime('%H:%M')}\n"
                
                bot.send_reminder(message, str(habit.user.id))
                logger.info(f"Completion check reminder sent for habit {habit.id}")
        
        logger.info("Habit completion check task completed successfully")
        
    except Exception as e:
        logger.error(f"Error in check_habit_completion task: {e}")


@shared_task
def send_daily_summary():
    """Отправка ежедневной сводки"""
    try:
        current_date = timezone.now().date()
        
        # Получаем всех пользователей с привычками
        users_with_habits = Habit.objects.values_list('user', flat=True).distinct()
        
        for user_id in users_with_habits:
            user_habits = Habit.objects.filter(user_id=user_id, is_pleasant=False)
            completed_today = 0
            total_habits = user_habits.count()
            
            for habit in user_habits:
                if habit.logs.filter(
                    completed_at__date=current_date,
                    is_completed=True
                ).exists():
                    completed_today += 1
            
            message = f"📊 Ежедневная сводка\n\n"
            message += f"Выполнено привычек: {completed_today}/{total_habits}\n"
            message += f"Процент выполнения: {(completed_today/total_habits*100):.1f}%\n"
            
            if completed_today == total_habits:
                message += "🎉 Отлично! Все привычки выполнены!"
            elif completed_today > 0:
                message += "👍 Хорошая работа! Продолжайте в том же духе!"
            else:
                message += "💪 Не расстраивайтесь! Завтра новый день!"
            
            bot.send_reminder(message, str(user_id))
        
        logger.info("Daily summary task completed successfully")
        
    except Exception as e:
        logger.error(f"Error in send_daily_summary task: {e}")
