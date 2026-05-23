from django.urls import path
from . import views

urlpatterns = [
    path('', views.template_list, name='template_list'),
    path('create/', views.template_create, name='template_create'),
    path('sync/', views.template_sync, name='template_sync'),
    path('<int:pk>/', views.template_detail, name='template_detail'),
    path('<int:pk>/delete/', views.template_delete, name='template_delete'),
]