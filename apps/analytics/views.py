from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
import csv
from apps.campaigns.models import Campaign, CampaignRecipient
from apps.contacts.models import Contact, ContactGroup


@login_required
def dashboard(request):
    user = request.user
    
    total_contacts = Contact.objects.filter(user=user).count()
    total_groups = ContactGroup.objects.filter(user=user).count()
    total_campaigns = Campaign.objects.filter(user=user).count()
    
    recipient_stats = CampaignRecipient.objects.filter(campaign__user=user).aggregate(
        total_sent=Count('id', filter=Q(status__in=['sent', 'delivered', 'read'])),
        total_delivered=Count('id', filter=Q(status='delivered')),
        total_read=Count('id', filter=Q(status='read')),
        total_failed=Count('id', filter=Q(status='failed'))
    )
    
    total_sent = recipient_stats['total_sent'] or 0
    total_delivered = recipient_stats['total_delivered'] or 0
    total_read = recipient_stats['total_read'] or 0
    total_failed = recipient_stats['total_failed'] or 0
    
    delivery_rate = round((total_delivered / total_sent * 100), 1) if total_sent > 0 else 0
    read_rate = round((total_read / total_delivered * 100), 1) if total_delivered > 0 else 0
    
    recent_campaigns = Campaign.objects.filter(user=user).order_by('-created_at')[:5]
    
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    
    daily_stats = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_start = timezone.make_aware(timezone.datetime.combine(day, timezone.datetime.min.time()))
        day_end = timezone.make_aware(timezone.datetime.combine(day + timedelta(days=1), timezone.datetime.min.time()))
        
        count = CampaignRecipient.objects.filter(
            campaign__user=user,
            sent_at__gte=day_start,
            sent_at__lt=day_end
        ).count()
        
        daily_stats.append({
            'date': day.strftime('%Y-%m-%d'),
            'label': day.strftime('%b %d'),
            'count': count
        })
    
    campaign_perf = Campaign.objects.filter(
        user=user,
        status='completed'
    ).annotate(
        recipient_count=Count('recipients')
    ).values('name', 'sent_count', 'delivered_count', 'read_count')[:10]
    
    return render(request, 'dashboard/index.html', {
        'total_contacts': total_contacts,
        'total_groups': total_groups,
        'total_campaigns': total_campaigns,
        'total_sent': total_sent,
        'total_delivered': total_delivered,
        'total_read': total_read,
        'total_failed': total_failed,
        'delivery_rate': delivery_rate,
        'read_rate': read_rate,
        'recent_campaigns': recent_campaigns,
        'daily_stats': daily_stats,
        'campaign_perf': list(campaign_perf),
    })


@login_required
def export_campaign_report(request, campaign_id):
    campaign = Campaign.objects.get(id=campaign_id, user=request.user)
    recipients = campaign.recipients.select_related('contact')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{campaign.name}_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Contact Name', 'Phone', 'Status', 'Sent At', 'Delivered At', 'Read At', 'Error'])
    
    for r in recipients:
        writer.writerow([
            r.contact.name,
            r.contact.phone,
            r.status,
            r.sent_at.strftime('%Y-%m-%d %H:%M') if r.sent_at else '',
            r.delivered_at.strftime('%Y-%m-%d %H:%M') if r.delivered_at else '',
            r.read_at.strftime('%Y-%m-%d %H:%M') if r.read_at else '',
            r.error_message or ''
        ])
    
    return response