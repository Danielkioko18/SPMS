from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from .models import Student, Lecturer, Coordinator


class StudentBackend(BaseBackend):
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
        
class LecturerBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None):
        try:
            lecturer = Lecturer.objects.get(email=email)
            if check_password(password, lecturer.password):
                return lecturer
        except Lecturer.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Lecturer.objects.get(pk=user_id)
        except Lecturer.DoesNotExist:
            return None
        
class CoordinatorBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None):
        try:
            coordinator = Coordinator.objects.get(email=email)
            if coordinator.check_password(password):
                return coordinator
        except Coordinator.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Coordinator.objects.get(pk=user_id)
        except Coordinator.DoesNotExist:
            return None