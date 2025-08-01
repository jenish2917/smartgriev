# Generated by Django 4.2.4 on 2025-07-27 05:59

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chatbot', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuickReplyTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('intent', models.CharField(max_length=100)),
                ('buttons', models.JSONField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='chatlog',
            name='escalated_to_human',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='chatlog',
            name='escalation_reason',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='chatlog',
            name='input_language',
            field=models.CharField(choices=[('en', 'English'), ('hi', 'Hindi'), ('mr', 'Marathi'), ('gu', 'Gujarati'), ('ta', 'Tamil'), ('te', 'Telugu'), ('kn', 'Kannada'), ('ml', 'Malayalam'), ('bn', 'Bengali'), ('pa', 'Punjabi')], default='en', max_length=2),
        ),
        migrations.AddField(
            model_name='chatlog',
            name='reply_language',
            field=models.CharField(choices=[('en', 'English'), ('hi', 'Hindi'), ('mr', 'Marathi'), ('gu', 'Gujarati'), ('ta', 'Tamil'), ('te', 'Telugu'), ('kn', 'Kannada'), ('ml', 'Malayalam'), ('bn', 'Bengali'), ('pa', 'Punjabi')], default='en', max_length=2),
        ),
        migrations.AddField(
            model_name='chatlog',
            name='reply_metadata',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='chatlog',
            name='reply_type',
            field=models.CharField(choices=[('text', 'Text Reply'), ('quick_reply', 'Quick Reply Buttons'), ('rich_media', 'Rich Media'), ('escalation', 'Human Escalation')], default='text', max_length=20),
        ),
        migrations.AddField(
            model_name='chatlog',
            name='sentiment',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='chatlog',
            name='sentiment_score',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='chatlog',
            name='confidence',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='chatlog',
            name='intent',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.CreateModel(
            name='ChatSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.UUIDField(unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('context', models.JSONField(blank=True, default=dict)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_sessions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ChatNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(choices=[('status_update', 'Status Update'), ('reminder', 'Reminder'), ('info', 'Information'), ('alert', 'Alert')], max_length=20)),
                ('title', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('is_sent', models.BooleanField(default=False)),
                ('scheduled_at', models.DateTimeField()),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ChatFeedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(choices=[(1, 'Very Poor'), (2, 'Poor'), (3, 'Average'), (4, 'Good'), (5, 'Excellent')], validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('is_helpful', models.BooleanField()),
                ('comments', models.TextField(blank=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('chat_log', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='feedback', to='chatbot.chatlog')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='chatlog',
            name='session',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chatbot.chatsession'),
        ),
    ]
