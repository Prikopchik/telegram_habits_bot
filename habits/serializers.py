from rest_framework import serializers
from .models import User, Habit, HabitLog


class BaseHabitValidationMixin:
    """Миксин для валидации привычек"""
    
    def validate(self, data):
        """Валидация данных привычки"""
        errors = {}
        
        # Исключить одновременный выбор связанной привычки и указания вознаграждения
        if data.get('related_habit') and data.get('reward'):
            errors['related_habit'] = 'Нельзя одновременно указывать связанную привычку и вознаграждение'
            errors['reward'] = 'Нельзя одновременно указывать связанную привычку и вознаграждение'
        
        # Время выполнения должно быть не больше 120 секунд
        if data.get('estimated_time') and data['estimated_time'] > 120:
            errors['estimated_time'] = 'Время выполнения должно быть не больше 120 секунд'
        
        # У приятной привычки не может быть вознаграждения или связанной привычки
        if data.get('is_pleasant'):
            if data.get('reward'):
                errors['reward'] = 'У приятной привычки не может быть вознаграждения'
            if data.get('related_habit'):
                errors['related_habit'] = 'У приятной привычки не может быть связанной привычки'
        
        # Нельзя выполнять привычку реже, чем 1 раз в 7 дней
        if data.get('periodicity') and data['periodicity'] > 7:
            errors['periodicity'] = 'Нельзя выполнять привычку реже, чем 1 раз в 7 дней'
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data

    def validate_related_habit(self, value):
        """Валидация связанной привычки"""
        if value and not value.is_pleasant:
            raise serializers.ValidationError(
                'В связанные привычки могут попадать только приятные привычки'
            )
        return value


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя"""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'telegram_chat_id', 'telegram_username']
        read_only_fields = ['id']


class HabitSerializer(BaseHabitValidationMixin, serializers.ModelSerializer):
    """Сериализатор для привычки"""
    
    user = UserSerializer(read_only=True)
    related_habit = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Habit
        fields = [
            'id', 'user', 'place', 'time', 'action', 'is_pleasant',
            'related_habit', 'periodicity', 'reward', 'estimated_time',
            'is_public', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class HabitLogSerializer(serializers.ModelSerializer):
    """Сериализатор для лога привычки"""
    
    habit = HabitSerializer(read_only=True)
    
    class Meta:
        model = HabitLog
        fields = ['id', 'habit', 'completed_at', 'is_completed']
        read_only_fields = ['id']


class HabitCreateSerializer(BaseHabitValidationMixin, serializers.ModelSerializer):
    """Сериализатор для создания привычки"""
    
    class Meta:
        model = Habit
        fields = [
            'place', 'time', 'action', 'is_pleasant', 'related_habit',
            'periodicity', 'reward', 'estimated_time', 'is_public'
        ]
