from django.contrib import admin
from .models import MessageLog


@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'contact', 'direction', 'message_type', 'status', 'wam_id', 'created_at')
    list_filter = ('direction', 'message_type', 'status', 'created_at')
    search_fields = ('contact__name', 'contact__phone', 'wam_id')
    readonly_fields = ('created_at',)