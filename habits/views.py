from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import User, Habit, HabitLog
from .serializers import (
    HabitSerializer,
    HabitCreateSerializer,
    HabitLogSerializer,
    UserSerializer
)
from .permissions import IsOwnerOrReadOnly


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Кастомный сериализатор для JWT токенов"""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Добавляем кастомные поля в токен
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        
        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    """Кастомное представление для получения JWT токенов"""
    serializer_class = CustomTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    """Представление для пользователей"""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        """Регистрация пользователя"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(
                email=serializer.validated_data['email'],
                password=request.data.get('password'),
                first_name=serializer.validated_data.get('first_name', ''),
                last_name=serializer.validated_data.get('last_name', ''),
                telegram_chat_id=serializer.validated_data.get('telegram_chat_id'),
                telegram_username=serializer.validated_data.get('telegram_username')
            )
            return Response(
                {'message': 'Пользователь успешно зарегистрирован'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HabitViewSet(viewsets.ModelViewSet):
    """Представление для привычек"""
    
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['is_pleasant', 'is_public']
    ordering_fields = ['created_at', 'time']
    ordering = ['-created_at']

    def get_queryset(self):
        """Получение queryset в зависимости от действия"""
        if self.action == 'public_habits':
            return Habit.objects.filter(is_public=True)
        return Habit.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия"""
        if self.action in ['create', 'update', 'partial_update']:
            return HabitCreateSerializer
        return HabitSerializer

    def perform_create(self, serializer):
        """Создание привычки с привязкой к пользователю"""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_habits(self, request):
        """Получение привычек текущего пользователя"""
        habits = self.get_queryset()
        page = self.paginate_queryset(habits)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(habits, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def public_habits(self, request):
        """Получение публичных привычек"""
        habits = Habit.objects.filter(is_public=True)
        page = self.paginate_queryset(habits)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(habits, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def complete(self, request, pk=None):
        """Отметить привычку как выполненную"""
        habit = self.get_object()
        HabitLog.objects.create(habit=habit, is_completed=True)
        return Response({'message': 'Привычка отмечена как выполненная'})

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def logs(self, request, pk=None):
        """Получить логи выполнения привычки"""
        habit = self.get_object()
        logs = habit.logs.all()
        serializer = HabitLogSerializer(logs, many=True)
        return Response(serializer.data)