# Generated by Django 5.0.2 on 2024-02-26 22:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projectsApp', '0004_announcement_notifications_project_milestone'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Announcement',
            new_name='Announcements',
        ),
        migrations.RenameModel(
            old_name='Project',
            new_name='Projects',
        ),
    ]