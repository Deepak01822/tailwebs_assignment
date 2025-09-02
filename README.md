# Django Teacher Portal

A secure, logic-driven teacher portal application built with Django that allows authenticated teachers to manage students and their marks with comprehensive audit logging.

## Features

### 🔐 Authentication & Security
- **Custom Password Hashing**: Implements SHA-256 hashing with salt (no built-in Django auth)
- **Session Management**: Custom session token handling with expiration
- **CSRF Protection**: All forms protected against Cross-Site Request Forgery
- **XSS Prevention**: Input sanitization and HTML escaping
- **SQL Injection Protection**: Parameterized queries throughout
- **Audit Logging**: Complete action logging with timestamps and IP addresses

### 📚 Student Management
- **Student Listing**: View all students with name, subject, and marks
- **Inline Editing**: Update marks directly in the table with real-time validation
- **Inline Deletion**: Remove student records with confirmation
- **Add New Students**: Modal-based form for adding students
- **Duplicate Handling**: Smart logic for handling existing student-subject combinations

### ✅ Validation & Logic
- **Server-side Validation**: Comprehensive input validation
- **Client-side Validation**: Real-time form validation for better UX
- **Marks Validation**: Ensures marks are between 0-100
- **Name/Subject Validation**: Alphabetic characters and minimum length requirements
- **Custom Helper Functions**: `calculate_new_marks()` for business logic

## Technical Implementation

### Security Measures
1. **Custom Authentication**: No Django built-in auth, custom password handling
2. **Session Tokens**: Secure token-based sessions with expiration
3. **Input Sanitization**: HTML escaping to prevent XSS
4. **CSRF Tokens**: Protection on all forms and AJAX requests
5. **Secure Cookies**: HTTPOnly, Secure, and SameSite cookie attributes
6. **IP Logging**: Track user actions by IP address
7. **Database Security**: Parameterized queries prevent SQL injection

### Architecture
- **Custom Decorators**: `@require_authentication` for view protection
- **Transaction Management**: Database integrity with atomic transactions
- **Error Handling**: Comprehensive error handling and user feedback
- **AJAX Integration**: Seamless user experience with asynchronous requests
- **Responsive Design**: Mobile-friendly interface

## Setup Instructions

### Prerequisites
- Python 3.8+
- pip (Python package installer)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd tailwebs_assignment
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install Django==4.2.7
   ```

4. **Project Structure Setup**
   Create the following directory structure:
   ```
   teacher_portal/
   ├── manage.py
   ├── teacher_portal/
   │   ├── __init__.py
   │   ├── settings.py
   │   ├── urls.py
   │   └── wsgi.py
   └── portal/
       ├── __init__.py
       ├── models.py
       ├── views.py
       ├── urls.py
       ├── forms.py
       ├── utils.py
       ├── migrations/
       │   └── __init__.py
       └── templates/
           └── portal/
               ├── login.html
               └── home.html
   ```

5. **Create Django project and app**
   ```bash
   django-admin startproject teacher_portal
   cd teacher_portal
   python manage.py startapp portal
   ```

6. **Copy the provided code**
   - Copy all the Python code from the implementation into respective files
   - Copy HTML templates into the templates directory

7. **Update settings.py**
   ```python
   INSTALLED_APPS = [
       'django.contrib.admin',
       'django.contrib.auth',
       'django.contrib.contenttypes',
       'django.contrib.sessions',
       'django.contrib.messages',
       'django.contrib.staticfiles',
       'portal',  # Add this
   ]
   ```

8. **Run migrations**
   ```bash
   python manage.py makemigrations portal
   python manage.py migrate
   ```

9. **Create a teacher account**
   ```bash
   python manage.py shell
   ```
   Then in the Python shell:
   ```python
   from portal.models import Teacher
   teacher = Teacher(username='admin')
   teacher.set_password('admin123')
   teacher.save()
   exit()
   ```

10. **Run the development server**
    ```bash
    python manage.py runserver
    ```

11. **Access the application**
    - Open browser to `http://localhost:8000/`
    - Login with username: `admin`, password: `admin123`

12. **Other test credentials**
    - Login with username: `Manoj`, password: `manoj123`
    - Login with username: `testuser`, password: `testpass123`

## Usage Guide

