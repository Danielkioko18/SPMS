# Generated by Django 5.0.2 on 2024-03-09 13:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projectsApp', '0017_documents_file_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposal',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='proposals', to='projectsApp.student'),
        ),
    ]
