from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'contacts', api_views.ContactViewSet, basename='api-contacts')
router.register(r'groups', api_views.ContactGroupViewSet, basename='api-groups')
router.register(r'campaigns', api_views.CampaignViewSet, basename='api-campaigns')
router.register(r'templates', api_views.TemplateViewSet, basename='api-templates')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', api_views.CampaignViewSet.as_view({'get': 'stats'}), name='api-dashboard-stats'),
]