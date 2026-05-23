import httpx
import logging
import json
from django.conf import settings

logger = logging.getLogger(__name__)


class WhatsAppAPIException(Exception):
    def __init__(self, message, code=None, error_data=None):
        self.message = message
        self.code = code
        self.error_data = error_data
        super().__init__(self.message)


class WhatsAppAPIClient:
    BASE_URL = f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}"
    
    def __init__(self, phone_number_id, access_token):
        self.phone_number_id = phone_number_id
        self.access_token = access_token
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }
    
    def _make_request(self, method, endpoint, data=None, params=None):
        url = f"{self.BASE_URL}/{self.phone_number_id}/{endpoint}"
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=data,
                    params=params
                )
                
                if response.status_code >= 400:
                    error_data = response.json() if response.content else {}
                    logger.error(f"WhatsApp API error: {response.status_code} - {error_data}")
                    raise WhatsAppAPIException(
                        message=error_data.get('error', {}).get('message', 'API Error'),
                        code=response.status_code,
                        error_data=error_data
                    )
                
                return response.json() if response.content else {}
                
        except httpx.RequestError as e:
            logger.error(f"HTTP request failed: {str(e)}")
            raise WhatsAppAPIException(message=f"Network error: {str(e)}")
    
    def send_text_message(self, to, body):
        payload = {
            'messaging_product': 'whatsapp',
            'to': to,
            'type': 'text',
            'text': {'body': body}
        }
        logger.info(f"Sending text message to {to}")
        return self._make_request('POST', 'messages', data=payload)
    
    def send_template_message(self, to, template_name, language='en_US', components=None):
        payload = {
            'messaging_product': 'whatsapp',
            'to': to,
            'type': 'template',
            'template': {
                'name': template_name,
                'language': {'code': language}
            }
        }
        
        if components:
            payload['template']['components'] = components
        
        logger.info(f"Sending template '{template_name}' to {to}")
        return self._make_request('POST', 'messages', data=payload)
    
    def send_media_message(self, to, media_type, media_url, caption=''):
        media_type_map = {
            'image': 'image',
            'document': 'document',
            'video': 'video',
            'audio': 'audio'
        }
        
        payload = {
            'messaging_product': 'whatsapp',
            'to': to,
            'type': media_type_map.get(media_type, 'image'),
            media_type_map.get(media_type, 'image'): {
                'link': media_url,
                'caption': caption
            }
        }
        
        logger.info(f"Sending {media_type} to {to}")
        return self._make_request('POST', 'messages', data=payload)
    
    def upload_media(self, file_url, media_type='image'):
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{self.BASE_URL}/{self.phone_number_id}/media",
                headers=self.headers,
                json={
                    'messaging_product': 'whatsapp',
                    'type': media_type,
                    'url': file_url
                }
            )
            return response.json()
    
    def get_templates(self):
        return self._make_request('GET', 'message_templates')
    
    def get_media(self, media_id):
        return self._make_request('GET', f'media/{media_id}')
    
    def send_reaction(self, to, message_id, emoji='👍'):
        payload = {
            'messaging_product': 'whatsapp',
            'to': to,
            'type': 'reaction',
            'reaction': {
                'message_id': message_id,
                'emoji': emoji
            }
        }
        return self._make_request('POST', 'messages', data=payload)


class WhatsAppAPI:
    @staticmethod
    def send_message(user, to, message_type, content, template_name=None, template_language='en_US', media_url=None, media_type='image'):
        from apps.accounts.models import UserProfile
        
        profile = UserProfile.objects.get(user=user)
        
        if not profile.has_whatsapp_config():
            raise WhatsAppAPIException("WhatsApp not configured")
        
        client = WhatsAppAPIClient(
            phone_number_id=profile.phone_number_id,
            access_token=profile.get_access_token()
        )
        
        if message_type == 'text':
            return client.send_text_message(to, content)
        elif message_type == 'template':
            return client.send_template_message(to, template_name, template_language, content)
        elif message_type == 'media':
            return client.send_media_message(to, media_type, media_url, content)
        
        raise WhatsAppAPIException("Invalid message type")