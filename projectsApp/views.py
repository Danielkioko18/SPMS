from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login,logout
from .AccessControl import coordinator_required, student_required,supervisor_required
from .models import Student, CoordinatorFeedbacks, CoordinatorAnnouncements, Lecturer, Projects,Notifications,Announcements, Phases, Proposal, Documents
from django.core.exceptions import ValidationError
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
    phases = Phases.objects.all().order_by('order')

    # Get the phase if a specific phase is requested, otherwise default to the first phase
    phase_id = request.GET.get('phase_id')
    if phase_id:
        try:
            phase = Phases.objects.get(id=phase_id)
        except Phases.DoesNotExist:
            # Handle the case where the requested phase doesn't exist
            phase = phases[0]  # Redirect to the first phase if the requested one is not found
    else:
        phase = phases[0]  # Set to the first phase if no phase is specified

    # Retrieve documents for the selected phase belonging to the logged-in student
    documents = Documents.objects.filter(phase=phase, student=student)

    context = {'phases': phases, 'phase': phase, 'documents': documents}
    return render(request, 'students/view_phases.html', context)


 # Restrict uploads to PDF files
'''if not file.name.lower().endswith('.pdf'):
                raise ValidationError("Only PDF files are allowed.")'''


# Upload project details to the portal
def upload_file(request):
    student = request.user
    proposal = student.proposal_set.get()
    print("explanation: ", proposal)
    print(student)


    if request.method == 'POST':
      # Access uploaded file and explanation from request.POST and request.FILES
      document_file = request.FILES.get('document_file')
      explanation = request.POST.get('explanation')
      selected_phase_id = request.POST.get('phase') 

      if document_file:
        try:
          # Retrieve the selected phase object
          phase = Phases.objects.get(pk=selected_phase_id)

          # Create a new Documents object and save it
          document = Documents(
            student=request.user,
            proposal=proposal,
            phase = phase,
            file=document_file,
            comment=explanation
          )
          document.save()
          return redirect('my_phases')  # Redirect to document list view after successful upload
        except Exception as e:
          print(f"Error uploading document: {e}")
          # Handle the error (e.g., display an error message to the user)
      else:
          print("No document file uploaded")   # Handle the case where no file was uploaded

    context = {'proposal': proposal, 'student':student}
    return render(request, 'students/view_phases.html', context)  # Redirect to document list view


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
    lecturer = request.user  # Get the logged-in user (lecturer)
    phase_proposals = []
    for phase in phases:
        proposals = Proposal.objects.filter(lecturer=lecturer, current_phase=phase)
        phase_proposals.append({'phase': phase, 'proposals': proposals})
    context = {'phase_proposals': phase_proposals}
    return render(request, 'supervisors/milestones.html', context)

# Accept title
def accept_title(request, project_id):
    project = get_object_or_404(Projects, pk=project_id)

    # Check if proposal already exists for the project
    proposal = Proposal.objects.filter(project=project).first()

    if not proposal:
        
        proposal = Proposal.objects.create(
            student=project.student, # Assuming student is linked to project
            title=project.title,
            lecturer=project.lecturer,  # Assuming supervisor is linked to project
            project=project,
        )
    # Assign the first phase to the proposal
    first_phase = Phases.objects.order_by('order').first()  # Get the first phase
    proposal.current_phase = first_phase
    proposal.save()

    return redirect('student_project', project_id=project_id)  # Redirect to project details

# View uploads

@supervisor_required
def view_student_uploads(request):
    return render(request, 'supervisors/milestones.html')


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

