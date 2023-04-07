# Generated by Django 4.1.4 on 2023-03-22 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('firewall', '0004_firewallrule_delete_rules'),
    ]

    operations = [
        migrations.AlterField(
            model_name='firewallrule',
            name='protocol',
            field=models.CharField(choices=[('TCP', 'TCP'), ('UDP', 'UDP'), ('ICMP', 'ICMP')], max_length=10),
        ),
    ]