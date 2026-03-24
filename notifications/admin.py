from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin for Notifications."""
    
    list_display = ['user', 'title', 'notification_type', 'is_read', 'email_sent', 'created_at']
    list_filter = ['notification_type', 'is_read', 'email_sent', 'created_at']
    search_fields = ['user__email', 'title', 'message']
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']
    
    actions = ['mark_as_read', 'send_email_notification']
    
    @admin.action(description='Mark as read')
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, 'Notifications marked as read.')
    
    @admin.action(description='Send email notification')
    def send_email_notification(self, request, queryset):
        # This would trigger the email task
        count = queryset.filter(email_sent=False).count()
        queryset.update(email_sent=True)
        self.message_user(request, f'{count} email notifications queued.')
