from django.db import models
from django.conf import settings


class MessageLog(models.Model):
    DIRECTION_CHOICES = [
        ('outgoing', 'Outgoing'),
        ('incoming', 'Incoming'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='message_logs', null=True, blank=True)
    campaign = models.ForeignKey('campaigns.Campaign', on_delete=models.SET_NULL, related_name='logs', null=True, blank=True)
    contact = models.ForeignKey('contacts.Contact', on_delete=models.CASCADE, related_name='message_logs')
    direction = models.CharField(max_length=20, choices=DIRECTION_CHOICES)
    message_type = models.CharField(max_length=20, default='text')
    wam_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True)
    raw_data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Message Log'
        verbose_name_plural = 'Message Logs'
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.direction} - {self.contact.name} - {self.created_at}"