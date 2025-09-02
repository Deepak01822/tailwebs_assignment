from django.urls import path
from .views import (
    LoginView, HomeView, StudentCreateView, StudentUpdateView,
    StudentDeleteView, LogoutView, StudentListView, AuditLogView
)

urlpatterns = [
    path('', LoginView.as_view(), name='login'),
    path('home/', HomeView.as_view(), name='home'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # API endpoints
    path('api/students/', StudentListView.as_view(), name='student_list_api'),
    path('api/students/add/', StudentCreateView.as_view(), name='add_student'),
    path('api/students/update/', StudentUpdateView.as_view(), name='update_marks'),
    path('api/students/delete/', StudentDeleteView.as_view(), name='delete_student'),
    path('api/audit-logs/', AuditLogView.as_view(), name='audit_logs'),
]