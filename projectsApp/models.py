from django.db import models
from django.contrib.auth.models import AbstractUser


#Cordinator model
class Coordinator(AbstractUser):
    pass

# Student model
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

# lecturer model
class Lecturer(models.Model):
    email = models.EmailField(max_length=255, unique=True, blank=False)
    name = models.CharField(max_length=255)
    phone = models.IntegerField(null=True, blank=True)
    password = models.CharField(max_length=128, null=False, blank=False)
    user_id = models.AutoField(primary_key=True)
    last_login = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone']

    @property
    def is_authenticated(self):
        return True
    
    class Meta:
        db_table = "Lecturers"

# projects model
class Projects(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    objectives = models.TextField()
    lecturer = models.ForeignKey(Lecturer, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'), 
        ('approved', 'Approved'), 
        ('rejected', 'Rejected')
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Notifications model
class Notifications(models.Model):
    sender = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    recipient = models.ForeignKey(Student, on_delete=models.CASCADE)
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

# Milestones Model 
class Milestone(models.Model):
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateTimeField()
    is_completed = models.BooleanField(default=False)

# Announcements model
class Announcements(models.Model):
    sender = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # Order announcements by creation date (newest first)

# Announcements model
class CoordinatorFeedbacks(models.Model):
    sender = models.ForeignKey(Coordinator, on_delete=models.CASCADE)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # Order announcements by creation date (newest first)

# Announcements model
class CoordinatorAnnouncements(models.Model):
    sender = models.ForeignKey(Coordinator, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # Order announcements by creation date (newest first)
