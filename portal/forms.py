# portal/forms.py
from django import forms
from django.core.exceptions import ValidationError
import html
import re

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

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        }), 
        required=True
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            # Escape HTML to prevent XSS
            username = html.escape(username.strip())
            if len(username) < 3:
                raise ValidationError("Username must be at least 3 characters long")
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password and len(password) < 6:
            raise ValidationError("Password must be at least 6 characters long")
        return password

class StudentForm(forms.Form):
    name = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter student name'
        })
    )
    subject = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter subject'
        })
    )
    marks = forms.IntegerField(
        min_value=0, 
        max_value=100, 
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter marks (0-100)',
            'min': '0',
            'max': '100'
        })
    )

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            name = html.escape(name.strip())
            is_valid, result = validate_name(name)
            if not is_valid:
                raise ValidationError(result)
            return result
        return name

    def clean_subject(self):
        subject = self.cleaned_data.get('subject')
        if subject:
            subject = html.escape(subject.strip())
            is_valid, result = validate_subject(subject)
            if not is_valid:
                raise ValidationError(result)
            return result
        return subject

    def clean_marks(self):
        marks = self.cleaned_data.get('marks')
        if marks is not None:
            if marks < 0 or marks > 100:
                raise ValidationError("Marks must be between 0 and 100")
        return marks