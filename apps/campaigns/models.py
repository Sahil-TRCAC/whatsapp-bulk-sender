from django.db import models
from django.conf import settings
from apps.contacts.models import Contact, ContactGroup


class Campaign(models.Model):
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text Message'),
        ('template', 'Template Message'),
        ('media', 'Media Message'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('queued', 'Queued'),
        ('sending', 'Sending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='campaigns')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='text')
    message_body = models.TextField(blank=True, help_text="Message text or template components")
    template_name = models.CharField(max_length=100, blank=True)
    template_language = models.CharField(max_length=10, default='en_US')
    media_url = models.URLField(blank=True)
    media_type = models.CharField(max_length=20, blank=True, choices=[('image', 'Image'), ('document', 'Document'), ('video', 'Video')])
    contact_groups = models.ManyToManyField(ContactGroup, related_name='campaigns', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    schedule_time = models.DateTimeField(null=True, blank=True)
    total_recipients = models.IntegerField(default=0)
    sent_count = models.IntegerField(default=0)
    delivered_count = models.IntegerField(default=0)
    read_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Campaign'
        verbose_name_plural = 'Campaigns'
        ordering = ('-created_at',)

    def __str__(self):
        return self.name

    @property
    def progress_percentage(self):
        if self.total_recipients == 0:
            return 0
        return int((self.sent_count / self.total_recipients) * 100)


class CampaignRecipient(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    ]

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='recipients')
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='recipients')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    wam_id = models.CharField(max_length=100, blank=True, null=True)
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Campaign Recipient'
        verbose_name_plural = 'Campaign Recipients'
        unique_together = ('campaign', 'contact')
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.campaign.name} - {self.contact.name} - {self.status}"