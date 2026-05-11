import os
import sys
import django

# Add the project root to sys.path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from academy.models import Course, Group
from homeworks.models import Homework, Submission

User = get_user_model()

def test_deletion():
    print("Testing deletion logic...")
    
    # 1. Test deleting a student
    student = User.objects.filter(role='STUDENT').first()
    if student:
        print(f"Deleting student: {student.username}")
        student.delete()
        print("Student deleted successfully.")
    else:
        print("No student found to delete.")

    # 2. Test deleting a group
    group = Group.objects.first()
    if group:
        print(f"Deleting group: {group.name}")
        group.delete()
        print("Group deleted successfully.")
    else:
        print("No group found to delete.")

    # 3. Test deleting a course
    course = Course.objects.first()
    if course:
        print(f"Deleting course: {course.name}")
        course.delete()
        print("Course deleted successfully.")
    else:
        print("No course found to delete.")

if __name__ == '__main__':
    test_deletion()
