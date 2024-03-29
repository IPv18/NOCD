"""NOCD URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import multiprocessing
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',
         include(('dashboard.urls', "dashboard"), namespace='dashboard')),
    path('firewall/',
         include(('firewall.urls', "firewall"), namespace='firewall')),
    path('notifications/',
         include(('notification.urls', "notification"), namespace='notification')),
    path('traffic_control/',
         include(('traffic_control.urls', "traffic_control"), namespace='traffic_control')),
]

print("Starting network sniffer...")
from network_sniffer.network_sniffer import main as network_sniffer_main
ps = multiprocessing.Process(target=network_sniffer_main)
ps.daemon = True
ps.start()