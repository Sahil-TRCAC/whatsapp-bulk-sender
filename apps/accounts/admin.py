from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number_id', 'waba_id', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__email', 'phone_number_id', 'waba_id')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('WhatsApp Configuration', {'fields': ('phone_number_id', 'waba_id', 'access_token_encrypted', 'webhook_verify_token')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )