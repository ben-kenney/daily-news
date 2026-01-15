"""URLs for the news app."""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add-term/', views.add_search_term, name='add_search_term'),
    path('delete-term/<int:pk>/', views.delete_search_term, name='delete_search_term'),
    path('digest/<int:pk>/', views.digest_detail, name='digest_detail'),
    path('profile/', views.profile, name='profile'),
]