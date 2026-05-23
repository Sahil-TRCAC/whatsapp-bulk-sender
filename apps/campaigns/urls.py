from django.urls import path
from . import views

urlpatterns = [
    path('', views.campaign_list, name='campaign_list'),
    path('create/', views.campaign_create, name='campaign_create'),
    path('<int:pk>/', views.campaign_detail, name='campaign_detail'),
    path('<int:pk>/edit/', views.campaign_edit, name='campaign_edit'),
    path('<int:pk>/delete/', views.campaign_delete, name='campaign_delete'),
    path('<int:pk>/send/', views.campaign_send, name='campaign_send'),
    path('<int:pk>/progress/', views.campaign_progress, name='campaign_progress'),
]