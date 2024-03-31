# Generated by Django 5.0.2 on 2024-03-31 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projectsApp', '0024_resources_file_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegistrationSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registration_open', models.BooleanField(default=False)),
                ('allowed_intake_year', models.IntegerField()),
            ],
        ),
        migrations.AlterField(
            model_name='projects',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='Pending', max_length=50),
        ),
    ]