from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

# Create your views here.

# Students Views here

def Home(request):
    return render(request, 'acounts/login.html')

def SignUp(request):
    return render(request, 'acounts/signup.html')

def student_dashboard(request):
    return render(request, 'students/student_dashboard.html')

def upload_title(request):
    return render(request, 'students/upload_title.html')

def upload_file(request):
    return render(request, 'students/upload_docs.html')

def announcements(request):
    return render(request, 'students/announcements.html')

def notifications(request):
    return render(request, 'students/notifications.html')

def resources(request):
    return render(request, 'students/resources.html')


# Supervisors views

def supervisor_dashboard(request):
    return render(request, 'supervisors/super_dashboard.html')

def mystudents(request):
    return render(request, 'supervisors/mystudents.html')

def announcemnt(request):
    return render(request, 'supervisors/announcement.html')

def lec_resource(request):
    return render(request, 'supervisors/upload_resource.html')

def results(request):
    return render(request, 'supervisors/results.html')

def milestones(request):
    return render(request, 'supervisors/milestones.html')

def student_upload(request):
    return render(request, 'supervisors/student_upload.html')


# Coordinator's views

def cordinator_dashboard(request):
    return render(request, 'cordinator/cord_dashboard.html')

def supervisors(request):
    return render(request, 'cordinator/supervisors.html')

def reg_students(request):
    return render(request, 'cordinator/students.html')

def view_projects(request):
    return render(request, 'cordinator/projects.html')

def pending_titles(request):
    return render(request, 'cordinator/pending_titles.html')

def approved_titles(request):
    return render(request, 'cordinator/aproved_titles.html')

def view_milestones_cord(request):
    return render(request, 'cordinator/milstones_cord.html')

def make_announcement(request):
    return render(request, 'cordinator/make_announcement.html')

def view_project_title(request):
    return render(request, 'cordinator/view_project.html')
