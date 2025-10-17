from django.contrib import admin
from .models import Habit, HabitLog


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    """Админка для привычек"""
    
    list_display = [
        'action', 'user', 'place', 'time', 'is_pleasant', 
        'is_public', 'periodicity', 'created_at'
    ]
    list_filter = ['is_pleasant', 'is_public', 'created_at', 'user']
    search_fields = ['action', 'place', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'action', 'place', 'time', 'estimated_time')
        }),
        ('Настройки', {
            'fields': ('is_pleasant', 'is_public', 'periodicity')
        }),
        ('Вознаграждение', {
            'fields': ('reward', 'related_habit')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(HabitLog)
class HabitLogAdmin(admin.ModelAdmin):
    """Админка для логов привычек"""
    
    list_display = ['habit', 'completed_at', 'is_completed']
    list_filter = ['is_completed', 'completed_at', 'habit__user']
    search_fields = ['habit__action', 'habit__user__username']
    readonly_fields = ['completed_at']