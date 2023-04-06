from django.db import models
from django.core.exceptions import ValidationError
import uuid


class FirewallRule(models.Model):
    directions = [
        ('Inbound','Inbound'),
        ('Outbound','Outbound')
    ]
    IPfamily = [
        ('IPv4','IPv4'),
        ('IPv6','IPv6')
    ]
    types = [
        ('CUSTOM TCP','CUSTOM TCP'),('CUSTOM UDP','CUSTOM UDP'),('CUSTOM ICMP','CUSTOM ICMP'),('ALL TCP','ALL TCP'),('ALL UDP','ALL UDP'),
        ('ALL ICMP','ALL ICMP'),('SSH 22','SSH 22'),('TELNET 23','TELNET 23'),('SMTP 25','SMTP 25'),
        ('NAMESERVER 42','NAMESERVER 42'),('DNS UDP 53','DNS UDP 53'),('DNS TCP 53','DNS TCP 53'),('HTTP 80','HTTP 80'),('POP3 110','POP3 110'),
        ('IMAP 143','IMAP 143'),('LDAP 389','LDAP 389'),('HTTPS 443','HTTPS 443'),('SMB 445','SMB 445'),('SMTPS 465','SMTPS 465'),
        ('IMAPS 993','IMAPS 993'),('POP3S 995','POP3S 995'),('NFS 2049','NFS 2049')
    ]
    actions = [
        ('ACCEPT','ACCEPT'),
        ('DROP','DROP'),
        ('LOG','LOG')
    ]
    protocols = [
        ('TCP','TCP'),
        ('UDP','UDP'),
        ('ICMP','ICMP')
    ]
    rule_num = models.IntegerField()                                                                    # rule number (priority)
    description = models.CharField(max_length=255)                                                      # user's comment or description 
    traffic_direction = models.CharField(max_length=30, choices=directions, default='Inbound')   
    IP_family = models.CharField(max_length=30, choices=IPfamily, default='IPv4')      
    type = models.CharField(max_length=50, choices=types, default="CUSTOM TCP", null=True, blank=True)  # tuple of some well known protocols and their port numbers 
    protocol = models.CharField(max_length=10, choices=protocols, default="TCP", null=True, blank=True) # TCP/UDP/ICMP
    source_address = models.CharField(max_length=45, null=True, blank=True)
    source_port = models.IntegerField(null=True, blank=True)                                              
    destination_address = models.CharField(max_length=45, null=True, blank=True)
    destination_port = models.IntegerField(null=True, blank=True)
    action = models.CharField(max_length=15, choices=actions, default='DROP')                           # ALLOW/DENY/LOG(notify) 
    created = models.DateTimeField(auto_now_add=True)                                 
    ID = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    class Meta:
        unique_together = ('rule_num', 'traffic_direction', 'IP_family')

    def __str__(self):
        return self.description
