# Generated by Django 5.0.2 on 2024-03-07 10:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projectsApp', '0014_alter_proposal_project'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposal',
            name='project',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='proposals', to='projectsApp.projects'),
        ),
    ]