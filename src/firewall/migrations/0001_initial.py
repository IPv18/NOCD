# Generated by Django 4.1.4 on 2023-05-31 13:30

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FirewallRule',
            fields=[
                ('rule_priority', models.IntegerField()),
                ('description', models.CharField(max_length=230)),
                ('traffic_direction', models.CharField(choices=[('Inbound', 'Inbound'), ('Outbound', 'Outbound')], default='Inbound', max_length=30)),
                ('ip_family', models.CharField(choices=[('IPv4', 'IPv4'), ('IPv6', 'IPv6')], default='IPv4', max_length=30)),
                ('type', models.CharField(blank=True, choices=[('CUSTOM TCP', 'CUSTOM TCP'), ('CUSTOM UDP', 'CUSTOM UDP'), ('CUSTOM ICMP', 'CUSTOM ICMP'), ('ALL TCP', 'ALL TCP'), ('ALL UDP', 'ALL UDP'), ('ALL ICMP', 'ALL ICMP'), ('SSH 22', 'SSH 22'), ('TELNET 23', 'TELNET 23'), ('SMTP 25', 'SMTP 25'), ('NAMESERVER 42', 'NAMESERVER 42'), ('DNS UDP 53', 'DNS UDP 53'), ('DNS TCP 53', 'DNS TCP 53'), ('HTTP 80', 'HTTP 80'), ('POP3 110', 'POP3 110'), ('IMAP 143', 'IMAP 143'), ('LDAP 389', 'LDAP 389'), ('HTTPS 443', 'HTTPS 443'), ('SMB 445', 'SMB 445'), ('SMTPS 465', 'SMTPS 465'), ('IMAPS 993', 'IMAPS 993'), ('POP3S 995', 'POP3S 995'), ('NFS 2049', 'NFS 2049')], default='CUSTOM TCP', max_length=50, null=True)),
                ('protocol', models.CharField(blank=True, choices=[('TCP', 'TCP'), ('UDP', 'UDP'), ('ICMP', 'ICMP')], default='TCP', max_length=10, null=True)),
                ('source_domain', models.CharField(blank=True, max_length=50, null=True)),
                ('source_address', models.CharField(blank=True, max_length=45, null=True)),
                ('source_port', models.CharField(blank=True, max_length=15, null=True)),
                ('destination_domain', models.CharField(blank=True, max_length=50, null=True)),
                ('destination_address', models.CharField(blank=True, max_length=45, null=True)),
                ('destination_port', models.CharField(blank=True, max_length=15, null=True)),
                ('action', models.CharField(choices=[('ACCEPT', 'ACCEPT'), ('DROP', 'DROP'), ('LOG', 'LOG')], default='DROP', max_length=15)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
            ],
            options={
                'unique_together': {('rule_priority', 'traffic_direction', 'ip_family')},
            },
        ),
    ]
