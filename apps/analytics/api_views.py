from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta

from .serializers import (
    ContactSerializer, ContactGroupSerializer,
    CampaignSerializer, CampaignRecipientSerializer,
    WhatsAppTemplateSerializer
)
from apps.contacts.models import Contact, ContactGroup
from apps.campaigns.models import Campaign, CampaignRecipient
from apps.templates_mgr.models import WhatsAppTemplate


class ContactViewSet(viewsets.ModelViewSet):
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Contact.objects.filter(user=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def import_csv(self, request):
        from apps.contacts.views import contact_import
        return Response({'message': 'Use /contacts/import/ endpoint'})
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.GET.get('q', '')
        contacts = self.get_queryset().filter(
            Q(name__icontains=query) | Q(phone__icontains=query)
        )[:20]
        serializer = self.get_serializer(contacts, many=True)
        return Response(serializer.data)


class ContactGroupViewSet(viewsets.ModelViewSet):
    serializer_class = ContactGroupSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ContactGroup.objects.filter(user=self.request.user).annotate(
            contact_count=Count('contacts')
        ).order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CampaignViewSet(viewsets.ModelViewSet):
    serializer_class = CampaignSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Campaign.objects.filter(user=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        campaign = self.get_object()
        if campaign.status not in ['draft', 'failed']:
            return Response(
                {'error': 'Campaign already sent'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from apps.campaigns.tasks import process_campaign
        campaign.status = 'queued'
        campaign.save()
        process_campaign.delay(campaign.id)
        
        return Response({'message': 'Campaign queued for sending'})
    
    @action(detail=True, methods=['get'])
    def recipients(self, request, pk=None):
        campaign = self.get_object()
        recipients = campaign.recipients.all()
        page = self.paginate_queryset(recipients)
        if page is not None:
            serializer = CampaignRecipientSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CampaignRecipientSerializer(recipients, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        user = request.user
        total = Campaign.objects.filter(user=user).count()
        completed = Campaign.objects.filter(user=user, status='completed').count()
        sending = Campaign.objects.filter(user=user, status='sending').count()
        
        return Response({
            'total': total,
            'completed': completed,
            'sending': sending,
            'draft': total - completed - sending
        })


class TemplateViewSet(viewsets.ModelViewSet):
    serializer_class = WhatsAppTemplateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return WhatsAppTemplate.objects.filter(user=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def sync(self, request):
        from apps.messaging.services import WhatsAppAPIClient
        from apps.accounts.models import UserProfile
        
        profile = UserProfile.objects.get(user=request.user)
        if not profile.has_whatsapp_config():
            return Response(
                {'error': 'WhatsApp not configured'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        client = WhatsAppAPIClient(
            phone_number_id=profile.phone_number_id,
            access_token=profile.get_access_token()
        )
        
        try:
            result = client.get_templates()
            templates = result.get('data', [])
            
            for t in templates:
                WhatsAppTemplate.objects.update_or_create(
                    user=request.user,
                    meta_template_id=t.get('id'),
                    defaults={
                        'template_name': t.get('name'),
                        'language': t.get('language'),
                        'category': t.get('category'),
                        'status': t.get('status'),
                        'components': t.get('components')
                    }
                )
            
            return Response({'message': f'Synced {len(templates)} templates'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )