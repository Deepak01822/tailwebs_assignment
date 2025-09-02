from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.views.generic import TemplateView
from django.views import View
from django.db import transaction
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Teacher, Student, SessionToken, AuditLog
from .serializers import (
    StudentSerializer,
    StudentCreateUpdateSerializer,
    MarksUpdateSerializer,
    StudentDeleteSerializer
)
from .utils import get_client_ip, require_authentication
import json

class LoginView(View):
    """Handle teacher login using Django forms"""
    template_name = 'portal/login.html'
    
    def get(self, request):
        from .forms import LoginForm
        form = LoginForm()
        return render(request, self.template_name, {'form': form})
    
    @method_decorator(csrf_protect)
    def post(self, request):
        from .forms import LoginForm
        form = LoginForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            try:
                teacher = Teacher.objects.get(username=username)
                if teacher.check_password(password):
                    # Create session token
                    session = SessionToken.create_token(teacher)
                    
                    # Log successful login
                    AuditLog.objects.create(
                        teacher=teacher,
                        action='LOGIN',
                        student_name='N/A',
                        subject='N/A',
                        ip_address=get_client_ip(request)
                    )
                    
                    response = redirect('home')
                    # Set secure cookie with session token
                    response.set_cookie(
                        'session_token', 
                        session.token,
                        max_age=28800,  # 8 hours
                        httponly=True,
                        secure=True if request.is_secure() else False,
                        samesite='Lax'
                    )
                    return response
                else:
                    form.add_error('password', 'Invalid credentials')
            except Teacher.DoesNotExist:
                form.add_error('username', 'Invalid credentials')
        
        return render(request, self.template_name, {'form': form})

@method_decorator(require_authentication, name='dispatch')
class HomeView(TemplateView):
    """Display teacher home page with student list"""
    template_name = 'portal/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        students = Student.objects.filter(teacher=self.request.teacher).order_by('name', 'subject')
        context.update({
            'students': students,
            'teacher': self.request.teacher
        })
        return context

@method_decorator(require_authentication, name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
class StudentCreateView(APIView):
    """Handle adding new student (AJAX)"""
    
    def post(self, request):
        try:
            serializer = StudentCreateUpdateSerializer(
                data=request.data,
                context={
                    'teacher': request.teacher,
                    'ip_address': get_client_ip(request)
                }
            )
            
            if serializer.is_valid():
                with transaction.atomic():
                    student = serializer.save()
                    
                    # Get the custom message from the serializer
                    message = getattr(student, '_update_message', 'Operation completed successfully')
                    
                    response_data = {
                        'success': True,
                        'message': message,
                        'student_id': student.id,
                        'new_marks': student.marks
                    }
                    
                    # If this was a new student creation, include student data
                    if 'added successfully' in message:
                        response_data['student'] = StudentSerializer(student).data
                    
                    return Response(response_data, status=status.HTTP_201_CREATED)
            
            return Response({
                'success': False,
                'error': 'Invalid form data',
                'form_errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except json.JSONDecodeError:
            return Response({
                'success': False, 
                'error': 'Invalid JSON data'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False, 
                'error': 'Server error occurred'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(require_authentication, name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
class StudentUpdateView(APIView):
    """Handle inline marks update (AJAX)"""
    
    def post(self, request):
        try:
            serializer = MarksUpdateSerializer(data=request.data)
            
            if serializer.is_valid():
                student_id = serializer.validated_data['student_id']
                new_marks = serializer.validated_data['marks']
                
                with transaction.atomic():
                    student = get_object_or_404(
                        Student, 
                        id=student_id, 
                        teacher=request.teacher
                    )
                    
                    old_marks = student.marks
                    student.marks = new_marks
                    student.save()
                    
                    # Log the update
                    AuditLog.objects.create(
                        teacher=request.teacher,
                        action='INLINE_UPDATE',
                        student_name=student.name,
                        subject=student.subject,
                        old_marks=old_marks,
                        new_marks=new_marks,
                        ip_address=get_client_ip(request)
                    )
                    
                    return Response({
                        'success': True, 
                        'message': 'Marks updated successfully'
                    })
            
            return Response({
                'success': False,
                'error': 'Invalid data',
                'form_errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except json.JSONDecodeError:
            return Response({
                'success': False, 
                'error': 'Invalid JSON data'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False, 
                'error': 'Failed to update marks'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(require_authentication, name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
class StudentDeleteView(APIView):
    """Handle student deletion (AJAX)"""
    
    def post(self, request):
        try:
            serializer = StudentDeleteSerializer(data=request.data)
            
            if serializer.is_valid():
                student_id = serializer.validated_data['student_id']
                
                with transaction.atomic():
                    student = get_object_or_404(
                        Student, 
                        id=student_id, 
                        teacher=request.teacher
                    )
                    
                    # Log the deletion before deleting
                    AuditLog.objects.create(
                        teacher=request.teacher,
                        action='DELETE_STUDENT',
                        student_name=student.name,
                        subject=student.subject,
                        old_marks=student.marks,
                        ip_address=get_client_ip(request)
                    )
                    
                    student.delete()
                    
                    return Response({
                        'success': True, 
                        'message': 'Student deleted successfully'
                    })
            
            return Response({
                'success': False,
                'error': 'Invalid data',
                'form_errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except json.JSONDecodeError:
            return Response({
                'success': False, 
                'error': 'Invalid JSON data'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False, 
                'error': 'Failed to delete student'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LogoutView(View):
    """Handle teacher logout"""
    
    def get(self, request):
        return self.post(request)
    
    def post(self, request):
        token = request.COOKIES.get('session_token')
        if token:
            try:
                session = SessionToken.objects.get(token=token)
                
                # Log logout
                AuditLog.objects.create(
                    teacher=session.teacher,
                    action='LOGOUT',
                    student_name='N/A',
                    subject='N/A',
                    ip_address=get_client_ip(request)
                )
                
                session.delete()
            except SessionToken.DoesNotExist:
                pass
        
        response = redirect('login')
        response.delete_cookie('session_token')
        return response

@method_decorator(require_authentication, name='dispatch')
class StudentListView(APIView):
    """API endpoint to get student list"""
    
    def get(self, request):
        students = Student.objects.filter(teacher=request.teacher).order_by('name', 'subject')
        serializer = StudentSerializer(students, many=True)
        return Response({
            'success': True,
            'students': serializer.data
        })

@method_decorator(require_authentication, name='dispatch')
class AuditLogView(APIView):
    """API endpoint to get audit logs"""
    
    def get(self, request):
        logs = AuditLog.objects.filter(teacher=request.teacher).order_by('-timestamp')[:100]
        from .serializers import AuditLogSerializer
        serializer = AuditLogSerializer(logs, many=True)
        return Response({
            'success': True,
            'logs': serializer.data
        })