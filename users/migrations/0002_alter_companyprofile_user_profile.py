# Generated by Django 5.1.5 on 2025-02-14 10:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companyprofile',
            name='user_profile',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='company', to='users.userprofile'),
            preserve_default=False,
        ),
    ]
