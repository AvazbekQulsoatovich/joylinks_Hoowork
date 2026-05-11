import os
import sys
import django
import random
from datetime import timedelta
from django.utils import timezone

# Add the project root to sys.path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from academy.models import Course, Group, Certificate, MarketProduct
from homeworks.models import Homework, Submission, Notification

User = get_user_model()

def populate_large():
    print("Starting large population script...")
    
    # 1. Create Courses
    print("Creating courses...")
    courses = []
    course_names = ["Python Foundation", "Fullstack Web", "Data Science", "Mobile Dev (Flutter)", "Cyber Security"]
    for name in course_names:
        course, _ = Course.objects.get_or_create(name=name, defaults={'description': f'{name} kursi uchun tavsif'})
        courses.append(course)

    # 2. Create Teachers
    print("Creating teachers...")
    teachers = []
    for i in range(1, 6):
        teacher, created = User.objects.get_or_create(
            username=f'teacher_{i}',
            defaults={
                'email': f'teacher{i}@example.com',
                'role': User.Role.TEACHER,
                'first_name': f'Teacher_{i}',
                'last_name': 'HooWork'
            }
        )
        if created:
            teacher.set_password('teacher123')
            teacher.save()
        teachers.append(teacher)

    # 3. Create Groups
    print("Creating groups...")
    groups = []
    for i in range(1, 11):
        course = random.choice(courses)
        group, _ = Group.objects.get_or_create(
            name=f'Guruh-{i:03d}',
            course=course
        )
        group.teachers.add(random.choice(teachers))
        groups.append(group)

    # 4. Create 100 Students
    print("Creating 100 students...")
    students = []
    for i in range(1, 101):
        username = f'student_{i:03d}'
        student, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@example.com',
                'role': User.Role.STUDENT,
                'coin_balance': random.randint(100, 1000),
                'first_name': f'Student_{i}',
                'last_name': 'Joylinks'
            }
        )
        if created:
            student.set_password('student123')
            student.save()
        
        # Assign to 1-2 groups
        assigned_groups = random.sample(groups, random.randint(1, 2))
        for g in assigned_groups:
            g.students.add(student)
        
        students.append(student)

    # 5. Create Homeworks
    print("Creating homeworks...")
    homeworks = []
    for g in groups:
        for i in range(1, 6):
            hw = Homework.objects.create(
                title=f'{g.name} - Vazifa {i}',
                description=f'Bu {g.name} guruhi uchun {i}-vazifa.',
                deadline=timezone.now() + timedelta(days=random.randint(-5, 10)),
                group=g,
                created_by=random.choice(g.teachers.all())
            )
            homeworks.append(hw)

    # 6. Create Submissions
    print("Creating submissions...")
    for hw in homeworks:
        # 70% of students submit
        students_in_group = hw.group.students.all()
        submitting_students = random.sample(list(students_in_group), int(len(students_in_group) * 0.7))
        
        for s in submitting_students:
            is_graded = random.choice([True, False])
            score = random.randint(50, 100) if is_graded else 0
            
            Submission.objects.create(
                homework=hw,
                student=s,
                content=f'Javob: {hw.title} uchun topshiriq bajarildi.',
                is_graded=is_graded,
                score_percent=score,
                graded_at=timezone.now() if is_graded else None,
                graded_by=random.choice(hw.group.teachers.all()) if is_graded else None
            )

    # 7. Create Certificates for some students
    print("Creating certificates...")
    for i in range(20):
        student = random.choice(students)
        course = random.choice(courses)
        Certificate.objects.create(student=student, course=course)

    # 8. Create Market Products
    print("Creating market products...")
    MarketProduct.objects.get_or_create(name="Futbolka", price_coins=500)
    MarketProduct.objects.get_or_create(name="Kepka", price_coins=300)
    MarketProduct.objects.get_or_create(name="Noutbuk stikeri", price_coins=50)

    print("\nPopulation complete!")
    print(f"Total Users: {User.objects.count()}")
    print(f"Total Students: {User.objects.filter(role='STUDENT').count()}")
    print(f"Total Groups: {Group.objects.count()}")
    print(f"Total Homeworks: {Homework.objects.count()}")

if __name__ == '__main__':
    populate_large()
