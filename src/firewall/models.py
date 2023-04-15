from django.db import models
from django.core.exceptions import ValidationError
import uuid


class FirewallRule(models.Model):
    directions = [
        ('Inbound', 'Inbound'),
        ('Outbound', 'Outbound')
    ]

    ip_families = [
        ('IPv4', 'IPv4'),
        ('IPv6', 'IPv6')
    ]

    types = [
        ('CUSTOM TCP', 'CUSTOM TCP'), ('CUSTOM UDP', 'CUSTOM UDP'), ('CUSTOM ICMP', 'CUSTOM ICMP'),
        ('ALL TCP', 'ALL TCP'), ('ALL UDP', 'ALL UDP'), ('ALL ICMP', 'ALL ICMP'),
        ('SSH 22', 'SSH 22'),('TELNET 23', 'TELNET 23'),('SMTP 25', 'SMTP 25'),
        ('NAMESERVER 42', 'NAMESERVER 42'),('DNS UDP 53', 'DNS UDP 53'), ('DNS TCP 53', 'DNS TCP 53'),
        ('HTTP 80', 'HTTP 80'),('POP3 110', 'POP3 110'), ('IMAP 143', 'IMAP 143'), ('LDAP 389', 'LDAP 389'),
        ('HTTPS 443', 'HTTPS 443'),('SMB 445', 'SMB 445'), ('SMTPS 465', 'SMTPS 465'),
        ('IMAPS 993', 'IMAPS 993'),('POP3S 995', 'POP3S 995'),('NFS 2049', 'NFS 2049')
    ]

    actions = [
        ('ACCEPT', 'ACCEPT'),
        ('DROP', 'DROP'),
        ('LOG', 'LOG')
    ]

    protocols = [
        ('TCP', 'TCP'),
        ('UDP', 'UDP'),
        ('ICMP', 'ICMP')
    ]

    rule_num = models.IntegerField()
    description = models.CharField(max_length=255)

    traffic_direction = models.CharField(max_length=30, choices=directions, default='Inbound')   
    ip_family = models.CharField(max_length=30, choices=ip_families, default='IPv4')   
    type = models.CharField(max_length=50, choices=types, default='CUSTOM TCP', null=True, blank=True)

    source_address = models.CharField(max_length=45, null=True, blank=True)
    source_port = models.IntegerField(null=True, blank=True)

    destination_address = models.CharField(max_length=45, null=True, blank=True)
    destination_port = models.IntegerField(null=True, blank=True)

    action = models.CharField(max_length=15, choices=actions, default='DROP')
    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    class Meta:
        unique_together = ('rule_num', 'traffic_direction', 'ip_family')

    def __str__(self):
        return self.description
