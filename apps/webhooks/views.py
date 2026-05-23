import json
import logging
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils import timezone
from apps.messaging.models import MessageLog
from apps.contacts.models import Contact
from apps.campaigns.models import CampaignRecipient

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def webhook(request):
    if request.method == 'GET':
        return verify_webhook(request)
    return handle_webhook(request)


def verify_webhook(request):
    mode = request.GET.get('hub.mode')
    token = request.GET.get('hub.verify_token')
    challenge = request.GET.get('hub.challenge')
    
    verify_token = getattr(settings, 'WHATSAPP_VERIFY_TOKEN', 'whatsapp_verify_token')
    
    if mode == 'subscribe' and token == verify_token:
        logger.info("Webhook verified successfully")
        return HttpResponse(challenge, status=200)
    
    logger.warning(f"Webhook verification failed: mode={mode}, token={token}")
    return JsonResponse({'error': 'Verification failed'}, status=403)


def handle_webhook(request):
    try:
        payload = json.loads(request.body)
        logger.info(f"Webhook received: {json.dumps(payload)[:500]}")
        
        entry = payload.get('entry', [])
        if not entry:
            return JsonResponse({'status': 'ok'})
        
        changes = entry[0].get('changes', [])
        if not changes:
            return JsonResponse({'status': 'ok'})
        
        value = changes[0].get('value', {})
        
        if 'messages' in value:
            handle_incoming_messages(value['messages'])
        
        if 'statuses' in value:
            handle_status_updates(value['statuses'])
        
        return JsonResponse({'status': 'ok'})
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in webhook: {str(e)}")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


def handle_incoming_messages(messages):
    for message in messages:
        from_id = message.get('from')
        msg_id = message.get('id')
        msg_type = message.get('type')
        
        logger.info(f"Incoming message from {from_id}: {msg_type}")
        
        contact, created = Contact.objects.get_or_create(
            phone=from_id,
            defaults={'name': f'Contact {from_id[-4:]}'}
        )
        
        MessageLog.objects.create(
            contact=contact,
            direction='incoming',
            message_type=msg_type,
            wam_id=msg_id,
            raw_data=message
        )


def handle_status_updates(statuses):
    for status in statuses:
        wam_id = status.get('id')
        wam_status = status.get('status')
        recipient_phone = status.get('recipient_id')
        
        logger.info(f"Status update: {wam_id} -> {wam_status}")
        
        status_map = {
            'sent': 'sent',
            'delivered': 'delivered',
            'read': 'read',
            'failed': 'failed'
        }
        
        db_status = status_map.get(wam_status)
        
        if db_status:
            recipients = CampaignRecipient.objects.filter(wam_id=wam_id)
            for recipient in recipients:
                old_status = recipient.status
                recipient.status = db_status
                
                if db_status == 'delivered':
                    recipient.delivered_at = timezone.now()
                elif db_status == 'read':
                    recipient.read_at = timezone.now()
                
                recipient.save()
                
                campaign = recipient.campaign
                if db_status == 'delivered':
                    campaign.delivered_count += 1
                elif db_status == 'read':
                    campaign.read_count += 1
                elif db_status == 'failed':
                    campaign.failed_count += 1
                
                if campaign.status == 'sending' and campaign.sent_count >= campaign.total_recipients:
                    campaign.status = 'completed'
                
                campaign.save()
        
        MessageLog.objects.filter(wam_id=wam_id).update(status=wam_status)