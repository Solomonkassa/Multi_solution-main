# Generated by Django 5.0.3 on 2024-05-12 04:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_alter_preference_tg_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='otp',
            field=models.CharField(blank=True, max_length=4, null=True),
        ),
    ]
