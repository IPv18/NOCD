from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('',                       views.index,         name="home"),
    path('addrule/',               views.add_rule,      name="addrule"),    
    path('updaterule/<str:pk>/',   views.update_rule,   name="updaterule"), 
    path('removerule/<str:pk>/',   views.remove_rule,   name="removerule"), 
    path('check_rule_uniqueness/', views.check_rule_uniqueness)
]


# path('rule/<str:pk>/',views.rule_handler,   name="rule_handler")
# TODO - addrule should be a POST request into index
# TODO - update should be a PUT request into rule_handler
# TODO - delete should be a DELETE request into rule_handler


"""
urlpatterns = [
    path('',                   views.index_RESTful,         name="home"),
    path('rule/',              views.rule_RESTful ,         name="rule"),
    path('rule/<str:pk>/',     views.rule_handler_RESTFUL,  name="rule_handler")
]
"""