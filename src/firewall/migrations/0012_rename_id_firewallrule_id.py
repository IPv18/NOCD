# Generated by Django 4.1.4 on 2023-04-01 14:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('firewall', '0011_alter_firewallrule_rule_num_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='firewallrule',
            old_name='id',
            new_name='ID',
        ),
    ]
