from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
import base64
from cryptography.fernet import Fernet


def get_fernet_key():
    key = settings.SECRET_KEY[:32].encode()
    return base64.urlsafe_b64encode(key.ljust(32, b'x'))


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number_id = models.CharField(max_length=100, blank=True, null=True)
    waba_id = models.CharField(max_length=100, blank=True, null=True)
    access_token_encrypted = models.TextField(blank=True, null=True)
    webhook_verify_token = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def set_access_token(self, token):
        if hasattr(settings, 'SECRET_KEY'):
            f = Fernet(get_fernet_key())
            self.access_token_encrypted = f.encrypt(token.encode()).decode()
        else:
            self.access_token_encrypted = token

    def get_access_token(self):
        if self.access_token_encrypted and hasattr(settings, 'SECRET_KEY'):
            try:
                f = Fernet(get_fernet_key())
                return f.decrypt(self.access_token_encrypted.encode()).decode()
            except:
                return self.access_token_encrypted
        return self.access_token_encrypted

    def has_whatsapp_config(self):
        return all([self.phone_number_id, self.waba_id, self.access_token_encrypted])

    def __str__(self):
        return f"{self.user.email} - Profile"


def userprofile_receiver(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


from django.db.models.signals import post_save
post_save.connect(userprofile_receiver, sender=User)