from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('export/<int:campaign_id>/', views.export_campaign_report, name='export_campaign_report'),
]