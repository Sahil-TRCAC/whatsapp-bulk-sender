from django.db import models
from django.conf import settings
import re


def validate_phone(phone):
    cleaned = re.sub(r'\D', '', phone)
    if not cleaned.startswith('+'):
        cleaned = '+' + cleaned
    if len(cleaned) < 10:
        raise ValueError("Invalid phone number")
    return cleaned


class ContactGroup(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contact_groups')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Contact Group'
        verbose_name_plural = 'Contact Groups'
        unique_together = ('user', 'name')

    def __str__(self):
        return self.name

    @property
    def contact_count(self):
        return self.contacts.count()


class Contact(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    groups = models.ManyToManyField(ContactGroup, related_name='contacts', blank=True)
    tags = models.CharField(max_length=200, blank=True, help_text="Comma separated tags")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
        unique_together = ('user', 'phone')
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.name} ({self.phone})"

    def get_normalized_phone(self):
        cleaned = re.sub(r'\D', '', self.phone)
        if not cleaned.startswith('+'):
            cleaned = '+' + cleaned
        return cleaned

    def save(self, *args, **kwargs):
        self.phone = self.get_normalized_phone()
        super().save(*args, **kwargs)