from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomePage, name="home"),
    path('addrule/',             views.AddRule,    name="addrule"),
    path('updaterule/<str:pk>/', views.UpdateRule, name="updaterule"),
    path('removerule/<str:pk>/',  views.RemoveRule,  name="removerule")
]
