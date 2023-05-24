from django.db import models
from django.core.exceptions import ValidationError
import uuid

class FirewallRule(models.Model):
    direction_choices = [
        ('Inbound', 'Inbound'),
        ('Outbound', 'Outbound')
    ]
    ip_family_choices = [
        ('IPv4', 'IPv4'),
        ('IPv6', 'IPv6')
    ]
    type_choices = [
        ('CUSTOM TCP', 'CUSTOM TCP'), ('CUSTOM UDP', 'CUSTOM UDP'), ('CUSTOM ICMP', 'CUSTOM ICMP'),
        ('ALL TCP', 'ALL TCP'), ('ALL UDP', 'ALL UDP'), ('ALL ICMP', 'ALL ICMP'),
        ('SSH 22', 'SSH 22'), ('TELNET 23', 'TELNET 23'), ('SMTP 25', 'SMTP 25'),
        ('NAMESERVER 42', 'NAMESERVER 42'), ('DNS UDP 53', 'DNS UDP 53'), ('DNS TCP 53', 'DNS TCP 53'),
        ('HTTP 80', 'HTTP 80'), ('POP3 110', 'POP3 110'), ('IMAP 143', 'IMAP 143'), ('LDAP 389', 'LDAP 389'),
        ('HTTPS 443', 'HTTPS 443'), ('SMB 445', 'SMB 445'), ('SMTPS 465', 'SMTPS 465'),
        ('IMAPS 993', 'IMAPS 993'), ('POP3S 995', 'POP3S 995'), ('NFS 2049', 'NFS 2049')
    ]
    action_choices = [
        ('ACCEPT', 'ACCEPT'),
        ('DROP', 'DROP'),
        ('LOG', 'LOG')
    ]
    protocol_choices = [
        ('TCP', 'TCP'),
        ('UDP', 'UDP'),
        ('ICMP', 'ICMP')
    ]
    
    rule_priority = models.IntegerField()
    description = models.CharField(max_length=230)
    traffic_direction = models.CharField(max_length=30, choices=direction_choices, default='Inbound')
    ip_family = models.CharField(max_length=30, choices=ip_family_choices, default='IPv4')
    type = models.CharField(max_length=50, choices=type_choices, default="CUSTOM TCP", null=True, blank=True)
    protocol = models.CharField(max_length=10, choices=protocol_choices, default="TCP", null=True, blank=True)
    source_address = models.CharField(max_length=45, null=True, blank=True)
    source_port = models.CharField(max_length=15, null=True, blank=True)
    destination_address = models.CharField(max_length=45, null=True, blank=True)
    destination_port = models.CharField(max_length=15, null=True, blank=True)
    action = models.CharField(max_length=15, choices=action_choices, default='DROP')
    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    class Meta:
        unique_together = ('rule_priority', 'traffic_direction', 'ip_family')

    def __str__(self):
        return self.description

    def to_dict(self):
        return {
            'id': str(self.id),
            'rule_priority': self.rule_priority,
            'description': self.description,
            'traffic_direction': self.traffic_direction,
            'ip_family': self.ip_family,
            'type': self.type,
            'protocol': self.protocol,
            'source_address': self.source_address,
            'source_port': self.source_port,
            'destination_address': self.destination_address,
            'destination_port': self.destination_port,
            'action': self.action
        }
    