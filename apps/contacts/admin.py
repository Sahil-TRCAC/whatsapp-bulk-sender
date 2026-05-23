from django.contrib import admin
from .models import Contact, ContactGroup


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'user', 'created_at')
    list_filter = ('created_at', 'tags')
    search_fields = ('name', 'phone', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('groups',)


@admin.register(ContactGroup)
class ContactGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'contact_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'user__email')
    readonly_fields = ('created_at', 'updated_at')