# Generated by Django 4.2.4 on 2025-07-27 05:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GeoAnalytics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('analysis_type', models.CharField(max_length=50)),
                ('analysis_date', models.DateTimeField(auto_now_add=True)),
                ('results', models.JSONField()),
                ('parameters', models.JSONField(default=dict)),
                ('data_version', models.CharField(max_length=50)),
                ('algorithm_version', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='GeospatialCluster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cluster_id', models.CharField(max_length=100, unique=True)),
                ('cluster_type', models.CharField(choices=[('hotspot', 'Complaint Hotspot'), ('pattern', 'Pattern Cluster'), ('temporal', 'Temporal Cluster'), ('category', 'Category Cluster')], max_length=20)),
                ('center_lat', models.FloatField()),
                ('center_lon', models.FloatField()),
                ('radius_meters', models.FloatField()),
                ('complaint_count', models.IntegerField()),
                ('severity_score', models.FloatField()),
                ('category_distribution', models.JSONField(default=dict)),
                ('first_complaint_date', models.DateTimeField()),
                ('last_complaint_date', models.DateTimeField()),
                ('time_span_days', models.IntegerField()),
                ('is_active', models.BooleanField(default=True)),
                ('priority_level', models.CharField(default='medium', max_length=20)),
                ('recommended_actions', models.JSONField(default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='HeatmapData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('region_type', models.CharField(max_length=50)),
                ('region_id', models.CharField(max_length=100)),
                ('bounds', models.JSONField()),
                ('center_lat', models.FloatField()),
                ('center_lon', models.FloatField()),
                ('complaint_density', models.FloatField()),
                ('resolution_rate', models.FloatField()),
                ('avg_response_time', models.FloatField()),
                ('satisfaction_score', models.FloatField()),
                ('time_period', models.CharField(max_length=20)),
                ('period_start', models.DateTimeField()),
                ('period_end', models.DateTimeField()),
                ('total_complaints', models.IntegerField()),
                ('resolved_complaints', models.IntegerField()),
                ('pending_complaints', models.IntegerField()),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='LocationIntelligence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location_lat', models.FloatField()),
                ('location_lon', models.FloatField()),
                ('risk_score', models.FloatField()),
                ('predicted_complaint_types', models.JSONField(default=list)),
                ('seasonal_patterns', models.JSONField(default=dict)),
                ('demographic_factors', models.JSONField(default=dict)),
                ('preventive_measures', models.JSONField(default=list)),
                ('resource_allocation', models.JSONField(default=dict)),
                ('confidence_score', models.FloatField()),
                ('data_sources', models.JSONField(default=list)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='RouteOptimization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('route_date', models.DateField()),
                ('complaint_ids', models.JSONField(default=list)),
                ('route_coordinates', models.JSONField(default=list)),
                ('total_distance_km', models.FloatField()),
                ('estimated_time_hours', models.FloatField()),
                ('fuel_cost_estimate', models.FloatField(null=True)),
                ('is_completed', models.BooleanField(default=False)),
                ('actual_distance_km', models.FloatField(null=True)),
                ('actual_time_hours', models.FloatField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(null=True)),
                ('officer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='optimized_routes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
