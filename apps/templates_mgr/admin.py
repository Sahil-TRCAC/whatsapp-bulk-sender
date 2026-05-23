from django.contrib import admin
from .models import WhatsAppTemplate


@admin.register(WhatsAppTemplate)
class WhatsAppTemplateAdmin(admin.ModelAdmin):
    list_display = ('template_name', 'language', 'category', 'status', 'meta_template_id', 'created_at')
    list_filter = ('status', 'category', 'language', 'created_at')
    search_fields = ('template_name', 'meta_template_id')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)