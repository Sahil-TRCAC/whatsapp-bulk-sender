from rest_framework import serializers
from apps.campaigns.models import Campaign, CampaignRecipient
from apps.contacts.models import Contact, ContactGroup
from apps.templates_mgr.models import WhatsAppTemplate


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'


class ContactGroupSerializer(serializers.ModelSerializer):
    contact_count = serializers.IntegerField()
    
    class Meta:
        model = ContactGroup
        fields = '__all__'


class CampaignRecipientSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source='contact.name')
    contact_phone = serializers.CharField(source='contact.phone')
    
    class Meta:
        model = CampaignRecipient
        fields = ('id', 'contact_name', 'contact_phone', 'status', 'sent_at', 'delivered_at', 'read_at', 'error_message')


class CampaignSerializer(serializers.ModelSerializer):
    recipients_detail = CampaignRecipientSerializer(source='recipients', many=True, read_only=True)
    contact_group_names = serializers.SerializerMethodField()
    
    class Meta:
        model = Campaign
        fields = '__all__'
    
    def get_contact_group_names(self, obj):
        return list(obj.contact_groups.values_list('name', flat=True))


class WhatsAppTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsAppTemplate
        fields = '__all__'