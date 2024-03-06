from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login,logout
from .AccessControl import coordinator_required, student_required,supervisor_required
from .models import Student, CoordinatorFeedbacks, CoordinatorAnnouncements, Lecturer, Projects,Notifications,Announcements, Phases, Proposal, Documents
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages

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

# Logout from the system
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
    student = request.user
    my_project = Projects.objects.filter(student=student)
    context = {
        'student':student,
        'my_project':my_project
    }
    return render(request, 'students/student_dashboard.html', context)

@student_required
def upload_title(request):
    user = request.user
    if request.method == 'POST':
        title=request.POST['title']
        description=request.POST['description']
        objectives=request.POST['objectives']

        project_exists = Projects.objects.filter(student=user)
        if project_exists:
            error_message='You Already Uploaded A project Please Consinder updating it'
            context = {'error_message':error_message}
            return render(request, 'students/upload_title.html', context)
        else:
            project = Projects(title=title, description=description,objectives=objectives)
            project.student = request.user
            project.save()
            return redirect('student_dashboard')
              

    else:
        return render(request, 'students/upload_title.html')
    


@student_required
def view_phases(request):
    student = request.user
    # Fetch all phases (ordered by their order field)
    phases = Phases.objects.all().order_by('order')
    context = {'phases': phases}

    # Check if a specific phase is requested
    phase_id = request.GET.get('phase_id')
    if phase_id:
        phase = get_object_or_404(Phases, id=phase_id)
        documents = Documents.objects.filter(phase=phase, student=student)
        context['phase'] = phase
        context['documents'] = documents

    return render(request, 'students/view_phases.html', context)




def upload_file(request, document_id):
    document = get_object_or_404(Documents, pk=document_id)

    # Check if document belongs to a phase associated with the current student
    student = request.user
    if document.proposal.student != student or document.proposal.phase not in student.proposals.all().order_by('phase__order'):
        return redirect('view_phases')  # Redirect if unauthorized access

    if request.method == 'POST':
        document.file = request.FILES['document_file']
        document.explanation = request.POST.get('explanation')  # Get document explanation
        document.save()
        return redirect('view_phases')  # Redirect after successful upload

    context = {'document': document}
    return render(request, 'students/view_phases.html', context)



@student_required
def announcements(request):
    return render(request, 'students/announcements.html')


@student_required
def notifications(request):
    return render(request, 'students/notifications.html')


@student_required
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
            error_message = "Invalid Email or Password"            
            return render(request, 'acounts/super_login.html', {'error_message': error_message})        
    else:
        return render(request, 'acounts/super_login.html')



@supervisor_required
def supervisor_dashboard(request):
    current_user = request.user
    project_count = Projects.objects.filter(lecturer = current_user).count()
    announcement_count = Announcements.objects.filter(sender=current_user).count()
    context = {
        'project_count':project_count,
        'announcement_count':announcement_count
    }
    return render(request, 'supervisors/super_dashboard.html', context)


@supervisor_required
def mystudents(request):
    lecturer = request.user
    projects = Projects.objects.filter(lecturer=lecturer)
    
    for i, project in enumerate(projects):
        project.index=i+1

    context = {'projects':projects}
    return render(request, 'supervisors/mystudents.html', context)

@supervisor_required
def announcemnt(request):
    if request.method == 'POST':
        subject = request.POST['subject']
        message = request.POST['message']

        if subject and message:
            announcement = Announcements.objects.create(sender=request.user, 
                                                            subject=subject, 
                                                            message=message
                                                        )
            announcement.save()
            success_message = 'Announcement Send'
            context = {'success_message':success_message}
            return render(request, 'supervisors/announcement.html', context)
        else:
            error_message = 'Error all fields must be filled'
            context = {'error_message':error_message}
            return render(request, 'supervisors/announcement.html', context)  

    else:
        return render(request, 'supervisors/announcement.html')


@supervisor_required
def lec_resource(request):
    return render(request, 'supervisors/upload_resource.html')


@supervisor_required
def results(request):
    return render(request, 'supervisors/results.html')


@supervisor_required
def milestones(request):
    phases = Phases.objects.all().order_by('order')  # Get all phases in order

    context = {'phases': phases}
    return render(request, 'supervisors/milestones.html', context)


# View uploads

@supervisor_required
def view_student_uploads(request, student_id):
    student = Student.objects.get(pk=student_id)
    documents = Documents.objects.filter(proposal__student=student)
    context = {'student': student, 'documents': documents}
    return render(request, 'supervisors/student_upload.html', context)


# View Project details including descripton and objectives
@supervisor_required
def project_details(request, project_id):
    project =  get_object_or_404(Projects, pk=project_id)
    current_user = request.user

    if request.method == 'POST':
        comment = request.POST['comment']
        if comment:
            notification = Notifications.objects.create(
                sender=current_user, 
                recipient=project.student, 
                message=comment
            )
            notification.save()

    context = {
        'project':project,
        }
    
    return render(request, 'supervisors/project_details.html', context)




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
    supervisor_count = Lecturer.objects.all().count()
    student_count = Student.objects.all().count()
    project_count = Projects.objects.all().count()
    approved_count = Projects.objects.filter(status="Approved").count()
    pending_count = Projects.objects.filter(status="pending").count()  
    context = {
        'supervisor_count': supervisor_count,
        'student_count':student_count,
        'project_count':project_count,
        'approved_count':approved_count,
        'pending_count':pending_count,
    }
    return render(request, 'cordinator/cord_dashboard.html', context)



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


