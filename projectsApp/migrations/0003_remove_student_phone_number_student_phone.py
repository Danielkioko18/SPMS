# Generated by Django 5.1.3 on 2024-12-04 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projectsApp', '0002_alter_lecturer_phone'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='phone_number',
        ),
        migrations.AddField(
            model_name='student',
            name='phone',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
