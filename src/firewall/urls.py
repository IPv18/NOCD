from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('',                    views.index,        name="home"),
    path('addrule/',            views.AddRule,      name="addrule"),    # TODO - this should be a POST request into index
    path('updaterule/<str:pk>/',views.UpdateRule,   name="updaterule"), # TODO - this should be a PUT request into rule_handler
    path('removerule/<str:pk>/',views.RemoveRule,   name="removerule"), # TODO - this should be a DELETE request into rule_handler
    path('check_rule_uniqueness/', views.check_rule_uniqueness)
]
# path('rule/<str:pk>/',views.rule_handler,   name="rule_handler")