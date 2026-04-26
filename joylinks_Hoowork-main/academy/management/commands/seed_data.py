from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from academy.models import Course, Group, Certificate
from homeworks.models import Homework, Submission
from django.utils import timezone
import random
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with test data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Clearing existing data...')
        # Clear data but keep superusers
        Certificate.objects.all().delete()
        Submission.objects.all().delete()
        Homework.objects.all().delete()
        Group.objects.all().delete()
        Course.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write('Creating courses...')
        courses_data = [
            ('Frontend Developer', 'Modern web technologies'),
            ('Backend Developer', 'Server-side programming'),
            ('Ingliz tili', 'English language for all levels'),
            ('Kompyuter savodxonligi', 'Basic computer skills'),
            ('Kiberxavfsizlik', 'Cybersecurity fundamentals'),
            ('Rus tili', 'Russian language for all levels'),
        ]
        courses = []
        for name, desc in courses_data:
            course = Course.objects.create(name=name, description=desc)
            courses.append(course)

        self.stdout.write('Creating teachers...')
        teachers = []
        for i in range(len(courses)):
            teacher = User.objects.create_user(
                username=f'teacher_{i+1}',
                email=f'teacher{i+1}@example.com',
                password='password123',
                first_name=f'Teacher',
                last_name=f'Number {i+1}',
                role='TEACHER'
            )
            teachers.append(teacher)

        self.stdout.write('Creating groups, students, and homeworks...')
        for course in courses:
            for g_idx in range(1, 4):
                group_name = f"{course.name} - Group {g_idx}"
                group = Group.objects.create(name=group_name, course=course)
                
                # Assign 1 random teacher to the group
                group.teachers.add(random.choice(teachers))

                # Create 14 students per group
                group_students = []
                for s_idx in range(1, 15):
                    username = f'student_{course.id}_{g_idx}_{s_idx}'
                    student = User.objects.create_user(
                        username=username,
                        email=f'{username}@example.com',
                        password='password123',
                        first_name=f'Student',
                        last_name=f'{course.id}-{g_idx}-{s_idx}',
                        role='STUDENT'
                    )
                    group.students.add(student)
                    group_students.append(student)

                # Create 2-3 homeworks per group
                for h_idx in range(1, random.randint(3, 4)):
                    homework = Homework.objects.create(
                        title=f'Homework {h_idx} for {group.name}',
                        description=f'Description for homework {h_idx}',
                        deadline=timezone.now() + timedelta(days=random.randint(1, 7)),
                        group=group,
                        created_by=group.teachers.first(),
                        sequence=h_idx
                    )

                    # Create submissions for some students
                    for student in group_students:
                        if random.random() > 0.3: # 70% chance to submit
                            is_graded = random.random() > 0.4
                            score = random.randint(60, 100) if is_graded else 0
                            
                            Submission.objects.create(
                                homework=homework,
                                student=student,
                                content=f'This is my submission for {homework.title}',
                                score_percent=score,
                                is_graded=is_graded,
                                teacher_comment='Well done!' if is_graded else '',
                                graded_at=timezone.now() if is_graded else None,
                                graded_by=group.teachers.first() if is_graded else None
                            )

        self.stdout.write('Assigning certificates...')
        # Ensure at least 8 students have certificates
        all_students = list(User.objects.filter(role='STUDENT'))
        selected_students = random.sample(all_students, min(len(all_students), 20)) # Select 20 students to be safe
        
        for student in selected_students[:10]: # Give certs to first 10 selected
            course = random.choice(courses)
            Certificate.objects.create(
                student=student,
                course=course,
                file='certificates/default_cert.pdf'
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded database!'))
