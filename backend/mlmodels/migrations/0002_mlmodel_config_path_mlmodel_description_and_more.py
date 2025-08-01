# Generated by Django 4.2.4 on 2025-07-26 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mlmodels', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mlmodel',
            name='config_path',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='mlmodel',
            name='description',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='mlmodel',
            name='metadata',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='mlmodel',
            name='model_path',
            field=models.CharField(default='models/default', max_length=255),
        ),
        migrations.AddField(
            model_name='mlmodel',
            name='supported_languages',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='mlmodel',
            name='vocab_path',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='modelprediction',
            name='metadata',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='modelprediction',
            name='processing_time',
            field=models.FloatField(help_text='Processing time in seconds', null=True),
        ),
        migrations.AlterField(
            model_name='mlmodel',
            name='accuracy',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='mlmodel',
            name='model_type',
            field=models.CharField(choices=[('COMPLAINT', 'Complaint Classifier'), ('SENTIMENT', 'Sentiment Analyzer'), ('NER', 'Named Entity Recognition'), ('LANG', 'Language Detector'), ('TRANS', 'Translator')], max_length=20),
        ),
        migrations.AlterField(
            model_name='modelprediction',
            name='prediction',
            field=models.JSONField(),
        ),
        migrations.AlterUniqueTogether(
            name='mlmodel',
            unique_together={('name', 'version')},
        ),
        migrations.RemoveField(
            model_name='mlmodel',
            name='model_file',
        ),
    ]
