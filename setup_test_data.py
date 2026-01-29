import os
import django
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import User
from academy.models import Course, Group
from homeworks.models import Homework, Submission

def setup_data():
    # 1. Create Superuser
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        admin.role = 'ADMIN'
        admin.save()
        print("Superuser 'admin' created (pass: admin123)")

    # 2. Create Teacher
    teacher, created = User.objects.get_or_create(username='teacher', defaults={'email': 'teacher@example.com'})
    if created:
        teacher.set_password('teacher123')
        teacher.role = 'TEACHER'
        teacher.save()
        print("Teacher 'teacher' created (pass: teacher123)")

    # 3. Create Student
    student, created = User.objects.get_or_create(username='student', defaults={'email': 'student@example.com'})
    if created:
        student.set_password('student123')
        student.role = 'STUDENT'
        student.save()
        print("Student 'student' created (pass: student123)")

    # 4. Create Course
    course, created = Course.objects.get_or_create(name='Python Backend', defaults={'description': 'Django va PostgreSQL o\'rganamiz'})
    if created:
        print(f"Course '{course.name}' created")

    # 5. Create Group
    group, created = Group.objects.get_or_create(name='PB-101', course=course)
    if created:
        group.teachers.add(teacher)
        group.students.add(student)
        print(f"Group '{group.name}' created and users linked")

    # 6. Create Homework
    hw, created = Homework.objects.get_or_create(
        title='Django Modellari',
        group=group,
        defaults={
            'description': 'Modellar bilan ishlashni o\'rganing.',
            'deadline': timezone.now() + timedelta(days=2),
            'created_by': teacher,
            'sequence': 1
        }
    )
    if created:
        print(f"Homework '{hw.title}' created")

    print("\nSetup complete!")

if __name__ == '__main__':
    setup_data()
