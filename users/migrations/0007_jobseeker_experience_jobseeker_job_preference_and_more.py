# Generated by Django 5.1.5 on 2025-02-27 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_remove_companyprofile_user_profile_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobseeker',
            name='experience',
            field=models.PositiveIntegerField(blank=True, help_text='Enter expirence in years', null=True, verbose_name='Years of Experience'),
        ),
        migrations.AddField(
            model_name='jobseeker',
            name='job_preference',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Job Preference'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='address',
            field=models.TextField(blank=True, null=True, verbose_name='Adress'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='date_of_birth',
            field=models.DateField(blank=True, null=True, verbose_name='Date of Birth'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='gender',
            field=models.CharField(blank=True, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], max_length=10, null=True, verbose_name='Gender'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='mobile_number',
            field=models.CharField(blank=True, max_length=15, null=True, verbose_name='Mobile Number'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile_picture', verbose_name='Profile Picture'),
        ),
    ]
