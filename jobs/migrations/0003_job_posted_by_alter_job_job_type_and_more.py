# Generated by Django 5.1.5 on 2025-02-19 11:10

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0002_alter_job_company_alter_job_required_skills'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='posted_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posted_jobs', to=settings.AUTH_USER_MODEL, verbose_name='Posted By'),
        ),
        migrations.AlterField(
            model_name='job',
            name='job_type',
            field=models.CharField(choices=[('Full-time', 'Full-time'), ('Part-time', 'Part-time'), ('Internship', 'Internship'), ('Contract', 'Contract')], default='Full-time', max_length=20, verbose_name='Job Type'),
        ),
        migrations.AlterField(
            model_name='job',
            name='required_skills',
            field=models.JSONField(default=[], verbose_name='Required Skills'),
        ),
        migrations.AlterField(
            model_name='job',
            name='salary_max',
            field=models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Maximum Salary'),
        ),
        migrations.AlterField(
            model_name='job',
            name='salary_min',
            field=models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Minimum Salary'),
        ),
    ]
