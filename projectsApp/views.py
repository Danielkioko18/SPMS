from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login,logout
from django.contrib.auth.hashers import check_password
from .AccessControl import coordinator_required, student_required,supervisor_required
from .models import Student, CoordinatorFeedbacks, CoordinatorAnnouncements, Lecturer, Projects,Notifications,Announcements, Phases, Proposal, Documents, Resources
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
# ==================================================================================================================

# Home
def Home(request):
    return render(request, 'index.html')


# Students Views here
def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        try:
            student = Student.objects.get(email=email)
            # Authenticate user against our custom User Model (Student)
            user = authenticate(email=email, password=password)
            
            if user is not None:
                auth_login(request, user)
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

    project = Projects.objects.filter(student=student).first()
    lecturer = project.lecturer

    # =============================== Coordinator and Lecturer Feedbacks Count ===================================
    lec_notifications = Notifications.objects.filter(recipient=student).count()
    cord_notifications = CoordinatorFeedbacks.objects.filter(project__student=student).count()

    # =============================== Announcemnts Count =========================================================
    lec_announcements = Announcements.objects.filter(sender=lecturer).count()
    cord_announcements = CoordinatorAnnouncements.objects.filter().count()

    # =============================== Notifications Count =========================================================
    unread_notifications = Notifications.objects.filter(recipient=student, read=False).count()
    unread_feedbacks = CoordinatorFeedbacks.objects.filter(project__student=student, read=False).count()
    total_unread = unread_notifications + unread_feedbacks

    # =============================== Totals ====================================================================
    total_notifications = lec_notifications + cord_notifications    
    total_announcements = lec_announcements + cord_announcements

    # check if project is accepted
    project_accepted = True
    if my_project.exists():
        project = my_project.first()
        if Proposal.objects.filter(project=project).exists():
            project_accepted = False
    

    context = {
        'student':student,
        'my_project':my_project,
        'total_notifications':total_notifications,
        'total_announcements':total_announcements,
        'project_accepted':project_accepted,
        'total_unread':total_unread
    }
    return render(request, 'students/student_dashboard.html', context)



# Student profile
def student_profile(request):
    user = request.user
    context = {
        'user':user
    }
    return render(request, 'students/profile.html', context)


# Change password
@student_required
def change_password(request):
    if request.method == 'POST':
        user = request.user
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_pass')

        # Check if the old password matches
        if not check_password(old_password, user.password):
            error_message = "Old password is incorrect"
            return render(request, 'students/profile.html', {'error_message': error_message})

        # Check if the new password and confirm password match
        if new_password != confirm_password:
            error_message = "New passwords do not match"
            return render(request, 'students/profile.html', {'error_message': error_message})

        # Hash the new password
        user.password = make_password(new_password)
        user.save()

        success_message = "Password changed successfully"
        return render(request, 'students/profile.html', {'success_message': success_message})

    return redirect('student_profile')



# Change details
@student_required
def update_details(request):
    if request.method == 'POST':
        user = request.user

        user.regno = request.POST.get('regno')
        user.email = request.POST.get('email')
        user.phone_number = request.POST.get('phone')
        user.intake_year = request.POST.get('intake_yr')
        user.name = request.POST.get('names')

        # Save the updated user details
        user.save()

        success_message = "Details updated successfully"
        context = {
            'success_message':success_message
        }
        return render(request, 'students/profile.html', context)

    return redirect('student_profile')



# upload project title
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



# my title
@student_required
def revise_title(request):
    project = Projects.objects.filter(student=request.user).first()
    if not project:
        error_message = 'You have not uploaded any project yet'
        context = {'error_message': error_message}
        return render(request, 'students/upload_title.html', context)

    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        objectives = request.POST['objectives']

        project.title = title
        project.description = description
        project.objectives = objectives
        project.save()
        return redirect('student_dashboard')

    else:
        context = {'project': project}
        return render(request, 'students/revise_title.html', context)


