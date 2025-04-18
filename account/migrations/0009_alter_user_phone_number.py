# Generated by Django 5.0.3 on 2024-05-21 06:25

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0008_alter_user_trans_num'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=models.CharField(blank=True, help_text='Required. 12-digit character should start with 251 followed by either 9 or 7 then 7 digits', max_length=12, null=True, unique=True, validators=[django.core.validators.RegexValidator(message='Invalid phone number: should start with 251 and be followed by either 9 or 7 then 8 digits', regex='^251(7|9)\\d{8}')]),
        ),
    ]
