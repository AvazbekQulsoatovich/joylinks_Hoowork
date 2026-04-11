import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import User

def reset_student_password():
    try:
        student = User.objects.get(username='student')
        student.set_password('student123')
        student.is_active = True
        student.save()
        print("Muvaffaqiyatli: 'student' foydalanuvchisi paroli 'student123' ga yangilandi va faollashtirildi.")
    except User.DoesNotExist:
        print("Xatolik: 'student' foydalanuvchisi topilmadi. setup_test_data.py ni ishga tushiring.")

if __name__ == '__main__':
    reset_student_password()
