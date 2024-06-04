# Generated by Django 5.0.6 on 2024-06-04 04:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0008_remove_history_period_type_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='curriculumplan',
            name='name',
            field=models.CharField(default='PLAN X', max_length=10),
        ),
        migrations.AlterField(
            model_name='profile',
            name='role_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='website.roles'),
        ),
    ]
