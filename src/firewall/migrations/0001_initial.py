# Generated by Django 4.1.4 on 2023-03-17 11:07

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Rules',
            fields=[
                ('rule', models.IntegerField(unique=True)),
                ('type', models.CharField(max_length=50)),
                ('protocol', models.CharField(max_length=10)),
                ('source_address', models.CharField(max_length=255)),
                ('source_port', models.IntegerField()),
                ('destination_address', models.CharField(max_length=255)),
                ('destination_port', models.IntegerField()),
                ('action', models.CharField(max_length=10)),
                ('description', models.CharField(max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
            ],
        ),
    ]