from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('',                       views.home,                  name="home"),           # GET   --> render(firewall.html)
    path('rule/',                  views.rule,                  name="rule"),           # GET   --> render(addrule.html) + form()
                                                                                        # POST  --> save form(new_rule) & redirect(firewall.html)
    path('check_rule_uniqueness/', views.check_rule_uniqueness),                        # GET   --> jsonresponse({'exists':True/False})
    path('rule/<str:pk>/',         views.rule_handler,          name="rule_handler")    # GET   --> render(addrule.html) + form(rule)
]                                                                                       # POST  --> save form(modified_rule) & redirect(firewall.html)
                                                                                        # PATCH --> jsonresponse({'success':True/False})/switch policy
                                                                                        # DELETE--> jsonresponse({'success':True/False})/delete rule
                                                                                        