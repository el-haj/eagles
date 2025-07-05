from django.urls import path
from . import views

urlpatterns = [
    path('', views.LabListView.as_view(), name='lab-list'),
    path('<int:pk>/', views.LabDetailView.as_view(), name='lab-detail'),
    path('user-labs/', views.UserLabListView.as_view(), name='user-lab-list'),
    path('user-labs/create/', views.UserLabCreateView.as_view(), name='user-lab-create'),
]
