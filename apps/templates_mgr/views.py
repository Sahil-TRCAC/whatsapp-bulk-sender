from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import WhatsAppTemplate
from apps.messaging.services import WhatsAppAPIClient
from apps.accounts.models import UserProfile


@login_required
def template_list(request):
    templates = WhatsAppTemplate.objects.filter(user=request.user)
    status_filter = request.GET.get('status', '')
    if status_filter:
        templates = templates.filter(status=status_filter)
    
    paginator = Paginator(templates, 20)
    page = request.GET.get('page', 1)
    templates_page = paginator.get_page(page)
    
    return render(request, 'templates/list.html', {
        'templates': templates_page,
        'status_filter': status_filter,
    })


@login_required
def template_sync(request):
    profile = UserProfile.objects.get(user=request.user)
    
    if not profile.has_whatsapp_config():
        messages.error(request, 'Please configure WhatsApp credentials first')
        return redirect('settings')
    
    try:
        client = WhatsAppAPIClient(
            phone_number_id=profile.phone_number_id,
            access_token=profile.get_access_token()
        )
        result = client.get_templates()
        templates_data = result.get('data', [])
        
        count = 0
        for t in templates_data:
            WhatsAppTemplate.objects.update_or_create(
                user=request.user,
                meta_template_id=t.get('id'),
                defaults={
                    'template_name': t.get('name'),
                    'language': t.get('language'),
                    'category': t.get('category'),
                    'status': t.get('status'),
                    'components': t.get('components', [])
                }
            )
            count += 1
        
        messages.success(request, f'Synced {count} templates from WhatsApp')
    except Exception as e:
        messages.error(request, f'Error syncing templates: {str(e)}')
    
    return redirect('template_list')


@login_required
def template_create(request):
    if request.method == 'POST':
        template_name = request.POST.get('template_name')
        language = request.POST.get('language', 'en_US')
        category = request.POST.get('category', 'MARKETING')
        header_text = request.POST.get('header_text', '')
        body_text = request.POST.get('body_text', '')
        footer_text = request.POST.get('footer_text', '')
        
        components = []
        
        if header_text:
            components.append({
                'type': 'header',
                'parameters': [{'type': 'text', 'text': header_text}]
            })
        
        if body_text:
            components.append({
                'type': 'body',
                'parameters': [{'type': 'text', 'text': body_text}]
            })
        
        if footer_text:
            components.append({
                'type': 'footer',
                'parameters': [{'type': 'text', 'text': footer_text}]
            })
        
        WhatsAppTemplate.objects.create(
            user=request.user,
            template_name=template_name,
            language=language,
            category=category,
            components=components,
            status='PENDING'
        )
        
        messages.success(request, f'Template "{template_name}" created! Note: This is a local template. Submit to Meta for approval.')
        return redirect('template_list')
    
    return render(request, 'templates/create.html')


@login_required
def template_detail(request, pk):
    template = get_object_or_404(WhatsAppTemplate, pk=pk, user=request.user)
    return render(request, 'templates/detail.html', {'template': template})


@login_required
def template_delete(request, pk):
    template = get_object_or_404(WhatsAppTemplate, pk=pk, user=request.user)
    template.delete()
    messages.success(request, 'Template deleted successfully!')
    return redirect('template_list')