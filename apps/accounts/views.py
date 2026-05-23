from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView
from .forms import UserRegistrationForm, UserLoginForm, WhatsAppConfigForm
from .models import UserProfile
from django.contrib.auth.views import LoginView as BaseLoginView


class RegisterView(TemplateView):
    template_name = 'auth/register.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = UserRegistrationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
        return render(request, self.template_name, {'form': form})


class LoginView(BaseLoginView):
    template_name = 'auth/login.html'
    authentication_form = UserLoginForm

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        return redirect('dashboard')


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def settings_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = WhatsAppConfigForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'WhatsApp configuration saved successfully!')
            return redirect('settings')
    else:
        form = WhatsAppConfigForm(instance=profile)
    
    webhook_url = f"{request.scheme}://{request.get_host()}/webhooks/"
    return render(request, 'auth/settings.html', {
        'form': form,
        'webhook_url': webhook_url,
        'profile': profile
    })