from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('',                       views.home,                  name="home"), 
    path('rule/',                  views.rule,                  name="rule"),
    path('rule/<str:pk>/',         views.rule_handler,          name="rule_handler"),
    path('check_rule_uniqueness/', views.check_rule_uniqueness)
]
