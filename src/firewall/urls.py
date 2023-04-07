from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('',                    views.index,        name="home"),
    path('addrule/',            views.AddRule,      name="addrule"),    # TODO - this should be a POST request into index
    path('updaterule/<str:pk>/',views.UpdateRule,   name="updaterule"), # TODO - this should be a PUT request into rule_handler
    path('removerule/<str:pk>/',views.RemoveRule,   name="removerule")  # TODO - this should be a DELETE request into rule_handler
]
