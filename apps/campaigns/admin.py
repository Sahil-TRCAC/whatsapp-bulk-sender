from django.contrib import admin
from .models import Campaign, CampaignRecipient


class CampaignRecipientInline(admin.TabularInline):
    model = CampaignRecipient
    extra = 0
    readonly_fields = ('contact', 'status', 'wam_id', 'sent_at', 'delivered_at', 'read_at')
    can_delete = False


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'message_type', 'status', 'total_recipients', 'sent_count', 'delivered_count', 'created_at')
    list_filter = ('status', 'message_type', 'created_at')
    search_fields = ('name', 'user__email')
    readonly_fields = ('created_at', 'updated_at', 'sent_count', 'delivered_count', 'read_count', 'failed_count')
    filter_horizontal = ('contact_groups',)
    inlines = [CampaignRecipientInline]


@admin.register(CampaignRecipient)
class CampaignRecipientAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'contact', 'status', 'wam_id', 'sent_at', 'delivered_at')
    list_filter = ('status', 'created_at')
    search_fields = ('campaign__name', 'contact__name', 'contact__phone')
    readonly_fields = ('created_at',)