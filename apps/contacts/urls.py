from django.urls import path
from . import views

urlpatterns = [
    path('contacts/', views.contact_list, name='contact_list'),
    path('contacts/create/', views.contact_create, name='contact_create'),
    path('contacts/edit/<int:pk>/', views.contact_edit, name='contact_edit'),
    path('contacts/delete/<int:pk>/', views.contact_delete, name='contact_delete'),
    path('contacts/import/', views.contact_import, name='contact_import'),
    path('groups/', views.group_list, name='group_list'),
    path('groups/create/', views.group_create, name='group_create'),
    path('groups/edit/<int:pk>/', views.group_edit, name='group_edit'),
    path('groups/delete/<int:pk>/', views.group_delete, name='group_delete'),
]