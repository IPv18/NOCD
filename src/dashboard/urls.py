from django.contrib import admin
from django.urls import path
from . import views



urlpatterns = [
    path('', views.DashboardPage, name="dashboard"),
    path('widgets/', views.Widgets, name="widgets"),
]
