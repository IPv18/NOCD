from django.contrib import admin
from django.urls import path
from . import views

"""
urlpatterns = [
    path('',                       views.index,         name="home"),
    path('addrule/',               views.add_rule,      name="addrule"),    
    path('updaterule/<str:pk>/',   views.update_rule,   name="updaterule"), 
    path('removerule/<str:pk>/',   views.remove_rule,   name="removerule"), 
    path('check_rule_uniqueness/', views.check_rule_uniqueness)
]
"""

urlpatterns = [
    path('',                   views.index_RESTful,         name="home"),           # GET   --> render(home_page.html) + context(tables)  
                                                                                    # POST  --> add_rule               --> 
    path('check_rule_uniqueness/', views.check_rule_uniqueness),                    # GET   --> check_rule_uniqueness  --> json_response(success/fail)                                                               
    path('rule/<str:pk>/',     views.rule_handler_RESTFUL,  name="rule_handler")    # GET   --> get_rule               --> json_Response(rule/fail)
]                                                                                   # PATCH --> switch rule#1000 action--> json_response(success/fail)
                                                                                    # DELETE--> delete_rule            --> json_response(success/fail)
