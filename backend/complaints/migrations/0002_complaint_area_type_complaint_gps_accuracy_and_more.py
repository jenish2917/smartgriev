# Generated by Django 4.2.4 on 2025-07-27 05:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('complaints', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='complaint',
            name='area_type',
            field=models.CharField(blank=True, choices=[('residential', 'Residential Area'), ('commercial', 'Commercial Area'), ('industrial', 'Industrial Area'), ('public', 'Public Space'), ('road', 'Road/Highway'), ('park', 'Park/Garden'), ('other', 'Other')], max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='complaint',
            name='gps_accuracy',
            field=models.FloatField(blank=True, help_text='GPS accuracy in meters', null=True),
        ),
        migrations.AddField(
            model_name='complaint',
            name='incident_address',
            field=models.TextField(blank=True, help_text='Full address of incident location', null=True),
        ),
        migrations.AddField(
            model_name='complaint',
            name='incident_landmark',
            field=models.CharField(blank=True, help_text='Nearby landmark', max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='complaint',
            name='incident_latitude',
            field=models.FloatField(blank=True, help_text='Latitude where the incident occurred', null=True),
        ),
        migrations.AddField(
            model_name='complaint',
            name='incident_longitude',
            field=models.FloatField(blank=True, help_text='Longitude where the incident occurred', null=True),
        ),
        migrations.AddField(
            model_name='complaint',
            name='location_method',
            field=models.CharField(choices=[('gps', 'GPS'), ('manual', 'Manual Entry'), ('address', 'Address Lookup')], default='gps', max_length=50),
        ),
        migrations.AlterField(
            model_name='complaint',
            name='location_lat',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='complaint',
            name='location_lon',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='IncidentLocationHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('accuracy', models.FloatField(blank=True, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('update_reason', models.CharField(choices=[('initial', 'Initial Location'), ('correction', 'Location Correction'), ('verification', 'Field Verification'), ('auto_geocode', 'Automatic Geocoding')], max_length=100)),
                ('is_verified', models.BooleanField(default=False)),
                ('verification_method', models.CharField(blank=True, choices=[('field_visit', 'Field Visit'), ('photo_verification', 'Photo Verification'), ('landmark_match', 'Landmark Matching'), ('address_verification', 'Address Verification')], max_length=50, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('complaint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='location_history', to='complaints.complaint')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='GPSValidation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_valid', models.BooleanField(default=True)),
                ('validation_score', models.FloatField(default=1.0, help_text='Confidence score 0-1')),
                ('accuracy_check', models.BooleanField(default=True)),
                ('range_check', models.BooleanField(default=True)),
                ('duplicate_check', models.BooleanField(default=True)),
                ('speed_check', models.BooleanField(default=True)),
                ('validation_notes', models.TextField(blank=True, null=True)),
                ('validated_at', models.DateTimeField(auto_now_add=True)),
                ('complaint', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='gps_validation', to='complaints.complaint')),
                ('validated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
