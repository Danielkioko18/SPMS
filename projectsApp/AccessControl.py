from .models import Student,Coordinator,Lecturer
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

# coordinator decorator
def coordinator_required(function):
    """
    Decorator that restricts access to a view only for logged-in coordinators.
    """
    @login_required
    def wrapper(request, *args, **kwargs):
        if not isinstance(request.user, Coordinator):
            return redirect('cordinator_login')
        return function(request, *args, **kwargs)
    return wrapper

# Student decorator
def student_required(function):
    """
    Decorator that restricts access to a view only for logged-in students.
    """
    @login_required
    def wrapper(request, *args, **kwargs):
        if not isinstance(request.user, Student):
            return redirect('home')
        return function(request, *args, **kwargs)
    return wrapper

# Supervisor decorator
def supervisor_required(function):
    """
    Decorator that restricts access to a view only for logged-in students.
    """
    @login_required
    def wrapper(request, *args, **kwargs):
        if not isinstance(request.user, Lecturer):
            return redirect('home')
        return function(request, *args, **kwargs)
    return wrapper