from django.apps import AppConfig

class FirewallConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'firewall'

    def ready(self):
        self.check_last_rules()

    def check_last_rules(self):
        from firewall.models import FirewallRule
        from firewall.views import update_ip_tables
        rules = FirewallRule.objects.filter(rule_priority=1000)

        try:
            if not rules:
                FirewallRule.objects.create(
                    ip_family='IPv4', traffic_direction='Inbound', rule_priority=1000, 
                    description="ALL TRAFFIC", type="", protocol="", action='ACCEPT')
                FirewallRule.objects.create(
                    ip_family='IPv4', traffic_direction='Outbound', rule_priority=1000,
                     description="ALL TRAFFIC", type="", protocol="", action='ACCEPT')
                FirewallRule.objects.create(
                    ip_family='IPv6', traffic_direction='Inbound', rule_priority=1000,
                     description="ALL TRAFFIC", type="", protocol="", action='ACCEPT')
                FirewallRule.objects.create(
                    ip_family='IPv6', traffic_direction='Outbound', rule_priority=1000,
                     description="ALL TRAFFIC", type="", protocol="", action='ACCEPT')
            update_ip_tables('IPv4', 'Inbound')
            update_ip_tables('IPv4', 'Outbound')
            update_ip_tables('IPv6', 'Inbound')
            update_ip_tables('IPv6', 'Outbound')
        except Exception as e:
            # TODO: log error or handle exception
            pass
        
