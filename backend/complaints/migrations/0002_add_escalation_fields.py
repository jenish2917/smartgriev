"""
Migration to add escalated and escalation_date fields to Complaint model
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('complaints', '0001_initial'),  # Adjust based on your last migration
    ]

    operations = [
        migrations.AddField(
            model_name='complaint',
            name='escalated',
            field=models.BooleanField(default=False, help_text='Whether this complaint has been auto-escalated'),
        ),
        migrations.AddField(
            model_name='complaint',
            name='escalation_date',
            field=models.DateTimeField(null=True, blank=True, help_text='Date when complaint was escalated'),
        ),
    ]
