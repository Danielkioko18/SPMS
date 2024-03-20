from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.Home, name='home'),
    path('student/login/', views.login, name='login'),
    path('student/signup/', views.SignUp, name='signup'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/upload_title/', views.upload_title, name='upload_title'),
    path('student/revise_title/', views.revise_title, name='revise_title'),
    path('student/milestones/', views.my_uploads, name='my_phases'),
    path('student/milestones/upload/', views.upload_file, name='upload_file'),
    path('student/announcements/', views.announcements, name='announcements'),
    path('student/notifications/', views.notifications, name='notifications'),
    path('student/uploads/resources/', views.resources, name='resources'),
    path('student/my_profile/', views.student_profile, name='student_profile'),
    


    path('supervisor/', views.supervisor_login, name='supervisor_login'),
    path('supervisor/dashboard/', views.supervisor_dashboard, name='supervisor_dashboard'),
    path('supervisor/mystundents/', views.mystudents, name='mystudents'),
    path('supervisor/project/details/<int:project_id>/', views.project_details, name='student_project'),
    path('supervisor/project/accept_title/<int:project_id>/', views.accept_title, name='accept_title'),
    path('supervisor/make_announcement/', views.announcemnt, name='announcement'),
    path('supervisor/resources/upload/', views.lec_resource, name='resource_upload'),
    path('supervisor/milestones/', views.milestones, name='milestones'),
    path('supervisor/student/uploads/<str:phase_id>/<int:student_id>/', views.view_student_uploads, name='view_student_upload'),
    path('supervisor/student/uploads/approve_document/', views.approve_document, name='approve_document'),
    path('supervisor/my_profile/', views.supervisor_profile, name='supervisor_profile'),



    path('coordinator/', views.cordinator_login, name='cordinator_login'),
    path('coordinator/dashboard/', views.cordinator_dashboard, name='cordinator_dashboard'),
    path('coordinator/supervisors/add/', views.add_supervisor, name='add_supervisor'),
    path('coordinator/supervisors/', views.supervisors, name='view_supervisors'),
     path('coordinator/supervisors/<int:lecturer_id>/edit/', views.edit_lecturer, name='edit_lecturer'),
    path('registered_students/', views.reg_students, name='registered_students'),
    path('coordinator/view_projects/', views.view_projects, name='view_projects'),
    path('projects/pending/', views.pending_titles, name='pending_titles'),
    path('projects/approved/', views.approved_titles, name='approved_titles'),
    path('projects/miletones/', views.view_milestones_cord, name='view_milestones'),
    path('coordinator/upload/resource/', views.upload_resource, name='upload_resource'),
    path('cordinator/make announcement/', views.make_announcement, name='make_announcement'),
    path('projects/view/details/<int:project_id>/', views.view_project_details, name='view_project_details'),
    path('coordinator/phases/create/', views.create_phase, name='create_phase'),
    path('coordinator/phases/', views.view_phases, name='view_phases'),
    path('coordinator/phases/<int:phase_id>/edit/', views.edit_phase, name='edit_phase'),
    path('coordinator/my_profile', views.coordinator_profile, name='coordinator_profile'),

    path('logout/', views.logout_view, name='logout'),
]

# uploads url#
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)