### Login
1. Navigate to the login page
2. Enter your username and password
3. System will create a secure session token upon successful authentication

### Managing Students
1. **View Students**: Home page displays all students in a table
2. **Add Student**: Click "Add New Student" button to open modal form
3. **Edit Marks**: Click on marks field to edit inline (validates 0-100)
4. **Delete Student**: Click delete button with confirmation prompt

### Special Features
- **Duplicate Handling**: Adding a student with existing name+subject will add marks to existing record
- **Audit Trail**: All actions are logged with timestamps and IP addresses
- **Session Management**: Automatic logout after 8 hours of inactivity
- **Real-time Validation**: Immediate feedback on invalid inputs

## Database Schema

### Models
- **Teacher**: Custom user model with hashed passwords
- **Student**: Student records linked to teachers
- **SessionToken**: Custom session management
- **AuditLog**: Complete action logging

### Key Relationships
- Students belong to Teachers (ForeignKey)
- Sessions belong to Teachers (ForeignKey)
- Audit logs track all Teacher actions
- Unique constraint on (name, subject, teacher)

## Security Considerations

1. **Password Security**: Custom SHA-256 hashing with unique salt per user
2. **Session Security**: Secure token-based sessions with expiration
3. **Input Security**: All inputs validated and sanitized
4. **CSRF Protection**: Tokens on all forms and AJAX requests
5. **XSS Protection**: HTML escaping prevents script injection
6. **SQL Injection**: Parameterized queries exclusively
7. **Cookie Security**: HTTPOnly, Secure, SameSite attributes
8. **Audit Trail**: Complete logging for security monitoring

## Challenges Faced

### 1. Custom Authentication Implementation
**Challenge**: Building authentication without Django's built-in system
**Solution**: Created custom password hashing with salt and session token management

### 2. Inline Editing with Validation
**Challenge**: Real-time validation while maintaining security
**Solution**: AJAX requests with both client and server-side validation

### 3. Duplicate Student Handling
**Challenge**: Complex logic for existing student-subject combinations
**Solution**: Custom `calculate_new_marks()` helper function with transaction management

### 4. Security Implementation
**Challenge**: Implementing comprehensive security without libraries
**Solution**: Custom decorators, CSRF tokens, input sanitization, and audit logging

### 5. User Experience
**Challenge**: Balancing security with smooth user experience
**Solution**: AJAX requests, real-time feedback, and responsive design

## Time Investment

**Approximate Time Taken: 12-14 hours**

- Planning & Architecture: 2 hours
- Model Design & Implementation: 2 hours  
- Authentication System: 3 hours
- Views & Business Logic: 3 hours
- Templates & Frontend: 2 hours
- Security Implementation: 1 hour
- Testing & Debugging: 1-2 hours
- Documentation: 1 hour

## Code Quality Features

1. **Comprehensive Comments**: Inline documentation explaining logic
2. **Error Handling**: Graceful error handling throughout
3. **Validation**: Input validation at multiple levels
4. **Security**: Following security best practices
5. **Maintainability**: Clean, organized code structure
6. **Performance**: Efficient database queries and caching considerations

## Testing

### Manual Testing Checklist
- [ ] Teacher login/logout functionality
- [ ] Session expiration handling
- [ ] Student CRUD operations
- [ ] Inline editing validation
- [ ] Duplicate student handling
- [ ] Security measures (CSRF, XSS prevention)
- [ ] Audit logging verification
- [ ] Error handling and user feedback

### Sample Test Data
```python
# Create test teacher
teacher = Teacher(username='testuser')
teacher.set_password('testpass123')
teacher.save()

# Test students
students = [
    {'name': 'John Doe', 'subject': 'Mathematics', 'marks': 85},
    {'name': 'Jane Smith', 'subject': 'Physics', 'marks': 92},
    {'name': 'John Doe', 'subject': 'Physics', 'marks': 78},
]
```

## Production Deployment Notes

1. **Environment Variables**: Move sensitive settings to environment variables
2. **Database**: Use PostgreSQL or MySQL for production
3. **Security Headers**: Add additional security headers
4. **HTTPS**: Ensure all traffic uses HTTPS
5. **Logging**: Configure proper logging for production monitoring
6. **Backup**: Regular database backups
7. **Monitoring**: Set up application monitoring

## License

This project is created for educational/assessment purposes.
