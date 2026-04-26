import os
import django
import json
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import User
from academy.models import Group, Course
from homeworks.models import Homework, Submission, Notification

def run_audit():
    c = Client()
    results = []

    def log_test(name, success, message=""):
        results.append({"name": name, "success": success, "message": message})
        status = "PASSED" if success else "FAILED"
        print(f"[{status}] {name}: {message}")

    try:
        # TEST 1: Login & Profile Update
        print("\n--- Testing Auth & Profile ---")
        if not c.login(username='teacher', password='teacher123'):
            log_test("Teacher Login", False, "Could not log in as teacher/teacher123")
            return
        log_test("Teacher Login", True)

        # Update Profile (Username & Name)
        # Note: ProfileUpdateView uses 'pk' in URL or inherits from LoginRequiredMixin
        profile_edit_url = reverse('profile_edit')
        response = c.post(profile_edit_url, {
            'username': 'teacher_new',
            'first_name': 'Zohid',
            'last_name': 'Egamberdiyev',
            'email': 'teacher@example.com',
            'phone': '+998901234567'
        }, follow=True)
        
        user = User.objects.get(pk=User.objects.get(username='teacher_new').pk)
        if response.status_code == 200 and user.username == 'teacher_new':
            log_test("Profile Update (Username)", True, f"Username changed to {user.username}")
        else:
            log_test("Profile Update (Username)", False, f"Status: {response.status_code}, User: {user.username}")

        # Check if still logged in
        dash_response = c.get(reverse('teacher_dashboard'))
        if dash_response.status_code == 200:
            log_test("Session Persistence", True, "Successfully stayed logged in after username change")
        else:
            log_test("Session Persistence", False, f"Status: {dash_response.status_code}")

        # TEST 2: Course Visibility
        print("\n--- Testing Course Visibility ---")
        course_list_url = reverse('course_list')
        response = c.get(course_list_url)
        content = response.content.decode('utf-8')
        
        # Debugging: Print found courses
        user.refresh_from_db()
        assigned_groups = Group.objects.filter(teachers=user)
        print(f"DEBUG: Teacher actually has {assigned_groups.count()} groups in DB.")
        
        course_found = False
        if assigned_groups.exists():
            course_name = assigned_groups.first().course.name
            if course_name in content:
                course_found = True
        
        log_test("Course Visibility (Assigned)", course_found, "Teacher sees their assigned course in list")

        # TEST 3: Coin System
        print("\n--- Testing Coin System ---")
        request_url = reverse('request_coins')
        response = c.get(request_url, follow=True)
        if response.status_code == 200:
            # Check for ANY notification with title "Tanga so'rovi"
            notif_exists = Notification.objects.filter(title="Tanga so'rovi").exists()
            log_test("Coin Request", notif_exists, "Notification created in DB")
        else:
            log_test("Coin Request", False, f"Status: {response.status_code}")

        # TEST 4: Homework Workflow
        print("\n--- Testing Homework Lifecycle ---")
        group = Group.objects.filter(teachers=user).first()
        if not group:
            log_test("Homework Test", False, "No group found for this teacher")
        else:
            hw = Homework.objects.filter(group=group).first()
            student_user = User.objects.get(username='student')
            
            # Student Submission
            c.logout()
            if not c.login(username='student', password='student123'):
                log_test("Student Login", False)
            else:
                sub_url = reverse('submission_create', kwargs={'homework_id': hw.pk})
                # Add submission_type to fix the ChoiceField error
                response = c.post(sub_url, {
                    'submission_type': 'text',
                    'content': 'This is my solution via verification script',
                    'code_language': 'python'
                }, follow=True)
                
                if response.status_code == 200 and Submission.objects.filter(homework=hw, student=student_user).exists():
                    log_test("Student Submission", True, f"Successfully submitted to {hw.title}")
                else:
                    print(f"DEBUG: Submission failed. Response status: {response.status_code}")
                    log_test("Student Submission", False)
        
        # Teacher Grading
        c.logout()
        c.login(username='teacher_new', password='teacher123')
        sub = Submission.objects.filter(homework=hw, student=student_user).first()
        if sub:
            grade_url = reverse('grade_submission', args=[sub.pk])
            response = c.post(grade_url, {'score_percent': 90, 'teacher_comment': 'Good job!'}, follow=True)
            sub.refresh_from_db()
            if response.status_code == 200 and sub.is_graded and sub.score_percent == 90:
                log_test("Teacher Grading", True, "Successfully graded submission at 90%")
            else:
                log_test("Teacher Grading", False, f"Status: {response.status_code}, Graded: {sub.is_graded}")

        # Cleanup / Report
        with open('test_report.json', 'w') as f:
            json.dump(results, f, indent=4)
        print("\nAudit Complete. Results saved to test_report.json")

    except Exception as e:
        print(f"\n[CRITICAL ERROR] {str(e)}")
        log_test("System Audit", False, str(e))

if __name__ == "__main__":
    run_audit()
