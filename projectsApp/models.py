from django.db import models
from django.contrib.auth.models import AbstractUser

class Coordinator(AbstractUser):
    pass

class Student(models.Model):
    regno = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    phone_number = models.IntegerField(null=True, blank=True)
    intake_year = models.PositiveSmallIntegerField(default=2024)
    password = models.CharField(max_length=128, null=False, blank=False)
    user_id = models.AutoField(primary_key=True)
    last_login = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['regno', 'name', 'phone_number']

    @property
    def is_authenticated(self):
        return True

    class Meta:
        db_table = "students"

class Lecturer(models.Model):
    email = models.EmailField(max_length=255, unique=True, blank=False)
    name = models.CharField(max_length=255)
    phone = models.IntegerField(null=True, blank=True)
    password = models.CharField(max_length=128, null=False, blank=False)
    user_id = models.AutoField(primary_key=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone']

    class Meta:
        db_table = "Lecturers"
