import os
import sys
import django

# Add the project root to sys.path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from academy.models import Course, Group

User = get_user_model()

def populate():
    # 1. Create Users
    print("Creating users...")
    
    # Admin
    admin, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'role': User.Role.ADMIN,
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin.set_password('admin123')
        admin.save()
        print(f"Admin created: admin / admin123")
    else:
        print("Admin already exists")

    # Teacher
    teacher, created = User.objects.get_or_create(
        username='teacher',
        defaults={
            'email': 'teacher@example.com',
            'role': User.Role.TEACHER,
            'is_staff': True
        }
    )
    if created:
        teacher.set_password('teacher123')
        teacher.save()
        print(f"Teacher created: teacher / teacher123")
    else:
        print("Teacher already exists")

    # Student
    student, created = User.objects.get_or_create(
        username='student',
        defaults={
            'email': 'student@example.com',
            'role': User.Role.STUDENT,
            'coin_balance': 500
        }
    )
    if created:
        student.set_password('student123')
        student.save()
        print(f"Student created: student / student123")
    else:
        print("Student already exists")

    # 2. Create Course and Group
    print("\nCreating academy data...")
    course, _ = Course.objects.get_or_create(
        name="Python Foundation",
        defaults={'description': 'Python asoslari kursi'}
    )
    
    group, created = Group.objects.get_or_create(
        name="Python-001",
        course=course
    )
    
    if created:
        group.teachers.add(teacher)
        group.students.add(student)
        print(f"Group 'Python-001' created and users assigned.")
    else:
        print(f"Group 'Python-001' already exists.")

if __name__ == '__main__':
    populate()
