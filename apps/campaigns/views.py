from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Campaign, CampaignRecipient
from .forms import CampaignForm
from .tasks import process_campaign
from apps.contacts.models import ContactGroup


@login_required
def campaign_list(request):
    campaigns = Campaign.objects.filter(user=request.user)
    status_filter = request.GET.get('status', '')
    if status_filter:
        campaigns = campaigns.filter(status=status_filter)
    
    paginator = Paginator(campaigns, 10)
    page = request.GET.get('page', 1)
    campaigns_page = paginator.get_page(page)
    
    return render(request, 'campaigns/list.html', {
        'campaigns': campaigns_page,
        'status_filter': status_filter,
    })


@login_required
def campaign_create(request):
    if request.method == 'POST':
        form = CampaignForm(request.POST, user=request.user)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.user = request.user
            campaign.save()
            form.save_m2m()
            messages.success(request, 'Campaign created successfully!')
            return redirect('campaign_list')
    else:
        form = CampaignForm(user=request.user)
    groups = ContactGroup.objects.filter(user=request.user)
    return render(request, 'campaigns/form.html', {'form': form, 'groups': groups})


@login_required
def campaign_edit(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk, user=request.user)
    if campaign.status not in ['draft', 'failed']:
        messages.error(request, 'Cannot edit campaign in progress')
        return redirect('campaign_list')
    
    if request.method == 'POST':
        form = CampaignForm(request.POST, instance=campaign, user=request.user)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.save()
            form.save_m2m()
            messages.success(request, 'Campaign updated successfully!')
            return redirect('campaign_list')
    else:
        form = CampaignForm(instance=campaign, user=request.user)
    groups = ContactGroup.objects.filter(user=request.user)
    return render(request, 'campaigns/form.html', {'form': form, 'groups': groups, 'campaign': campaign})


@login_required
def campaign_detail(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk, user=request.user)
    recipients = campaign.recipients.all()
    paginator = Paginator(recipients, 25)
    page = request.GET.get('page', 1)
    recipients_page = paginator.get_page(page)
    
    return render(request, 'campaigns/detail.html', {
        'campaign': campaign,
        'recipients': recipients_page,
    })


@require_POST
@login_required
def campaign_delete(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk, user=request.user)
    if campaign.status in ['sending']:
        messages.error(request, 'Cannot delete campaign in progress')
        return redirect('campaign_list')
    campaign.delete()
    messages.success(request, 'Campaign deleted successfully!')
    return redirect('campaign_list')


@require_POST
@login_required
def campaign_send(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk, user=request.user)
    
    if campaign.status not in ['draft', 'failed']:
        messages.error(request, 'Campaign already sent')
        return redirect('campaign_detail', pk=pk)
    
    if not campaign.contact_groups.exists():
        messages.error(request, 'Please select at least one contact group')
        return redirect('campaign_detail', pk=pk)
    
    if campaign.message_type == 'template' and not campaign.template_name:
        messages.error(request, 'Template name is required for template messages')
        return redirect('campaign_detail', pk=pk)
    
    campaign.status = 'queued'
    campaign.save()
    
    recipient_count = 0
    for group in campaign.contact_groups.all():
        for contact in group.contacts.all():
            CampaignRecipient.objects.get_or_create(
                campaign=campaign,
                contact=contact,
                defaults={'status': 'pending'}
            )
            recipient_count += 1
    
    campaign.total_recipients = recipient_count
    campaign.save()
    
    if campaign.schedule_time and campaign.schedule_time > timezone.now():
        campaign.status = 'queued'
        campaign.save()
    else:
        process_campaign(campaign.id)
    
    messages.success(request, f'Campaign queued for sending to {recipient_count} recipients!')
    return redirect('campaign_detail', pk=pk)


@login_required
def campaign_progress(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk, user=request.user)
    return JsonResponse({
        'status': campaign.status,
        'total': campaign.total_recipients,
        'sent': campaign.sent_count,
        'delivered': campaign.delivered_count,
        'read': campaign.read_count,
        'failed': campaign.failed_count,
        'progress': campaign.progress_percentage,
    })