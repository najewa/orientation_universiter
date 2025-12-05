from django.urls import path
from . import views

urlpatterns = [
     
    path('', views.home, name='home'),
    path('login/student/', views.login_student, name='login_student'),
    path('login/admin/', views.login_admin, name='login_admin'),
    path('register/student/', views.register_student, name='register_student'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/spending/', views.student_spending, name='student_spending'),
    path('import-students/', views.import_students, name='import_students'),
    
   # ✅ Suppression / modification OfficialStudent
    path('student/<int:student_id>/delete/', views.delete_student, name='delete_student'),
    path('student/<int:student_id>/edit/', views.edit_student, name='edit_student'),

    # ✅ Liste et suppression AuthorizedStudent
    path('accounts/authorized/', views.authorized_students_list, name='authorized_students_list'),
    path('authorized/delete/<int:student_id>/', views.delete_authorized_student, name='delete_authorized_student'),
    path('authorized/restore/', views.restore_authorized_student, name='restore_authorized_student'),
    
    path('decide/<int:student_id>/', views.decide_specialite, name='decide_specialite'),


    


]
   
  


