from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login,logout
from django.contrib.auth.hashers import check_password
from django.contrib.auth.views import PasswordResetView
from .AccessControl import coordinator_required, student_required,supervisor_required
from .models import Student, CoordinatorFeedbacks, CoordinatorAnnouncements, Lecturer, Projects,Notifications,Announcements, Phases, Proposal, Documents, Resources, RegistrationSettings
from django.http import HttpResponseBadRequest
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.utils import timezone
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.urls import reverse_lazy
from .mail_service import send_email
from django.db import IntegrityError
import random
import string
import os
# ==================================================================================================================

# Home
def Home(request):
    return render(request, 'index.html')


def password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        student = Student.objects.filter(email=email).first()

        if student:
            # Generate random 6-digit verification code
            verification_code = ''.join(random.choices(string.digits, k=6))

            # Send verification code to student's email
            subject = "Password Reset Verification Code"
            message = f"Your verification code is: {verification_code}"
            send_email(student.email, subject, message)

            # Store verification code in session
            request.session['verification_code'] = verification_code
            request.session['email'] = email

            return redirect('verify_code')

    return render(request, 'acounts/password_reset.html', {'step': 'send_verification_code'})

def verify_verification_code(request):
    if request.method == 'POST':
        verification_code = request.POST.get('verification_code')
        stored_verification_code = request.session.get('verification_code')

        if verification_code == stored_verification_code:
            # Verification code is correct
            return redirect('reset_password')

    return render(request, 'acounts/password_reset.html', {'step': 'enter_verification_code'})