# view phases
@student_required
def my_uploads(request):
    student = request.user
    phases = Phases.objects.all().order_by('order')

    for phase in phases:
        phase.documents.set(Documents.objects.filter(phase=phase, student=student).order_by('-uploaded_at'))
        phase.approved_documents_exist = Documents.objects.filter(phase=phase, student=student, status='approved').exists()

    context = {'phases': phases}
    return render(request, 'students/view_phases.html', context)


 # Restrict uploads to PDF files
'''if not file.name.lower().endswith('.pdf'):
                raise ValidationError("Only PDF files are allowed.")'''


# Upload project details to the portal
def upload_file(request):
    student = request.user
    proposal = get_object_or_404(Proposal, student=student)

    #
    if request.method == 'POST':
      # Access uploaded file and explanation from request.POST and request.FILES
      document_file = request.FILES.get('document_file')
      explanation = request.POST.get('explanation')
      selected_phase_id = request.POST.get('phase') 

      if document_file:
        try:
            # Retrieve the selected phase object
            phase = Phases.objects.get(pk=selected_phase_id)

            '''# Check if any document from the previous phase is approved
            previous_phase = phase.get_previous_phase()
            if previous_phase and not Documents.objects.filter(phase=previous_phase, student=student, status='approved').exists():
                return HttpResponseBadRequest("You must complete the previous phase first.")'''

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
    # Get the current student
    current_student = request.user

    # Fetch the proposal of the current student
    project = Projects.objects.filter(student=current_student).first()
    lecturer = project.lecturer

    # Fetch announcements from the lecturer associated with the proposal
    if project:
        lecturer_announcements = Announcements.objects.filter(sender=lecturer)
        # Update Announcements to read
        for announcement in lecturer_announcements:
            announcement.read = True
            announcement.save()
    else:
        lecturer_announcements = Announcements.objects.none() 

    

    # Fetch announcements from the coordinator
    coordinator_announcements = CoordinatorAnnouncements.objects.all().order_by('-created_at')
    # Update Announcements to read
    for announcement in coordinator_announcements:
            announcement.read = True
            announcement.save()

    context = {
        'lecturer_announcements': lecturer_announcements,
        'coordinator_announcements': coordinator_announcements,
    }
    return render(request, 'students/announcements.html', context)


@student_required
def notifications(request):
    student = request.user
    notifications = Notifications.objects.filter(recipient=student).order_by('-created_at')

    # Fetch coordinator feedbacks
    coordinator_feedbacks = CoordinatorFeedbacks.objects.filter(project__student=student).order_by('-created_at')


    # Mark notifications as read
    for notification in notifications:
        notification.read = True
        notification.save()

    # Mark feedback as read
    for feedback in coordinator_feedbacks:
        feedback.read = True
        feedback.save()

    context = {
        'notifications':notifications,
        'coordinator_feedbacks':coordinator_feedbacks
        }

    return render(request, 'students/notifications.html', context)


@student_required
def resources(request):
    # Fetch all resources, arranged by latest upload first
    resources = Resources.objects.all().order_by('-uploaded_at')

    context = {'resources': resources}

    return render(request, 'students/resources.html', context)


# =================================================================================================================

