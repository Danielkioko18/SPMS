from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import check_password
from .models import Student


class StudentBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            student = Student.objects.get(email=email)
            if check_password(password, student.password):
                return student
        except Student.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Student.objects.get(pk=user_id)
        except Student.DoesNotExist:
            return None