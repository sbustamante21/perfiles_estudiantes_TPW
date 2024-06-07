# Generated by Django 5.0.6 on 2024-06-06 03:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0013_rename_user_id_profile_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='personal_mail',
            field=models.EmailField(blank=True, max_length=254, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='pfp',
            field=models.ImageField(null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='student',
            name='phone_number',
            field=models.IntegerField(blank=True, null=True, unique=True),
        ),
    ]
