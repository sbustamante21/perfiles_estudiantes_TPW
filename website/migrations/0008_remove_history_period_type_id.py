# Generated by Django 5.0.6 on 2024-06-04 04:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0007_alter_interest_interest_type_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='history',
            name='period_type_id',
        ),
    ]
