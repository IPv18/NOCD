from django.apps import AppConfig


class FirewallConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'firewall'

    def ready(self):
        self.check_last_rules()

    def check_last_rules(self):
        from firewall.models import FirewallRule
        rules = [
            FirewallRule.objects.filter(
                IP_family='IPv4', traffic_direction='Inbound', rule_num=1000),
            FirewallRule.objects.filter(
                IP_family='IPv4', traffic_direction='Outbound', rule_num=1000),
            FirewallRule.objects.filter(
                IP_family='IPv6', traffic_direction='Inbound', rule_num=1000),
            FirewallRule.objects.filter(
                IP_family='IPv6', traffic_direction='Outbound', rule_num=1000),
        ]

        if not rules[0]:
            FirewallRule.objects.create(
                IP_family='IPv4', traffic_direction='Inbound', rule_num=1000, action='ACCEPT')

        if not rules[1]:
            FirewallRule.objects.create(
                IP_family='IPv4', traffic_direction='Outbound', rule_num=1000, action='ACCEPT')

        if not rules[2]:
            FirewallRule.objects.create(
                IP_family='IPv6', traffic_direction='Inbound', rule_num=1000, action='ACCEPT')

        if not rules[3]:
            FirewallRule.objects.create(
                IP_family='IPv6', traffic_direction='Outbound', rule_num=1000, action='ACCEPT')