from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/analytics/dashboard/', permanent=False)),
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls')),
    path('', include('apps.contacts.urls')),
    path('campaigns/', include('apps.campaigns.urls')),
    path('webhooks/', include('apps.webhooks.urls')),
    path('analytics/', include('apps.analytics.urls')),
    path('templates/', include('apps.templates_mgr.urls')),
    path('api/', include('apps.analytics.api_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)