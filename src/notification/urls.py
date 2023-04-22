from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.notifications, name='notifications'),
    path('create/', views.add_notification, name='add_notification'),
    path('delete/<int:id>/', views.delete_notification, name='delete_notification'),
    path('clear/', views.clear_notifications, name='clear_notifications'),
    path('toggle_read/<int:id>/', views.toggle_read_notification, name='toggle_read_notification'),
]
