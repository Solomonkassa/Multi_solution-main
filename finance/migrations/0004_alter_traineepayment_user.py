# Generated by Django 5.0.3 on 2024-05-01 08:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_preference'),
        ('finance', '0003_delete_preference'),
    ]

    operations = [
        migrations.AlterField(
            model_name='traineepayment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s', related_query_name='%(class)s', to='account.trainee', verbose_name='Trainee'),
        ),
    ]
