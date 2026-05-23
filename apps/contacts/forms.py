from django import forms
from .models import Contact, ContactGroup


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('name', 'phone', 'tags')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1234567890'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'tag1, tag2'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        import re
        cleaned = re.sub(r'\D', '', phone)
        if not cleaned.startswith('+'):
            cleaned = '+' + cleaned
        if len(cleaned) < 10:
            raise forms.ValidationError("Invalid phone number format")
        return cleaned


class ContactGroupForm(forms.ModelForm):
    class Meta:
        model = ContactGroup
        fields = ('name', 'description')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Group Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description', 'rows': 3}),
        }


class ContactImportForm(forms.Form):
    file = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv,.xlsx,.xls'}),
        help_text="Upload CSV or Excel file with columns: name, phone"
    )