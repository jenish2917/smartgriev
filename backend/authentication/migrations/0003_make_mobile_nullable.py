"""
Fix mobile field to allow NULL values
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_alter_user_address_alter_user_mobile_otpverification_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='mobile',
            field=models.CharField(max_length=15, blank=True, null=True),
        ),
    ]
