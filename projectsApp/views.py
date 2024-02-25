from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout

from .models import Student,Coordinator,Lecturer
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from .AccessControl import coordinator_required, student_required,supervisor_required
# ==================================================================================================================
# Students Views here

def Home(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        try:
            student = Student.objects.get(email=email)
            # Authenticate user against our custom User Model (Student)
            user = authenticate(email=email, password=password)
            
            if user is not None:
                login(request, user)
                # Update last login time
                student.last_login = timezone.now()
                student.save()
                
                return redirect('student_dashboard')  # Replace 'dashboard' with the desired destination after login
            
            else:
                error_message = "Invalid username or password"
                return render(request, 'acounts/student_login.html', {'error_message': error_message})

        except Student.DoesNotExist:
            error_message = "User does not exist"
            return render(request, 'acounts/student_login.html', {'error_message': error_message})

    return render(request, 'acounts/student_login.html')

def logout_view(request):
    logout(request)   
    return redirect('home') 

# Student registration
def SignUp(request):
    if request.method == 'POST':
        regno = request.POST['regno']
        email = request.POST['email']
        name = request.POST['names']
        phone_number = request.POST['phone']
        intake_year = request.POST['intake_yr']
        password = request.POST['password']
        confirm_pass = request.POST['confirm_pass']

        # Check if passwords match
        if password != confirm_pass:
            error_message = "Passwords do not match"
            return render(request, 'acounts/signup.html', {'error_message': error_message})

        # Hash password
        hashed_password = make_password(password)

        # Create new student object
        student = Student(regno=regno, email=email, name=name, phone_number=phone_number, intake_year=intake_year, password=hashed_password)

        # Save student object to database
        student.save()

        success_message = "Registration successful. Please login to continue."
        return render(request, 'acounts/signup.html', {'success_message': success_message})

    return render(request, 'acounts/signup.html')


@student_required
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




# =================================================================================================================
# Supervisors views

def supervisor_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('supervisor_dashboard')
        else:
             return render(request, 'acounts/super_login.html', {'error_message': "Invalid username or password."})
        
    else:
        return render(request, 'acounts/super_login.html')

@supervisor_required
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

def cordinator_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        coordinator = authenticate(email=email, password=password)
        if coordinator is not None:
            if coordinator.is_staff:
                login(request, coordinator)
                return redirect('cordinator_dashboard')                
            else:
                 return render(request, 'acounts/cord_login.html', {'error_message': "You are not authorized to access this page."})
        else:
             return render(request, 'acounts/cord_login.html', {'error_message': "Invalid Email or Password."})
    else:
        return render(request, 'acounts/cord_login.html')

@coordinator_required
def cordinator_dashboard(request):
    return render(request, 'cordinator/cord_dashboard.html')

@coordinator_required
def supervisors(request):
    supervisors = Lecturer.objects.all().order_by('name')
    for i, supervisor in enumerate(supervisors):
        supervisor.index = i + 1 
    context = {'supervisors':supervisors}
    return render(request, 'cordinator/supervisors.html', context)

@coordinator_required
def add_supervisor(request):
    if request.method == 'POST':
        email = request.POST['email']
        name = request.POST['names']
        phone_number = request.POST['phone']
        password = request.POST['password']
        confirm_pass = request.POST['confirm_pass']

        # Check if passwords match
        if password != confirm_pass:
            error_message = "Passwords do not match"
            return render(request, 'acounts/signup.html', {'error_message': error_message})

        # Hash password
        hashed_password = make_password(password)

        # Create new student object
        lecturer = Lecturer(email=email, name=name, phone=phone_number, password=hashed_password)

        # Save student object to database
        lecturer.save()

        success_message = "Registration successful. Please login to continue."
        return render(request, 'cordinator/add_lecturer.html', {'success_message': success_message})

    return render(request, 'cordinator/add_lecturer.html')

@coordinator_required
def reg_students(request):
    students = Student.objects.all().order_by('regno')
    for i, student in enumerate(students):
        student.index = i + 1 
    context = {'students':students}
    return render(request, 'cordinator/students.html', context)

def view_projects(request):
    return render(request, 'cordinator/projects.html')

def pending_titles(request):
    return render(request, 'cordinator/pending_titles.html')

def approved_titles(request):
    return render(request, 'cordinator/approved_titles.html')

def view_milestones_cord(request):
    return render(request, 'cordinator/milestones_cord.html')

def make_announcement(request):
    return render(request, 'cordinator/make_announcement.html')

def view_project_title(request):
    return render(request, 'cordinator/view_project.html')
