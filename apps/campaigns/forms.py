from django import forms
from .models import Campaign
from apps.contacts.models import ContactGroup


class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ('name', 'description', 'message_type', 'message_body', 'template_name', 'template_language', 'media_url', 'media_type', 'schedule_time', 'contact_groups')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Campaign Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description', 'rows': 2}),
            'message_body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Message body', 'rows': 5}),
            'template_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Template Name'}),
            'template_language': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'en_US'}),
            'media_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'schedule_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['contact_groups'].queryset = ContactGroup.objects.filter(user=user)

    contact_groups = forms.ModelMultipleChoiceField(
        queryset=ContactGroup.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )


class CampaignSendForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ('contact_groups',)
        widgets = {
            'contact_groups': forms.CheckboxSelectMultiple(),
        }