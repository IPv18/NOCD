# Generated by Django 4.1.4 on 2023-04-05 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('firewall', '0014_alter_firewallrule_destination_address_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='firewallrule',
            name='traffic_direction',
            field=models.CharField(choices=[('Inbound', 'Inbound'), ('Outbound', 'Outbound')], default='INBOUND', max_length=30),
        ),
    ]
