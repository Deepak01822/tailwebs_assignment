from django.http import JsonResponse
from django.shortcuts import redirect
from rest_framework.response import Response
from rest_framework import status
import re

def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def validate_marks(marks):
    """Validate marks are within acceptable range"""
    try:
        marks = int(marks)
        if marks < 0 or marks > 100:
            return False, "Marks must be between 0 and 100"
        return True, marks
    except (ValueError, TypeError):
        return False, "Marks must be a valid number"

def validate_name(name):
    """Validate student name"""
    if not name or len(name.strip()) < 2:
        return False, "Name must be at least 2 characters long"
    if not re.match(r'^[a-zA-Z\s]+$', name.strip()):
        return False, "Name can only contain letters and spaces"
    return True, name.strip()

def validate_subject(subject):
    """Validate subject name"""
    if not subject or len(subject.strip()) < 2:
        return False, "Subject must be at least 2 characters long"
    if not re.match(r'^[a-zA-Z\s]+$', subject.strip()):
        return False, "Subject can only contain letters and spaces"
    return True, subject.strip()

def calculate_new_marks(existing_marks, new_marks):
    """Helper function to calculate new marks when student exists"""
    # Business logic: Add new marks to existing marks
    total = existing_marks + new_marks
    if total > 100:
        return False, total, "Total marks cannot exceed 100"
    return True, total, "Marks updated successfully"

def require_authentication(view_func_or_class):
    """Decorator to require authentication for views (works with both function and class-based views)"""
    
    def check_auth(request):
        """Helper function to check authentication"""
        from .models import SessionToken
        
        token = request.COOKIES.get('session_token')
        if not token:
            return False, None
        
        try:
            session = SessionToken.objects.get(token=token)
            if not session.is_valid():
                return False, None
            
            request.teacher = session.teacher
            return True, session.teacher
        except SessionToken.DoesNotExist:
            return False, None
    
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            is_authenticated, teacher = check_auth(request)
            
            if not is_authenticated:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'error': 'Authentication required'}, status=401)
                return redirect('login')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    
    # Handle both function-based and class-based views
    if hasattr(view_func_or_class, 'as_view'):
        # It's a class-based view
        original_dispatch = view_func_or_class.dispatch
        
        def authenticated_dispatch(self, request, *args, **kwargs):
            is_authenticated, teacher = check_auth(request)
            
            if not is_authenticated:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'error': 'Authentication required'}, status=401)
                return redirect('login')
            
            return original_dispatch(self, request, *args, **kwargs)
        
        view_func_or_class.dispatch = authenticated_dispatch
        return view_func_or_class
    else:
        # It's a function-based view
        return decorator(view_func_or_class)