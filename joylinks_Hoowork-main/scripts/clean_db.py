import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from academy.models import Group, Course, MarketProduct, MarketPurchase
from homeworks.models import Homework, Submission, Notification

User = get_user_model()

def clean_database():
    print("Starting database cleanup...")
    
    # Keep users with roles ADMIN, TEACHER, STUDENT
    # Actually, keep all current users but reset their balances? 
    # The user said "ADMIN TEACHER STUDENT QOLSIN". 
    # I'll keep users who have these roles.
    
    # 1. Clear Notifications
    Notification.objects.all().delete()
    print("Notifications cleared.")
    
    # 2. Clear Market data
    MarketPurchase.objects.all().delete()
    MarketProduct.objects.all().delete()
    print("Market data cleared.")
    
    # 3. Clear Submissions and Homeworks
    Submission.objects.all().delete()
    Homework.objects.all().delete()
    print("Submissions and Homeworks cleared.")
    
    # 4. Clear Groups and Courses
    Group.objects.all().delete()
    Course.objects.all().delete()
    print("Groups and Courses cleared.")
    
    # 6. Delete users who DON'T have a standard role
    deleted_users = User.objects.exclude(role__in=['ADMIN', 'TEACHER', 'STUDENT']).delete()
    print(f"Deleted {deleted_users[0]} non-standard users.")
    
    # 7. Reset coin balances and give Admins a large amount
    User.objects.exclude(role='ADMIN', role__in=['TEACHER', 'STUDENT']).update(coin_balance=0)
    User.objects.filter(role='ADMIN').update(coin_balance=1000000000000)
    print("User coin balances reset (Admins given 1,000,000,000,000).")
    
    print("Database cleanup complete.")

if __name__ == "__main__":
    clean_database()
