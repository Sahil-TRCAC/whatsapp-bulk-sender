from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import UserProfile


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = user.email
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class WhatsAppConfigForm(forms.ModelForm):
    access_token = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'WhatsApp Access Token'}), required=False)
    
    class Meta:
        model = UserProfile
        fields = ('phone_number_id', 'waba_id', 'access_token', 'webhook_verify_token')
        widgets = {
            'phone_number_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number ID'}),
            'waba_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'WhatsApp Business Account ID'}),
            'webhook_verify_token': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Webhook Verify Token'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.access_token_encrypted:
            self.initial['access_token'] = '********'

    def save(self, commit=True):
        profile = super().save(commit=False)
        token = self.cleaned_data.get('access_token')
        if token and token != '********':
            profile.set_access_token(token)
        if commit:
            profile.save()
        return profile