from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Пользователь может редактировать только свои привычки.
    Публичные привычки доступны только для чтения.
    """

    def has_object_permission(self, request, view, obj):
        # Права на чтение для всех аутентифицированных пользователей
        if request.method in permissions.SAFE_METHODS:
            return True

        # Права на запись только для владельца
        return obj.user == request.user
