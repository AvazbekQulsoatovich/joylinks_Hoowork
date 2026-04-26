import os
import sys
import django

# Add the current directory to sys.path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.template.loader import get_template

try:
    t = get_template('admin/dashboard.html')
    print("Admin dashboard template loaded successfully!")
except Exception as e:
    print(f"Error loading admin dashboard template: {e}")

try:
    t = get_template('teacher/dashboard.html')
    print("Teacher dashboard template loaded successfully!")
except Exception as e:
    print(f"Error loading teacher dashboard template: {e}")
