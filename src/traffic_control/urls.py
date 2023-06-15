from django.urls import path, include

from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'policy', views.TCPolicyViewSet)
router.register(r'program_policy', views.ProgramTCPolicyViewSet)
router.register(r'ip_policy', views.IPTCPolicyViewSet)

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('', include(router.urls)),
    path("interface_metrics/", views.interface_metrics, name="pkt_metrics"),
    path("interfaces/", views.get_interfaces, name="interfaces"),
]
