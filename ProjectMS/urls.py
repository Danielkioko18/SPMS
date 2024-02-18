from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.Home, name='home'),
    path('signup/', views.SignUp, name='signup'),
    path('student_dashboard/', views.student_dashboard, name='studne_dashboard'),
    path('upload_title/', views.upload_title, name='upload_title'),
    path('milestones/', views.upload_file, name='upload_file'),
    path('announcements/', views.announcements, name='announcements'),
    path('notifications/', views.notifications, name='notifications'),
    path('resources/', views.resources, name='resources'),


    path('supervisor/dashboard/', views.supervisor_dashboard, name='supervisor_dashboard'),
    path('supervisor/mystundents/', views.mystudents, name='mystudents'),
    path('supervisor/make_announcement/', views.announcemnt, name='announcement'),
    path('supervisor/upload_resource/', views.lec_resource, name='resource_upload'),
    path('supervisor/students/results/', views.results, name='student_results'),
    path('supervisor/milestones/', views.milestones, name='milestones'),
    path('supervisors/student/upload/regno/', views.student_upload, name='student_upload'),
    
]