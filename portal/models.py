from django.db import models
from django.utils import timezone
import hashlib
import secrets

class Teacher(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password_hash = models.CharField(max_length=64)  # SHA-256 hash
    salt = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password):
        # Custom password hashing with salt
        self.salt = secrets.token_hex(16)
        salted_password = raw_password + self.salt
        self.password_hash = hashlib.sha256(salted_password.encode()).hexdigest()

    def check_password(self, raw_password):
        # Verify password against stored hash
        salted_password = raw_password + self.salt
        computed_hash = hashlib.sha256(salted_password.encode()).hexdigest()
        return computed_hash == self.password_hash

    def __str__(self):
        return self.username

class Student(models.Model):
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    marks = models.IntegerField()
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='students')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Ensure unique combination of name and subject per teacher
        unique_together = ('name', 'subject', 'teacher')
        indexes = [
            models.Index(fields=['teacher', 'name']),
            models.Index(fields=['teacher', 'subject']),
        ]

    def __str__(self):
        return f"{self.name} - {self.subject} ({self.marks})"

class SessionToken(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='sessions')
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_valid(self):
        return timezone.now() < self.expires_at

    @classmethod
    def create_token(cls, teacher):
        # Generate secure session token
        token = secrets.token_hex(32)
        expires_at = timezone.now() + timezone.timedelta(hours=8)
        
        # Clean up old tokens for this teacher
        cls.objects.filter(teacher=teacher).delete()
        
        return cls.objects.create(
            teacher=teacher,
            token=token,
            expires_at=expires_at
        )

    class Meta:
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['expires_at']),
        ]

class AuditLog(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=50)
    student_name = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    old_marks = models.IntegerField(null=True, blank=True)
    new_marks = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()

    class Meta:
        indexes = [
            models.Index(fields=['teacher', '-timestamp']),
            models.Index(fields=['action']),
        ]

    def __str__(self):
        return f"{self.teacher.username} - {self.action} - {self.timestamp}"
