from django.db import models
from django.conf import settings


class WhatsAppTemplate(models.Model):
    CATEGORY_CHOICES = [
        ('MARKETING', 'Marketing'),
        ('UTILITY', 'Utility'),
        ('AUTHENTICATION', 'Authentication'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='whatsapp_templates')
    template_name = models.CharField(max_length=100)
    language = models.CharField(max_length=20, default='en_US')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='MARKETING')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    components = models.JSONField(default=list, blank=True)
    meta_template_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'WhatsApp Template'
        verbose_name_plural = 'WhatsApp Templates'
        unique_together = ('user', 'template_name', 'language')
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.template_name} ({self.language}) - {self.status}"