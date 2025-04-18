# Generated by Django 5.0.3 on 2024-04-15 10:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0003_initial'),
        ('enrollment', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='user',
            field=models.OneToOneField(blank=True, help_text='The user associated with this contact (if applicable).', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='contact', to='account.trainee'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='user',
            field=models.OneToOneField(blank=True, help_text='The user enrolled in the training.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='enrollment', to='account.trainee'),
        ),
        migrations.AddField(
            model_name='training',
            name='trainee',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='enrolled_course', to='account.trainee'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='training',
            field=models.ForeignKey(blank=True, help_text='The training in which the user is enrolled.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='enrollments', to='enrollment.training'),
        ),
    ]