# Supervisors views
def supervisor_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(email=email, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('supervisor_dashboard')
        else:
            error_message = "Invalid Email or Password"            
            return render(request, 'acounts/super_login.html', {'error_message': error_message})        
    else:
        return render(request, 'acounts/super_login.html')


# supervisor profile
def supervisor_profile(request):
    current_user = request.user

    context = {
        'current_user':current_user
    }

    return render(request, 'supervisors/profile.html', context)



# Change password
@supervisor_required
def lec_change_password(request):
    if request.method == 'POST':
        user = request.user
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_pass')

        # Check if the old password matches
        if not check_password(old_password, user.password):
            error_message = "Old password is incorrect"
            context = {
                'error_message':error_message
            }
            return render(request, 'supervisors/profile.html', context)

        # Check if the new password and confirm password match
        if new_password != confirm_password:
            error_message = "New passwords do not match"
            context = {
                'error_message':error_message
            }
            return render(request, 'supervisors/profile.html', context)

        # Hash the new password
        user.password = make_password(new_password)
        user.save()

        success_message = "Password changed successfully"
        context = {
            'success_message': success_message
        }
        return render(request, 'supervisors/profile.html', context)

    return redirect('supervisor_profile')


# Change details
@supervisor_required
def lec_update_details(request):
    if request.method == 'POST':
        user = request.user

        # update details
        user.email = request.POST.get('email')
        user.phone_number = request.POST.get('phone')
        user.name = request.POST.get('names')

        # Save the updated user details
        user.save()

        success_message = "Details updated successfully"
        context = {
            'success_message':success_message
        }
        return render(request, 'supervisors/profile.html', context)

    return redirect('supervisor_profile')



# supervisor dashboard
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


# supervisor mystudents
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
    if request.method == 'POST':
        # Extract data from the POST request
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        resource_file = request.FILES.get('resource_file')

        # cupturing messages for user
        context = {}
        

        # Print uploaded file for debugging
        print(f"Uploaded file: {resource_file}")

        # Create a new resource instance and save it
        if resource_file:
            try:
                resource = Resources(
                    subject=subject,
                    file=resource_file,
                    message=message,
                    uploaded_at=timezone.now()
                )
                resource.save()
                
                # Redirect to resource list page or any other appropriate URL
                return redirect(request.path)
            except Exception as e:
                error_message = f'Error Uploading Document: {e}'
                return render(request, 'supervisors/upload_resource.html', {'error_message':error_message})
        else:
            # Error message
            error_message = 'Error: No file received. Please choose a file'
            print("Error: No file received. Please choose a file")
            return render(request, 'supervisors/upload_resource.html', {'error_message':error_message})

    return render(request, 'supervisors/upload_resource.html')



@supervisor_required
def milestones(request):
    phases = Phases.objects.all().order_by('order')  # Get all phases in order
    lecturer = request.user  # Get the logged-in user (lecturer)
    phase_proposals = []
    for phase in phases:
        proposals = Proposal.objects.filter(lecturer=lecturer, current_phase=phase)
        documents = Documents.objects.filter(phase=phase)
        phase_proposals.append({'phase': phase, 'proposals': proposals, 'documents':documents})
        #print(phase_proposals)
    context = {'phase_proposals': phase_proposals}
    
    return render(request, 'supervisors/milestones.html', context)


# View uploads

@supervisor_required
def view_student_uploads(request, phase_id, student_id):
    phase = get_object_or_404(Phases, pk=phase_id)
    student = get_object_or_404(Student, pk=student_id)
    documents = Documents.objects.filter(phase=phase, student=student).order_by('-uploaded_at')
    

    current_user = request.user
    
    if request.method == 'POST':
        comment = request.POST['reason']
        if comment:
            notification = Notifications.objects.create(
                sender=current_user, 
                recipient=student, 
                message=comment
            )
            notification.save()
        
        
        for document in documents:
            document.status = "revision_requested"
            document.save()

        return redirect(request.path)  # Redirect to some appropriate URL

    context = {'phase': phase, 'student': student, 'documents': documents}
    return render(request, 'supervisors/view_student_uploads.html', context)

# approve upload
def approve_document(request):
    if request.method == 'POST':
        # Get the document ID from the form
        document_id = request.POST.get('document_id')
        # Update status to "approved" for the specific document
        document = get_object_or_404(Documents, pk=document_id)
        document.status = "approved"
        document.save()

        proposal = document.proposal
        proposal.move_to_next_phase()
        proposal.check_completion()

        # Redirect back to the previous page
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    return redirect(request.path)



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

    context = {'project':project}
    
    return render(request, 'supervisors/project_details.html', context)

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

# ============================================= End Supervisor views ===============================================


# ============================================= Coordinator's views ================================================

# coordinator login
def cordinator_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        coordinator = authenticate(email=email, password=password)
        if coordinator is not None:
            if coordinator.is_staff:
                auth_login(request, coordinator)
                return redirect('cordinator_dashboard')                
            else:
                 return render(request, 'acounts/cord_login.html', {'error_message': "You are not authorized to access this page."})
        else:
             return render(request, 'acounts/cord_login.html', {'error_message': "Invalid Email or Password."})
    else:
        return render(request, 'acounts/cord_login.html')



# Coordinator Profile
def coordinator_profile(request):
    user = request.user
    context = {
        'user':user
    }
    return render(request, 'cordinator/profile.html', context)




# coordinator dashboard
@coordinator_required
def cordinator_dashboard(request):
    supervisor_count = Lecturer.objects.all().count()
    student_count = Student.objects.all().count()
    project_count = Projects.objects.all().count()
    approved_count = Projects.objects.filter(status="Approved").count()
    pending_count = Projects.objects.filter(status="pending").count()
    complete_count = Proposal.objects.filter(completed=True).count()
    active_count = Proposal.objects.filter(completed=False).count() 
    phase_count = Phases.objects.all().count()
    
    context = {
        'supervisor_count': supervisor_count,
        'student_count':student_count,
        'project_count':project_count,
        'approved_count':approved_count,
        'pending_count':pending_count,
        'complete_count':complete_count,
        'phase_count':phase_count,
        'active_count':active_count,
    }
    return render(request, 'cordinator/cord_dashboard.html', context)



# add supervisor
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



# update supervisor
@coordinator_required
def edit_lecturer(request, lecturer_id):
    lecturer = get_object_or_404(Lecturer, pk=lecturer_id)

    if request.method == 'POST':
        lecturer.email = request.POST.get('email')
        lecturer.name = request.POST.get('name')
        lecturer.phone = request.POST.get('phone')
        # Note: You should hash the password before saving it
        lecturer.password = request.POST.get('password')
        lecturer.save()
        return redirect('view_supervisors')

    context = {'lecturer': lecturer}
    return render(request, 'cordinator/edit_lecturer.html', context)



# View all supervisors registered
@coordinator_required
def supervisors(request):
    supervisors = Lecturer.objects.all().order_by('name')

    # Add project count to each supervisor
    for supervisor in supervisors:
        project_count = Projects.objects.filter(lecturer=supervisor).count()
        supervisor.project_count = project_count
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



# View phases/milestones with students
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
    if request.method == 'POST':
        # Extract data from the POST request
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        resource_file = request.FILES.get('resource_file')

        # cupturing messages for user
        context = {}
        

        # Print uploaded file for debugging
        print(f"Uploaded file: {resource_file}")

        # Create a new resource instance and save it
        if resource_file:
            try:
                resource = Resources(
                    subject=subject,
                    file=resource_file,
                    message=message,
                    uploaded_at=timezone.now()
                )
                resource.save()
                
                # Redirect to resource list page or any other appropriate URL
                return redirect(request.path)
            except Exception as e:
                error_message = f'Error Uploading Document: {e}'
                print(f"Error uploading document: {e}")
                return render(request, 'cordinator/resource.html', {'error_message':error_message})
        else:
            # Error message
            error_message = 'Error: No file received. Please choose a file'
            print("Error: No file received. Please choose a file to upload")
            return render(request, 'cordinator/resource.html', {'error_message':error_message})

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



# View phase details
@coordinator_required
def view_phases(request):
    phases = Phases.objects.all().order_by('order')

    # delete phase
    if request.method == 'POST':
        phase_id = request.POST.get('phase_id')
        if phase_id:
            phase = get_object_or_404(Phases, pk=phase_id)
            phase.delete()
            return redirect(request.path)
   
    context = {'phases':phases}
    return render(request, 'cordinator/view_phases.html', context)



# edit phase
@coordinator_required
def edit_phase(request, phase_id):
    phase = get_object_or_404(Phases, pk=phase_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        order = request.POST.get('order')
        deadline_date = request.POST.get('deadline_date')

        phase.name = name
        phase.description = description
        phase.order = order
        phase.deadline_date = deadline_date
        phase.save()

        return redirect('view_phases')

    context = {'phase': phase}
    return render(request, 'cordinator/edit_phase.html', context)