def reset_password(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password1')
        email = request.session.get('email')
        student = Student.objects.filter(email=email).first()

        # Check if password is at least 8 characters long
        if len(new_password) < 8:
            error_message = "Your password should be at least 8 characters long"
            return render(request, 'acounts/change_password.html', {'error_message': error_message})

        
        if student:
            # Update the student's password
            student.password = new_password
            student.save()

            # Clear session data
            del request.session['verification_code']
            del request.session['email']

            return redirect('login')

    return render(request, 'acounts/change_password.html')

# Student signup/Registration
def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        try:
            student = Student.objects.get(email=email)
            # Authenticate Student
            user = authenticate(email=email, password=password)
            
            if user is not None:
                auth_login(request, user)
                # Update last login time
                student.last_login = timezone.now()
                student.save()
                
                return redirect('student_dashboard')
            
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
    # get year set for registration
    registration_settings = RegistrationSettings.objects.first()
    year = registration_settings.allowed_year
    context = {'year':year}

    #form submission
    if request.method == 'POST':
        
        regno = request.POST['regno']
        email = request.POST['email']
        name = request.POST['names']
        phone_number = request.POST['phone']
        intake_year = int(request.POST['intake_yr'])
        password = request.POST['password']
        confirm_pass = request.POST['confirm_pass']
        
        # Check if registration is active
        if registration_settings.open == False:
            error_message = 'Sorry Registrations are currently closed. Try again Later.'
            return render(request, 'acounts/signup.html', {'error_message': error_message})

        if intake_year > registration_settings.allowed_year:
            # Display not eligible message
            error_message = f"You are not eligible to register for the selected intake year. Allowed intake year: {registration_settings.allowed_year} or earlier."
            return render(request, 'acounts/signup.html', {'error_message': error_message})
        
        # Check if registration number is unique
        if Student.objects.filter(regno=regno).exists():
            error_message = "This registration number is already registered."
            return render(request, 'acounts/signup.html', {'error_message': error_message})

        # Check if email is unique
        if Student.objects.filter(email=email).exists():
            error_message = "This Email is already registered."
            return render(request, 'acounts/signup.html', {'error_message': error_message})

        # Check if passwords match
        if password != confirm_pass:
            error_message = "Passwords do not match"
            return render(request, 'acounts/signup.html', {'error_message': error_message})

        # Check if password is at least 8 characters long
        if len(password) < 8:
            error_message = "Your password should be at least 8 characters long"
            return render(request, 'acounts/signup.html', {'error_message': error_message})

        # Hash password
        hashed_password = make_password(password)

        # Create new student object
        student = Student(regno=regno, email=email, name=name, phone_number=phone_number, intake_year=intake_year, password=hashed_password)

        # Save student object to database
        student.save()

        success_message = "Registration successful. Please login to continue."
        return render(request, 'acounts/signup.html', {'success_message': success_message})

    return render(request, 'acounts/signup.html', context)




@student_required
def student_dashboard(request):
    student = request.user
    my_project = Projects.objects.filter(student=student)
    project = my_project.first()  # Get the first project if it exists

    if project:
        lecturer = project.lecturer
    else:
        lecturer = None  # Set lecturer to None if there are no projects

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

    # =============================== Phases ====================================================================
    phases = Phases.objects.all()

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
        'total_unread':total_unread,
        'phases':phases
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

        # Check if password is at least 8 characters long
        if len(new_password) < 8:
            error_message = "Your password should be at least 8 characters long"
            return render(request, 'students/profile.html', {'error_message': error_message})

        # Check if the new password and confirm password match
        if new_password != confirm_password:
            error_message = "New passwords do not match"
            return render(request, 'students/profile.html', {'error_message': error_message})

        # Hash the new password
        user.password = make_password(new_password)
        user.save()

        return redirect('student_profile')

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

        return redirect('student_profile')

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
            context = {
                'error_message':error_message
                }
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
        project.status = "Pending"
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



# Upload project details to the portal
@student_required
def upload_file(request):
    student = request.user
    proposal = get_object_or_404(Proposal, student=student)
    error = None

    if request.method == 'POST':
        # Access uploaded file and explanation from request.POST and request.FILES
        document_file = request.FILES.get('document_file')
        explanation = request.POST.get('explanation')
        selected_phase_id = request.POST.get('phase')

        if document_file:
            if document_file.name.endswith('.pdf'):
                try:
                    # Retrieve the selected phase object
                    phase = Phases.objects.get(pk=selected_phase_id)

                    # Create a new Documents object and save it
                    document = Documents(
                        student=request.user,
                        proposal=proposal,
                        phase=phase,
                        file=document_file,
                        comment=explanation
                    )
                    document.save()
                    return redirect('my_phases')
                except Exception as e:
                    error = f"Error uploading document: {e}"
            else:
                error = "Error: Only PDF files are allowed. Please choose a PDF file to upload"
                return HttpResponseBadRequest("Error: Only PDF files are allowed. Please choose a PDF file to upload")
        else:
            error = "Error: No document file uploaded"

    context = {'proposal': proposal, 'student': student, 'error': error}
    return render(request, 'students/view_phases.html', context)  # Redirect to document list view


# anouncements
@student_required
def announcements(request):
    # Get the current student
    current_student = request.user

    # Fetch the proposal of the current student
    project = Projects.objects.filter(student=current_student).first()
    if project:
        lecturer = project.lecturer
    else:
        lecturer = None

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


# ======================================================== Supervisors views =========================================================

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

        # Check if password is at least 8 characters long
        if len(new_password) < 8:
            error_message = "Your password should be at least 8 characters long"
            context = {
                'error_message':error_message
            }
            return render(request, 'supervisors/profile.html', context)

        # Hash the new password
        user.password = make_password(new_password)
        user.save()

        return redirect('supervisor_profile')

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

        return redirect('supervisor_profile')

    return redirect('supervisor_profile')


# supervisor dashboard
@supervisor_required
def supervisor_dashboard(request):
    current_user = request.user

    project_count = Projects.objects.filter(lecturer = current_user).count()
    announcement_count = Announcements.objects.filter(sender=current_user).count()

    phases = Phases.objects.all()

    context = {
        'project_count':project_count,
        'announcement_count':announcement_count,
        'phases':phases
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


# Supervisor upload resource
@supervisor_required
def lec_resource(request):
    error_message = None

    if request.method == 'POST':
        # Extract data from the POST request
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        resource_file = request.FILES.get('resource_file')

        if resource_file:
            if resource_file.name.endswith('.pdf'):
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
            else:
                error_message = 'Error: Only PDF files are allowed. Please choose a PDF file'
        else:
            error_message = 'Error: No file received. Please choose a file'

    context = {'error_message': error_message}
    return render(request, 'supervisors/upload_resource.html', context)


# supervisor phases
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


'''# View pdf files by supervisor
def view_pdf(request, file_id):
    document = get_object_or_404(Documents, id=file_id)
    file_path = os.path.join(settings.MEDIA_ROOT, document.file.name)  # Adjust based on how file paths are stored
    
    with open(file_path, 'rb') as pdf_file:
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="{}"'.format(document.file.name)
        return response'''
    


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
@supervisor_required
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
@coordinator_required
def coordinator_profile(request):
    user = request.user
    context = {
        'user':user
    }
    return render(request, 'cordinator/profile.html', context)


# Student registration settings
@coordinator_required
def registration_settings(request):
    settings = RegistrationSettings.objects.first()
    context = {
        'settings':settings
        }
    return render(request, 'cordinator/registration_settings.html', context)


# Update the registration settings
@coordinator_required
def update_registration_settings(request):
    # Retrieve existing settings object if it exists, otherwise create a new one
    settings = RegistrationSettings.objects.first()
    if settings is None:
        settings = RegistrationSettings()
        # Set default year to the current year
        settings.allowed_year = timezone.now().year

    if request.method == 'POST':
        registration_open = request.POST.get('registration_open')
        allowed_intake_year = request.POST.get('allowed_intake_year')

        settings.open = bool(registration_open)
        settings.allowed_year = int(allowed_intake_year)
        # Save the settings object
        settings.save()

    # Redirect or render a response
    return redirect('registration_settings')



# Dispatch students
def dispatch_students(request):
    if request.method == 'GET':
        try:
            # Retrieve all students
            students = Student.objects.all()
            # Iterate over each student and perform dispatch
            for student in students:
                # Remove all associated records                
                student.projects_set.all().delete()
                student.proposals.all().delete()
                student.documents.all().delete()
                student.notifications.all().delete()

            Student.objects.all().delete()
            CoordinatorFeedbacks.objects.all().delete()
            Resources.objects.all().delete()
            Announcements.objects.all().delete()
            CoordinatorAnnouncements.objects.all().delete()

            # Redirect back to the registration settings page after dispatching
            messages.success(request, 'All students have been dispatched successfully.')
            return redirect('registration_settings')
        except IntegrityError as e:
            # Handle IntegrityError (database integrity constraint violations)
            messages.error(request, f'An error occurred during deletion: {e}')
            return redirect('registration_settings')
    else:
        # Handle other HTTP methods appropriately
        return redirect('registration_settings')



# change password
@coordinator_required
def coordinator_change_password(request):
    if request.method == 'POST':
        user = request.user
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_pass = request.POST.get('confirm_pass')

        # Check if old password matches
        if not user.check_password(old_password):
            error_message = "Old password is incorrect"
            context = {
                'error_message': error_message
            }
            return render(request, 'cordinator/profile.html', context)

        # Check if new password matches the confirmation
        if new_password != confirm_pass:
            error_message = "New password and confirmation do not match"
            context ={
                'error_message':error_message
            }
            return render(request, 'cordinator/profile.html', context)

        # Check if password is at least 8 characters long
        if len(new_password) < 8:
            error_message = "Your password should be at least 8 characters long"
            context ={
                'error_message':error_message
            }            
            return render(request, 'acounts/signup.html', context)


        # Update password
        user.password = make_password(new_password)
        user.save()

        success_message = "Password changed successfully"
        context ={
                'success_message': success_message
            } 
        return render(request, 'cordinator/profile.html', context)

    return render(request, 'cordinator/profile.html')



# update details
@coordinator_required
def coordinator_update_details(request):
    if request.method == 'POST':
        user = request.user
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')

        # Save the updated user details
        user.save()

        success_message = "Details updated successfully"
        return render(request, 'cordinator/profile.html', {'success_message': success_message})

    return render(request, 'cordinator/profile.html')



# coordinator dashboard
@coordinator_required
def cordinator_dashboard(request):
    supervisor_count = Lecturer.objects.all().count()
    student_count = Student.objects.all().count()
    project_count = Projects.objects.all().count()
    approved_count = Projects.objects.filter(status="Approved").count()
    pending_count = Projects.objects.filter(status="Pending").count()
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
        password = 'spmssupervisor'

        # Hash password
        hashed_password = make_password(password)

        # Create new student object
        lecturer = Lecturer(email=email, name=name, phone=phone_number, password=hashed_password)

        # Save student object to database
        lecturer.save()


        # Send registration email to the lecturer
        recipient_email = email  # Lecturer's email address
        subject = 'Welcome to SPMS'
        message = f"""
                    <html>
                        <body>
                            <p>Hello, <strong>{name}</strong>, you have been registered as a supervisor on the SPMS system.</p>
                            <p>Your password is <strong><span style="color:red;">{password}</span></strong>. Please login to the system and change your password to your most convenient one.</p>
                            <p>Thank you.</p>
                        </body>
                    </html>"""
                
        
        # Send the email
        send_email(recipient_email, subject, message)


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


# Reset supervisor passwords to defaault
@coordinator_required
def sup_reset_password(request):
    if request.method == 'POST':
        lecturer_id = request.POST.get('lecturer_id')
        # Retrieve the lecturer object based on the ID
        lecturer = Lecturer.objects.get(pk=lecturer_id)

        password = 'spmssupervisor'
        new_password = make_password(password)

        # Reset the password to the default one
        lecturer.password = new_password
        lecturer.save()

        # Redirect back to the page where you display the list of lecturers
        return redirect('view_supervisors')

    # If the request method is not POST, handle accordingly
    return redirect('view_supervisors')




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
    
    context = {
        'projects':projects
        }
    return render(request, 'cordinator/projects.html',context)



# pending titles
@coordinator_required
def pending_titles(request):
    projects = Projects.objects.filter(status="Pending").order_by('created_at')
    
    context = {
        'projects':projects
        }
    return render(request, 'cordinator/pending_titles.html', context)



# Approved titles
@coordinator_required
def approved_titles(request):
    projects = Projects.objects.filter(status="Approved").order_by('student')
    
    context = {
        'projects':projects,
        }
    return render(request, 'cordinator/approved_titles.html', context)


# Approved titles
@coordinator_required
def rejected_titles(request):
    projects = Projects.objects.filter(status="Rejected").order_by('-created_at')

    context = {
        'projects':projects,
        }
    return render(request, 'cordinator/rejected_titles.html', context)

# Completed projects
def completed_projects(request):
    projects = Proposal.objects.filter(completed=True).order_by('id')

    context = {
        'projects':projects,
        }
    return render(request, 'cordinator/complete_projects.html', context)


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



# Make announcements view
@coordinator_required
def upload_resource(request):
    if request.method == 'POST':
        # Extract data from the POST request
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        resource_file = request.FILES.get('resource_file')

        # Check if the uploaded file is a PDF
        if resource_file:
            if resource_file.name.endswith('.pdf'):
                # Create a new resource instance and save it
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
                    return render(request, 'cordinator/resource.html', {'error_message': error_message})
            else:
                # Error message for invalid file type
                error_message = 'Error: Only PDF files are allowed. Please choose a PDF file to upload'
                print("Error: Only PDF files are allowed. Please choose a PDF file to upload")
                return render(request, 'cordinator/resource.html', {'error_message': error_message})
        else:
            # Error message for no file received
            error_message = 'Error: No file received. Please choose a file'
            print("Error: No file received. Please choose a file to upload")
            return render(request, 'cordinator/resource.html', {'error_message': error_message})

    return render(request, 'cordinator/resource.html')


# View Project details including descripton and objectives
@coordinator_required
def view_project_details(request, project_id):
    project =  get_object_or_404(Projects, pk=project_id)
    lecturer = Lecturer.objects.all()

    context = {
        'project':project,
        'lecturer':lecturer
        }
    
    return render(request, 'cordinator/view_project.html', context)


# Approve title
@coordinator_required
def approve_title(request, project_id):
    project = get_object_or_404(Projects, pk=project_id)
    if request.method == "POST":
        allocated_lec = request.POST.get('allocated_lecturer')
        comment = request.POST.get('comment')

        if allocated_lec:
            project.status = 'Approved'
            lecturer_obj = Lecturer.objects.get(pk=allocated_lec)
            project.lecturer = lecturer_obj
            project.save()

            feedback = CoordinatorFeedbacks.objects.create(sender=request.user, project=project, comment=comment)
            feedback.save()

            # Send approval email to the student
            name = project.student.name
            supervisor = lecturer_obj.name
            recipient_email = project.student.email
            subject = 'Project Title Approval'
            message = f"""
                        <html>
                            <body>
                                <p>Hello, <strong>{name}</strong>, Cogratulations, your project title has been approved.</p>
                                <p>Your Supervisor is <strong>{supervisor}</strong>. Please wait for the supervisor feedback on whether to revise your title details or proceed to phase 1 of the projects.</p>
                                <p>You will be notified about this on the systems notifications when you login.</p>
                                <p>Thank you.</p>
                            </body>
                        </html>
                        """
            
            # Send the email
            send_email(recipient_email, subject, message)


            messages.success(request, 'Project approved successfully!')
            return HttpResponseRedirect(reverse('view_project_details', args=[project.id]))
        else:
            messages.error(request, 'Please select a lecturer for allocation.')

    return render(request, 'cordinator/view_project.html', {'project': project})



# reject title
@coordinator_required
def reject_title(request, project_id):
    project = get_object_or_404(Projects, pk=project_id)
    if request.method == "POST":
        reason = request.POST.get('reason')

        if reason:
            # Update project status to 'Rejected' and save the reason
            project.status = 'Rejected'
            project.save()

            feedback = CoordinatorFeedbacks.objects.create(sender=request.user, project=project, comment=reason)
            feedback.save()


            # Send email email to the student
            name = project.student.name
            recipient_email = project.student.email
            subject = 'Project Title Approval'
            message = f"""
                        <html>
                            <body>
                                <p>Dear, <strong>{name}</strong>,your project title has been declined by the projects coordinator.</p>
                                <p><strong>Reason: </strong><b style="color:red;">{reason}</b></p>
                                <p>Please consider revising your title for approval</p>
                                <p>Thank you.</p>
                            </body>
                        </html>
                        """
            
            # Send the email
            send_email(recipient_email, subject, message)

            messages.success(request, 'Project rejected successfully!')
            return HttpResponseRedirect(reverse('view_project_details', args=[project.id]))
        else:
            messages.error(request, 'Please provide a reason for rejection.')

    return render(request, 'cordinator/view_project.html', {'project': project})



# Create a phase
@coordinator_required
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
            return render(request, 'cordinator/add_phase.html', context)

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
        return render(request, 'cordinator/add_phase.html')  # Render the form for GET requests



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