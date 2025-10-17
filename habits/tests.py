from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import Habit, HabitLog
from datetime import time


class HabitModelTest(TestCase):
    """Тесты для модели Habit"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_habit(self):
        """Тест создания привычки"""
        habit = Habit.objects.create(
            user=self.user,
            place='Дома',
            time=time(9, 0),
            action='Читать книгу',
            estimated_time=60,
            periodicity=1
        )
        self.assertEqual(habit.user, self.user)
        self.assertEqual(habit.place, 'Дома')
        self.assertEqual(habit.action, 'Читать книгу')
        self.assertFalse(habit.is_pleasant)
        self.assertFalse(habit.is_public)
    
    def test_habit_validation_reward_and_related_habit(self):
        """Тест валидации: нельзя одновременно указывать вознаграждение и связанную привычку"""
        pleasant_habit = Habit.objects.create(
            user=self.user,
            place='Дома',
            time=time(9, 0),
            action='Приятная привычка',
            is_pleasant=True,
            estimated_time=60
        )
        
        habit = Habit(
            user=self.user,
            place='Парк',
            time=time(10, 0),
            action='Полезная привычка',
            reward='Шоколад',
            related_habit=pleasant_habit,
            estimated_time=60
        )
        
        with self.assertRaises(ValidationError):
            habit.clean()
    
    def test_habit_validation_estimated_time(self):
        """Тест валидации: время выполнения не больше 120 секунд"""
        habit = Habit(
            user=self.user,
            place='Дома',
            time=time(9, 0),
            action='Действие',
            estimated_time=150
        )
        
        with self.assertRaises(ValidationError):
            habit.clean()
    
    def test_habit_validation_pleasant_habit_reward(self):
        """Тест валидации: у приятной привычки не может быть вознаграждения"""
        habit = Habit(
            user=self.user,
            place='Дома',
            time=time(9, 0),
            action='Приятная привычка',
            is_pleasant=True,
            reward='Шоколад',
            estimated_time=60
        )
        
        with self.assertRaises(ValidationError):
            habit.clean()
    
    def test_habit_validation_periodicity(self):
        """Тест валидации: нельзя выполнять привычку реже, чем 1 раз в 7 дней"""
        habit = Habit(
            user=self.user,
            place='Дома',
            time=time(9, 0),
            action='Действие',
            periodicity=10,
            estimated_time=60
        )
        
        with self.assertRaises(ValidationError):
            habit.clean()


class HabitAPITest(APITestCase):
    """Тесты для API привычек"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        self.pleasant_habit = Habit.objects.create(
            user=self.user,
            place='Дома',
            time=time(9, 0),
            action='Приятная привычка',
            is_pleasant=True,
            estimated_time=60
        )
    
    def test_create_habit(self):
        """Тест создания привычки через API"""
        data = {
            'place': 'Парк',
            'time': '10:00:00',
            'action': 'Пробежка',
            'estimated_time': 60,
            'periodicity': 1
        }
        
        response = self.client.post('/api/v1/habits/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 2)
    
    def test_get_my_habits(self):
        """Тест получения привычек пользователя"""
        response = self.client.get('/api/v1/habits/my_habits/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_get_public_habits(self):
        """Тест получения публичных привычек"""
        # Создаем публичную привычку
        Habit.objects.create(
            user=self.user,
            place='Спортзал',
            time=time(18, 0),
            action='Тренировка',
            is_public=True,
            estimated_time=60
        )
        
        response = self.client.get('/api/v1/habits/public_habits/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_complete_habit(self):
        """Тест отметки привычки как выполненной"""
        response = self.client.post(f'/api/v1/habits/{self.pleasant_habit.id}/complete/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(HabitLog.objects.filter(habit=self.pleasant_habit).exists())
    
    def test_habit_logs(self):
        """Тест получения логов привычки"""
        # Создаем лог
        HabitLog.objects.create(habit=self.pleasant_habit, is_completed=True)
        
        response = self.client.get(f'/api/v1/habits/{self.pleasant_habit.id}/logs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_unauthorized_access(self):
        """Тест доступа без авторизации"""
        self.client.credentials()  # Убираем токен
        response = self.client.get('/api/v1/habits/my_habits/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserAPITest(APITestCase):
    """Тесты для API пользователей"""
    
    def test_user_registration(self):
        """Тест регистрации пользователя"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123'
        }
        
        response = self.client.post('/api/v1/users/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())


class HabitLogModelTest(TestCase):
    """Тесты для модели HabitLog"""
    
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
            estimated_time=60
        )
    
    def test_create_habit_log(self):
        """Тест создания лога привычки"""
        log = HabitLog.objects.create(
            habit=self.habit,
            is_completed=True
        )
        self.assertEqual(log.habit, self.habit)
        self.assertTrue(log.is_completed)
        self.assertIsNotNone(log.completed_at)