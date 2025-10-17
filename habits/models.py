from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


class Habit(models.Model):
    """Модель привычки"""
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name='Пользователь',
        related_name='habits'
    )
    place = models.CharField(
        max_length=200, 
        verbose_name='Место',
        help_text='Место, в котором необходимо выполнять привычку'
    )
    time = models.TimeField(
        verbose_name='Время',
        help_text='Время, когда необходимо выполнять привычку'
    )
    action = models.CharField(
        max_length=200, 
        verbose_name='Действие',
        help_text='Действие, которое представляет собой привычка'
    )
    is_pleasant = models.BooleanField(
        default=False,
        verbose_name='Приятная привычка',
        help_text='Привычка, которую можно привязать к выполнению полезной привычки'
    )
    related_habit = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Связанная привычка',
        help_text='Приятная привычка, которая связана с полезной привычкой'
    )
    periodicity = models.PositiveIntegerField(
        default=1,
        verbose_name='Периодичность (дни)',
        help_text='Периодичность выполнения привычки для напоминания в днях'
    )
    reward = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Вознаграждение',
        help_text='Чем пользователь должен себя вознаградить после выполнения'
    )
    estimated_time = models.PositiveIntegerField(
        verbose_name='Время на выполнение (секунды)',
        help_text='Время, которое предположительно потратит пользователь на выполнение привычки'
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name='Публичная привычка',
        help_text='Привычки можно публиковать в общий доступ'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Привычка'
        verbose_name_plural = 'Привычки'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action} в {self.place} в {self.time}"

    def clean(self):
        """Валидация модели"""
        errors = {}
        
        # Исключить одновременный выбор связанной привычки и указания вознаграждения
        if self.related_habit and self.reward:
            errors['related_habit'] = 'Нельзя одновременно указывать связанную привычку и вознаграждение'
            errors['reward'] = 'Нельзя одновременно указывать связанную привычку и вознаграждение'
        
        # Время выполнения должно быть не больше 120 секунд
        if self.estimated_time and self.estimated_time > 120:
            errors['estimated_time'] = 'Время выполнения должно быть не больше 120 секунд'
        
        # В связанные привычки могут попадать только привычки с признаком приятной привычки
        if self.related_habit and not self.related_habit.is_pleasant:
            errors['related_habit'] = 'В связанные привычки могут попадать только приятные привычки'
        
        # У приятной привычки не может быть вознаграждения или связанной привычки
        if self.is_pleasant:
            if self.reward:
                errors['reward'] = 'У приятной привычки не может быть вознаграждения'
            if self.related_habit:
                errors['related_habit'] = 'У приятной привычки не может быть связанной привычки'
        
        # Нельзя выполнять привычку реже, чем 1 раз в 7 дней
        if self.periodicity > 7:
            errors['periodicity'] = 'Нельзя выполнять привычку реже, чем 1 раз в 7 дней'
        
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class HabitLog(models.Model):
    """Модель для отслеживания выполнения привычек"""
    
    habit = models.ForeignKey(
        Habit,
        on_delete=models.CASCADE,
        verbose_name='Привычка',
        related_name='logs'
    )
    completed_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата и время выполнения'
    )
    is_completed = models.BooleanField(
        default=True,
        verbose_name='Выполнено'
    )

    class Meta:
        verbose_name = 'Лог привычки'
        verbose_name_plural = 'Логи привычек'
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.habit.action} - {self.completed_at.strftime('%d.%m.%Y %H:%M')}"