# Generated by Django 5.0.3 on 2024-05-01 08:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_preference'),
    ]

    operations = [
        migrations.AlterField(
            model_name='preference',
            name='tg_id',
            field=models.BigIntegerField(null=True),
        ),
    ]
