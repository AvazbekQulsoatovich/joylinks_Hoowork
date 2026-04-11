import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import User

def reset_user_password(username, password):
    try:
        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()
        print(f"Successfully reset password for: {username}")
    except User.DoesNotExist:
        print(f"User not found: {username}")

if __name__ == '__main__':
    reset_user_password('admin', 'admin123')
    reset_user_password('teacher', 'teacher123')
    reset_user_password('student', 'student123')