# View all supervisors registered
@coordinator_required
def supervisors(request):
    supervisors = Lecturer.objects.all().order_by('name')

    # Add project count to each supervisor
    for supervisor in supervisors:
        project_count = Projects.objects.filter(lecturer=supervisor).count()
        supervisor.project_count = project_count

    for i, supervisor in enumerate(supervisors):
        supervisor.index = i + 1 
    if request.method == 'POST':
        lecturer_id = request.POST.get('lecturer_id')
        if lecturer_id:
            lecturer = get_object_or_404(Lecturer, pk=lecturer_id)
            lecturer.projects_set.update(status="pending")
            lecturer.delete()
            return redirect('view_supervisors')
   
    context = {'supervisors':supervisors}
    return render(request, 'cordinator/supervisors.html', context)



# View all regoistered students
@coordinator_required
def reg_students(request):
    students = Student.objects.all().order_by('regno')
    for i, student in enumerate(students):
        student.index = i + 1 
    context = {'students':students}
    return render(request, 'cordinator/students.html', context)


# View all uploaded titles
@coordinator_required
def view_projects(request):
    projects = Projects.objects.all().order_by('-created_at')
    for i,project in enumerate(projects):
        project.index = i+1
        student = project.student
        project.reg_number = student.regno
    context = {'projects':projects}
    return render(request, 'cordinator/projects.html',context)


# pending titles
@coordinator_required
def pending_titles(request):
    projects = Projects.objects.filter(status="pending").order_by('created_at')
    for i,project in enumerate(projects):
        project.index = i+1
        student = project.student
        project.reg_number = student.regno
    context = {'projects':projects}
    return render(request, 'cordinator/pending_titles.html', context)


# Approved titles
@coordinator_required
def approved_titles(request):
    projects = Projects.objects.filter(status="Approved").order_by('-created_at')
    for i,project in enumerate(projects):
        project.index = i+1
        student = project.student
        project.reg_number = student.regno
    context = {
        'projects':projects,
        }
    return render(request, 'cordinator/approved_titles.html', context)


# View milestones
@coordinator_required
def view_milestones_cord(request):
    phases = Phases.objects.all().order_by('order')  # Get all phases in order

    context = {'phases': phases}
    return render(request, 'cordinator/milestones_cord.html', context)


# Make announcemnts view
@coordinator_required
def make_announcement(request):
    if request.method == 'POST':
        subject = request.POST['subject']
        message = request.POST['message']

        if subject and message:
            announcement = CoordinatorAnnouncements.objects.create(sender=request.user, 
                                                                   subject=subject, 
                                                                   message=message
                                                                   )
            announcement.save()
            success_message = 'Announcement Made Successfully'
            context = {'success_message':success_message}
            return render(request, 'cordinator/make_announcement.html', context)
        else:
            error_message = 'Error all fields must be filled'
            context = {'error_message':error_message}
            return render(request, 'cordinator/make_announcement.html', context)  

    else:
        return render(request, 'cordinator/make_announcement.html')


# Make announcemnts view
@coordinator_required
def upload_resource(request):
    return render(request, 'cordinator/resource.html')


# View Project details including descripton and objectives
@coordinator_required
def view_project_details(request, project_id):
    project =  get_object_or_404(Projects, pk=project_id)
    lecturer = Lecturer.objects.all()
    approved_project = Projects.objects.get(pk=project_id)

    # Updating project details
    if request.method =="POST":
        allocated_lec = request.POST['allocated_lecturer']
        comment = request.POST['comment']

        if allocated_lec:
            project.status = 'Approved'
            lecturer_obj = Lecturer.objects.get(pk=allocated_lec)
            project.lecturer = lecturer_obj
            
            project.save()

            feedback = CoordinatorFeedbacks.objects.create(sender=request.user, project=approved_project, comment=comment)
            
            feedback.save()

            messages.success(request, 'Project details updated successfully!')
            return HttpResponseRedirect(reverse('view_project_details', args=[project.id]))
        else:
           messages.error(request, 'Missing comment or allocated lecturer data.')

    context = {
        'project':project,
        'lecturer':lecturer
        }
    
    return render(request, 'cordinator/view_project.html', context)


# Create a phase
def create_phase(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        order = int(request.POST.get('order'))
        deadline_date = request.POST.get('deadline_date')  # Optional, can be blank

        # Basic validation (improve as needed)
        if not name or not description or order <= 0:
            # Handle invalid data (e.g., display error messages)
            error_message = 'Please fill all required fields and ensure order is a positive integer.'
            context = {
                'error_message':error_message
            }
            return render(request, 'cordinator/create_phase.html', context)

        # Create and save the phase
        phase = Phases.objects.create(
            name=name,
            description=description,
            order=order,
            deadline_date=deadline_date 
        )
        phase.save()

        # Redirect to success page or list of phases
        return redirect('create_phase')
    else:
        return render(request, 'cordinator/create_phase.html')  # Render the form for GET requests

