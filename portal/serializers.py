from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Teacher, Student, AuditLog
from .utils import validate_name, validate_subject, validate_marks
import html

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100, required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate_username(self, value):
        if value:
            # Escape HTML to prevent XSS
            value = html.escape(value.strip())
            if len(value) < 3:
                raise serializers.ValidationError("Username must be at least 3 characters long")
        return value

    def validate_password(self, value):
        if value and len(value) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters long")
        return value

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'name', 'subject', 'marks', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        if value:
            value = html.escape(value.strip())
            is_valid, result = validate_name(value)
            if not is_valid:
                raise serializers.ValidationError(result)
            return result
        return value

    def validate_subject(self, value):
        if value:
            value = html.escape(value.strip())
            is_valid, result = validate_subject(value)
            if not is_valid:
                raise serializers.ValidationError(result)
            return result
        return value

    def validate_marks(self, value):
        if value is not None:
            is_valid, validated_marks = validate_marks(value)
            if not is_valid:
                raise serializers.ValidationError(validated_marks)
            return validated_marks
        return value

class StudentCreateUpdateSerializer(StudentSerializer):
    """Serializer for creating/updating students with business logic"""
    
    def create(self, validated_data):
        teacher = self.context['teacher']
        name = validated_data['name']
        subject = validated_data['subject']
        marks = validated_data['marks']
        
        # Check if student with same name and subject exists
        try:
            existing_student = Student.objects.get(
                name=name, 
                subject=subject, 
                teacher=teacher
            )
            
            # Student exists, calculate new marks
            from .utils import calculate_new_marks
            success, new_marks, message = calculate_new_marks(
                existing_student.marks, marks
            )
            
            if not success:
                raise serializers.ValidationError({'marks': message})
            
            # Update existing student
            old_marks = existing_student.marks
            existing_student.marks = new_marks
            existing_student.save()
            
            # Log the update
            AuditLog.objects.create(
                teacher=teacher,
                action='UPDATE_MARKS',
                student_name=name,
                subject=subject,
                old_marks=old_marks,
                new_marks=new_marks,
                ip_address=self.context['ip_address']
            )
            
            # Add custom message for frontend
            existing_student._update_message = f'Updated marks for {name}. New total: {new_marks}'
            return existing_student
        
        except Student.DoesNotExist:
            # Create new student
            student = Student.objects.create(
                name=name,
                subject=subject,
                marks=marks,
                teacher=teacher
            )
            
            # Log the creation
            AuditLog.objects.create(
                teacher=teacher,
                action='CREATE_STUDENT',
                student_name=name,
                subject=subject,
                new_marks=marks,
                ip_address=self.context['ip_address']
            )
            
            student._update_message = f'Student {name} added successfully'
            return student

class MarksUpdateSerializer(serializers.Serializer):
    student_id = serializers.IntegerField(required=True)
    marks = serializers.IntegerField(required=True)

    def validate_marks(self, value):
        is_valid, validated_marks = validate_marks(value)
        if not is_valid:
            raise serializers.ValidationError(validated_marks)
        return validated_marks

class StudentDeleteSerializer(serializers.Serializer):
    student_id = serializers.IntegerField(required=True)

class AuditLogSerializer(serializers.ModelSerializer):
    teacher_username = serializers.CharField(source='teacher.username', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = ['id', 'teacher_username', 'action', 'student_name', 'subject', 
                 'old_marks', 'new_marks', 'timestamp', 'ip_address']
        read_only_fields = fields