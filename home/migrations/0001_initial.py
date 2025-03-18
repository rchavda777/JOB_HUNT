# Generated by Django 5.1.5 on 2025-02-12 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Full Name')),
                ('email', models.EmailField(max_length=254, verbose_name='Email Address')),
                ('message', models.TextField(verbose_name='YOur Message')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Submitted On')),
            ],
            options={
                'verbose_name': 'Contact Inquiry',
                'verbose_name_plural': 'Contact Inquiries',
            },
        ),
    ]
