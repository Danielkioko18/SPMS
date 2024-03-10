import os
from django.db import models
from django.utils import timezone
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


# Phases Model
class Phases(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Ensure unique phase names
    description = models.TextField()
    order = models.IntegerField(unique=True)  # Ensure unique order for phases
    deadline_date = models.DateField(null=True, blank=True)  # Optional deadline for phase

    def __str__(self):
        return self.name


# Proposal model 
class Proposal(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='proposals')  # Link to Student model
    title = models.CharField(max_length=255)
    current_phase = models.ForeignKey(Phases, on_delete=models.SET_NULL, null=True, related_name='proposals')
    lecturer = models.ForeignKey(Lecturer, on_delete=models.SET_NULL, null=True, related_name='proposals')
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, null=True, related_name='proposals')  # Filter by project status
    completed = models.BooleanField(default=False)

    def move_to_next_phase(self):
        current_phase = self.current_phase
        next_phase = Phases.objects.filter(order__gt=current_phase.order).order_by('order').first()
        if next_phase:
            self.current_phase = next_phase
            self.save()

    """
        Check if all phases are completed.
    """
    def check_completion(self):        
        remaining_phases = Phases.objects.filter(order__gt=self.current_phase.order)
        if not remaining_phases.exists():
            self.completed = True
            self.save()

    def __str__(self):
        return f"{self.student.name} - {self.title}"

# Documents Model   
class Documents(models.Model):
    proposal = models.ForeignKey(Proposal, related_name='documents', on_delete=models.CASCADE)
    phase = models.ForeignKey(Phases, related_name='documents', on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/')
    file_name = models.CharField(max_length=255, default=None)  
    uploaded_at = models.DateTimeField(default=timezone.now)
    comment = models.TextField()
    student = models.ForeignKey(Student, related_name='documents', on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('revision_requested', 'Revision Required')
    ], default='pending')

    def save(self, *args, **kwargs):
        if not self.file_name:  # If file name is not already set
            self.file_name = os.path.basename(self.file.name)
        super().save(*args, **kwargs)
    


    def __str__(self):
        return f"{self.proposal.title} - {self.phase.name} - {self.status}"
    
    
    
# Notifications model
class Notifications(models.Model):
    sender = models.ForeignKey(Lecturer, on_delete=models.CASCADE, related_name='notifications')
    recipient = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

# Announcements model
class Announcements(models.Model):
    sender = models.ForeignKey(Lecturer, on_delete=models.CASCADE, related_name='announcements')
    subject = models.CharField(max_length=255)
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # Order announcements by creation date (newest first)

# Announcements model
class CoordinatorFeedbacks(models.Model):
    sender = models.ForeignKey(Coordinator, on_delete=models.CASCADE, related_name='coordinatorfeedbacks')
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, related_name='coordinatorfeedbacks')
    comment = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # Order announcements by creation date (newest first)

# Announcements model
class CoordinatorAnnouncements(models.Model):
    sender = models.ForeignKey(Coordinator, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # Order announcements by creation date (newest first)

# Announcements model
class Resources(models.Model):
    subject = models.CharField(max_length=255, default=None)  
    file = models.FileField(upload_to='resources/')
    uploaded_at = models.DateTimeField(default=timezone.now)
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # Order announcements by creation date (newest first)
