from django.contrib import admin
from .models import UserProfile, PriceAlert, NotificationLog


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['user__username', 'user__email']


@admin.register(PriceAlert)
class PriceAlertAdmin(admin.ModelAdmin):
    list_display = ['user', 'origin', 'destination', 'threshold_price', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'origin', 'destination']
    search_fields = ['user__username', 'origin', 'destination']


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ['alert', 'triggered_price', 'notified_at']
    list_filter = ['notified_at']
    search_fields = ['alert__user__username', 'message']
    readonly_fields = ['notified_at']
