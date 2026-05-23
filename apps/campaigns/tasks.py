import time
import logging
from celery import shared_task
from django.utils import timezone
from django.db import transaction

logger = logging.getLogger(__name__)

MESSAGES_PER_SECOND = 80
DELAY_BETWEEN_MESSAGES = 1.0 / MESSAGES_PER_SECOND


@shared_task(bind=True)
def process_campaign(self, campaign_id):
    from .models import Campaign, CampaignRecipient
    from apps.messaging.services import WhatsAppAPIClient
    from apps.accounts.models import UserProfile
    
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        campaign.status = 'sending'
        campaign.save()
        
        profile = UserProfile.objects.get(user=campaign.user)
        if not profile.has_whatsapp_config():
            campaign.status = 'failed'
            campaign.save()
            logger.error(f"Campaign {campaign_id}: WhatsApp not configured")
            return
        
        api_client = WhatsAppAPIClient(
            phone_number_id=profile.phone_number_id,
            access_token=profile.get_access_token()
        )
        
        recipients = campaign.recipients.filter(status='pending')
        
        for recipient in recipients:
            try:
                result = send_message_to_contact(api_client, campaign, recipient.contact)
                
                with transaction.atomic():
                    recipient = CampaignRecipient.objects.select_for_update().get(id=recipient.id)
                    recipient.status = 'sent'
                    recipient.wam_id = result.get('message_id')
                    recipient.sent_at = timezone.now()
                    recipient.save()
                    
                    campaign.sent_count += 1
                    campaign.save()
                    
            except Exception as e:
                logger.error(f"Failed to send to {recipient.contact.phone}: {str(e)}")
                recipient.status = 'failed'
                recipient.error_message = str(e)
                recipient.save()
                campaign.failed_count += 1
                campaign.save()
            
            time.sleep(DELAY_BETWEEN_MESSAGES)
        
        campaign.status = 'completed'
        campaign.save()
        logger.info(f"Campaign {campaign_id} completed")
        
    except Exception as e:
        logger.error(f"Campaign {campaign_id} failed: {str(e)}")
        try:
            campaign = Campaign.objects.get(id=campaign_id)
            campaign.status = 'failed'
            campaign.save()
        except:
            pass
        raise


def send_message_to_contact(api_client, campaign, contact):
    phone = contact.phone
    
    if campaign.message_type == 'text':
        return api_client.send_text_message(phone, campaign.message_body)
    elif campaign.message_type == 'template':
        return api_client.send_template_message(
            phone,
            campaign.template_name,
            campaign.template_language,
            campaign.message_body
        )
    elif campaign.message_type == 'media':
        return api_client.send_media_message(
            phone,
            campaign.media_type,
            campaign.media_url,
            campaign.message_body
        )


@shared_task
def update_message_status(recipient_id, status):
    from .models import CampaignRecipient
    
    try:
        recipient = CampaignRecipient.objects.get(id=recipient_id)
        recipient.status = status
        
        if status == 'delivered':
            recipient.delivered_at = timezone.now()
        elif status == 'read':
            recipient.read_at = timezone.now()
        
        recipient.save()
        
        campaign = recipient.campaign
        if status == 'delivered':
            campaign.delivered_count += 1
        elif status == 'read':
            campaign.read_count += 1
        elif status == 'failed':
            campaign.failed_count += 1
        campaign.save()
        
    except Exception as e:
        logger.error(f"Failed to update status for recipient {recipient_id}: {str(e)}")