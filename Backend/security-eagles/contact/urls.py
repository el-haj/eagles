from django.urls import path
from . import views

app_name = 'contact'

urlpatterns = [
    # Public APIs (No authentication required)
    path('message/', views.ContactMessageCreateView.as_view(), name='create_message'),
    path('settings/', views.ContactSettingsView.as_view(), name='contact_settings'),
    path('subjects/', views.ContactSubjectChoicesView.as_view(), name='subject_choices'),
    
    # Admin APIs (Authentication required)
    path('admin/messages/', views.ContactMessageListView.as_view(), name='admin_messages_list'),
    path('admin/messages/<int:pk>/', views.ContactMessageDetailView.as_view(), name='admin_message_detail'),
    path('admin/settings/', views.ContactSettingsAdminView.as_view(), name='admin_settings'),
    path('admin/stats/', views.ContactStatsView.as_view(), name='admin_stats'),
]
