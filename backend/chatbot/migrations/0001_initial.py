# Generated by Django 5.2.4 on 2025-07-26 06:36

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('reply', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('intent', models.CharField(max_length=100, null=True)),
                ('confidence', models.FloatField(null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_logs', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
