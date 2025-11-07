# Generated migration to remove video functionality

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('complaints', '0005_merge_20251030_1212'),
    ]

    operations = [
        # Remove video_file field
        migrations.RemoveField(
            model_name='complaint',
            name='video_file',
        ),
        # Remove video_analysis field
        migrations.RemoveField(
            model_name='complaint',
            name='video_analysis',
        ),
        # Update audio_transcription help text (remove video reference)
        migrations.AlterField(
            model_name='complaint',
            name='audio_transcription',
            field=models.TextField(blank=True, help_text="Transcribed text from audio files"),
        ),
        # Update detected_objects help text (remove video reference)
        migrations.AlterField(
            model_name='complaint',
            name='detected_objects',
            field=models.JSONField(blank=True, default=list, help_text="Objects detected in images"),
        ),
    ]
