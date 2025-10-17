from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HabitViewSet, UserViewSet

router = DefaultRouter()
router.register(r'habits', HabitViewSet, basename='habit')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]
