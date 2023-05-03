from django.apps import AppConfig
from .traffic_control import update_tc, bootstrap_tc

class TrafficControlConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'traffic_control'

    def ready(self):
        # Bootstrap the traffic control system
        from .models import TCPolicy
        # Disable all policies that are not startup policies
        TCPolicy.objects.filter(startup=False).update(enabled=False)
        startup_policies = TCPolicy.objects.filter(startup=True)
        bootstrap_tc(startup_policies)
