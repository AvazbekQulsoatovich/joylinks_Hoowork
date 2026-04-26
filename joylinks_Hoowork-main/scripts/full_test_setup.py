#!/usr/bin/env python
import os
import django
from django.utils import timezone
from datetime import timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from academy.models import Course, Group, Certificate, MarketProduct, MarketPurchase
from homeworks.models import Homework, Submission
from django.db import models

User = get_user_model()

def clear_all_data():
    """Ma'lumotlar bazasini qibinib tozala"""
    print("📦 Ma'lumotlar bazasini tozalanmoqda...")
    User.objects.all().delete()
    Course.objects.all().delete()
    Group.objects.all().delete()
    Certificate.objects.all().delete()
    MarketProduct.objects.all().delete()
    MarketPurchase.objects.all().delete()
    Homework.objects.all().delete()
    Submission.objects.all().delete()
    print("✅ Ma'lumotlar bazasi tozalandi\n")

def create_users():
    """100 ta foydalanuvchi yaratish"""
    print("👥 100 ta foydalanuvchi yaratilmoqda...")
    from django.contrib.auth.hashers import make_password
    
    users_data = []
    users = {
        'admins': [],
        'teachers': [],
        'students': [],
        'moderators': []
    }
    
    # Barcha foydalanuvchilar uchun password hash
    hashed_pw = make_password('password123')
    
    # 5 ta Admin yaratish
    for i in range(1, 6):
        users_data.append(User(
            username=f'admin{i}',
            email=f'admin{i}@test.com',
            password=hashed_pw,
            first_name=f'Admin',
            last_name=f'{i}',
            role='ADMIN',
            coin_balance=999999
        ))
    
    # 5 ta Moderator yaratish
    for i in range(1, 6):
        users_data.append(User(
            username=f'moderator{i}',
            email=f'moderator{i}@test.com',
            password=hashed_pw,
            first_name=f'Moderator',
            last_name=f'{i}',
            role='MODERATOR',
            coin_balance=50000
        ))
    
    # 20 ta O'qituvchi yaratish
    for i in range(1, 21):
        users_data.append(User(
            username=f'teacher{i}',
            email=f'teacher{i}@test.com',
            password=hashed_pw,
            first_name=f'O\'qituvchi',
            last_name=f'{i}',
            role='TEACHER',
            coin_balance=1000
        ))
    
    # 70 ta O'quvchi yaratish
    for i in range(1, 71):
        users_data.append(User(
            username=f'student{i}',
            email=f'student{i}@test.com',
            password=hashed_pw,
            first_name=f'O\'quvchi',
            last_name=f'{i}',
            role='STUDENT',
            coin_balance=random.randint(100, 5000)
        ))
    
    # Barcha foydalanuvchilarni batch qo'shish
    created_users = User.objects.bulk_create(users_data, batch_size=100)
    
    # Barcha foydalanuvchilarni yaratilgan ro'yxatga jo'natish
    for user in created_users:
        if user.role == 'ADMIN':
            users['admins'].append(user)
        elif user.role == 'MODERATOR':
            users['moderators'].append(user)
        elif user.role == 'TEACHER':
            users['teachers'].append(user)
        elif user.role == 'STUDENT':
            users['students'].append(user)
    
    print(f"✅ 100 ta foydalanuvchi yaratildi:")
    print(f"   - Adminlar: {len(users['admins'])}")
    print(f"   - Moderatorlar: {len(users['moderators'])}")
    print(f"   - O'qituvchilar: {len(users['teachers'])}")
    print(f"   - O'quvchilar: {len(users['students'])}\n")
    
    return users

def create_courses():
    """Kurslar yaratish"""
    print("📚 Kurslar yaratilmoqda...")
    courses = []
    course_titles = [
        'Python Backend Development',
        'Web Design va Frontend',
        'Mobile App Development',
        'Data Science va AI',
        'DevOps va Cloud',
        'Cybersecurity',
        'Game Development',
        'Machine Learning',
        'Blockchain Development',
        'Cloud Architecture'
    ]
    
    for title in course_titles:
        course = Course.objects.create(
            name=title,
            description=f'{title} bo\'yicha chuqur o\'qituvlik kursi'
        )
        courses.append(course)
    
    print(f"✅ {len(courses)} ta kurs yaratildi\n")
    return courses

def create_groups(courses, teachers):
    """Guruhlar yaratish"""
    print("👨‍👩‍👧‍👦 Guruhlar yaratilmoqda...")
    groups = []
    group_counter = 1
    
    for course in courses:
        for j in range(1, 11):  # Har bir kursda 10 ta guruha
            group = Group.objects.create(
                name=f"{course.name} - Guruha {j}",
                course=course
            )
            # Tasodifiy 2-3 o'qituvchi belgilash
            group_teachers = random.sample(teachers, k=random.randint(2, 3))
            group.teachers.set(group_teachers)
            
            groups.append(group)
            group_counter += 1
    
    print(f"✅ {len(groups)} ta guruha yaratildi\n")
    return groups

def assign_students_to_groups(groups, students):
    """O'quvchilarni guruhlar bilan bog'lash"""
    print("📋 O'quvchilar guruhlar bilan bog'lanmoqda...")
    
    # Har bir o'quvchini 2-3 ta guruhga belgilash
    for student in students:
        assigned_groups = random.sample(groups, k=random.randint(2, 3))
        for group in assigned_groups:
            group.students.add(student)
    
    print(f"✅ Barcha o'quvchilar guruhlar bilan bog'landi\n")

def create_market_products():
    """Market produktlari yaratish"""
    print("🛍️  Market produktlari yaratilmoqda...")
    products = []
    
    product_data = [
        ('Certificate of Excellence', 'Sertifikat', 500),
        ('Laptop Sticker Pack', 'Stikers to\'plami', 100),
        ('Premium Account', 'Premium hisobi', 5000),
        ('Coding Book', 'Dasturlash kitabi', 300),
        ('Coffee Cup', 'Qahva kosasi', 150),
        ('USB Drive 32GB', 'USB drive', 400),
        ('Monitor 24"', 'Monitor', 15000),
        ('Mechanical Keyboard', 'Mexanik klaviatura', 3000),
        ('Wireless Mouse', 'Simsiz sichqoncha', 800),
        ('Gaming Headset', 'Gaming naushnik', 2500),
        ('Desk Lamp', 'Stol lampasi', 1200),
        ('Coding Challenge Pack', 'Murakkab vazifalar to\'plami', 200),
        ('Algorithm Course', 'Algoritm kursi', 2000),
        ('Web Development Course', 'Web kursi', 3000),
        ('Python Masterclass', 'Python kurs', 2500),
        ('Database Design', 'Ma\'lumotlar bazasi kursi', 1800),
        ('System Design', 'Sistema dizayni', 4000),
        ('Mobile Dev Kit', 'Mobile vositalari', 5000),
        ('AI Workshop', 'AI seminar', 3500),
        ('Cloud Certification', 'Cloud sertifikati', 6000),
    ]
    
    for name, description, price in product_data:
        product = MarketProduct.objects.create(
            name=name,
            description=description,
            price_coins=price,
            is_active=True
        )
        products.append(product)
    
    print(f"✅ {len(products)} ta product yaratildi\n")
    return products

def create_homeworks(groups, teachers):
    """Vazifalar yaratish"""
    print("📝 Vazifalar yaratilmoqda...")
    homeworks = []
    homework_titles = [
        'Python Functions',
        'Django ORM',
        'REST API Development',
        'Database Normalization',
        'Authentication & Authorization',
        'Testing & Debugging',
        'Performance Optimization',
        'Security Best Practices',
        'Code Documentation',
        'Git & Version Control',
    ]
    
    homework_count = 0
    for group in groups:
        for idx, title in enumerate(homework_titles[:3]):  # Har guruhga 3 ta vazifa
            deadline = timezone.now() + timedelta(days=random.randint(3, 14))
            teacher = random.choice(group.teachers.all())
            
            homework = Homework.objects.create(
                title=f"{title} - {group.name}",
                description=f"{title} bo'yicha chuqur o'rganish va amaliy ko'nikma",
                deadline=deadline,
                max_score=100,
                group=group,
                created_by=teacher,
                sequence=idx + 1
            )
            homeworks.append(homework)
            homework_count += 1
    
    print(f"✅ {homework_count} ta vazifa yaratildi\n")
    return homeworks

def create_submissions(homeworks, groups, students):
    """Topshirishlar yaratish"""
    print("📤 Topshirishlar yaratilmoqda...")
    submissions = []
    submission_count = 0
    
    for homework in homeworks:
        group = homework.group
        group_students = list(group.students.all())
        
        # Agar guruha o'quvchisi yo'q bo'lsa skip qil
        if not group_students:
            continue
        
        # Har vazifaga 50-100% o'quvchilar topshirydi
        sample_size = max(1, len(group_students) // 2)
        submitting_students = random.sample(group_students, k=min(sample_size, len(group_students)))
        
        for student in submitting_students:
            # Agar submission mavjud bo'lsa, skip qil
            if Submission.objects.filter(homework=homework, student=student).exists():
                continue
            
            score = random.randint(0, 100)
            is_graded = random.choice([True, False])
            
            submission = Submission.objects.create(
                homework=homework,
                student=student,
                content=f"Solution for {homework.title}",
                is_code=random.choice([True, False]),
                code_language=random.choice(['python', 'javascript', 'java', 'cpp']),
                score_percent=score if is_graded else 0,
                is_graded=is_graded,
                teacher_comment="Good work!" if is_graded and score > 70 else "Needs improvement" if is_graded else "",
                graded_by=random.choice(homework.group.teachers.all()) if is_graded else None,
                graded_at=timezone.now() if is_graded else None,
                coin_rewarded=is_graded and score > 60,
                coin_amount_awarded=int((score / 100) * 100) if is_graded and score > 60 else 0
            )
            submissions.append(submission)
            submission_count += 1
            
            # Coin berish
            if submission.coin_rewarded:
                student.coin_balance += submission.coin_amount_awarded
                student.save(update_fields=['coin_balance'])
    
    print(f"✅ {submission_count} ta topshirish yaratildi\n")

def create_market_purchases(students, products):
    """Market xaridlari yaratish"""
    print("🛒 Market xaridlari yaratilmoqda...")
    purchases = []
    
    for student in students:
        # Har bir o'quvchi 1-3 ta mahsulot xarid qiladi
        num_purchases = random.randint(1, 3)
        selected_products = random.sample(products, k=min(num_purchases, len(products)))
        
        for product in selected_products:
            if student.coin_balance >= product.price_coins:
                purchase = MarketPurchase.objects.create(
                    product=product,
                    student=student,
                    coins_spent=product.price_coins,
                    admin_confirmed=random.choice([True, False])
                )
                purchases.append(purchase)
                
                if purchase.admin_confirmed:
                    student.coin_balance -= product.price_coins
                    student.save(update_fields=['coin_balance'])
    
    print(f"✅ {len(purchases)} ta xarid yaratildi\n")

def create_certificates(students, courses):
    """Sertifikatlar yaratish"""
    print("🎓 Sertifikatlar yaratilmoqda...")
    certificates = []
    
    # Har o'quvchiga 1-2 ta sertifikat berish
    for student in students:
        num_certs = random.randint(1, 2)
        selected_courses = random.sample(courses, k=min(num_certs, len(courses)))
        
        for course in selected_courses:
            certificate = Certificate.objects.create(
                student=student,
                course=course,
                file=None  # Haqiqiy faylni yaratmayapti
            )
            certificates.append(certificate)
    
    print(f"✅ {len(certificates)} ta sertifikat yaratildi\n")

def run_system_tests():
    """Sistem testlarini o'tkazish"""
    print("🧪 Sistem testlarini o'tkazilmoqda...\n")
    
    errors = []
    # 3. Guruha testi
    print("3️⃣  Guruha testi:")
    try:
        groups = Group.objects.count()
        avg_teachers = Group.objects.annotate(num_teachers=models.Count('teachers')).aggregate(avg=models.Avg('num_teachers'))['avg'] or 0
        print(f"   ✓ Gruppalar soni: {groups}")
        print(f"   ✓ O'rtacha o'qituvchilar: {avg_teachers}")
        print()
    except Exception as e:
        errors.append(f"Guruha testi: {str(e)}")
    
    # 4. Vazifa testi
    print("4️⃣  Vazifa testi:")
    try:
        homeworks = Homework.objects.count()
        submissions = Submission.objects.count()
        graded = Submission.objects.filter(is_graded=True).count()
        
        print(f"   ✓ Vazifalar soni: {homeworks}")
        print(f"   ✓ Topshirishlar soni: {submissions}")
        print(f"   ✓ Shunchaki baholanganlari: {graded}")
        print()
    except Exception as e:
        errors.append(f"Vazifa testi: {str(e)}")
    
    # 5. Market testi
    print("5️⃣  Market testi:")
    try:
        products = MarketProduct.objects.count()
        purchases = MarketPurchase.objects.count()
        
        print(f"   ✓ Market mahsulotlari: {products}")
        print(f"   ✓ Xaridlar soni: {purchases}")
        print()
    except Exception as e:
        errors.append(f"Market testi: {str(e)}")
    
    # 6. Sertifikat testi
    print("6️⃣  Sertifikat testi:")
    try:
        certificates = Certificate.objects.count()
        print(f"   ✓ Sertifikatlar soni: {certificates}")
        print()
    except Exception as e:
        errors.append(f"Sertifikat testi: {str(e)}")
    
    # 7. Tangalar testi
    print("7️⃣  Tanga balansi testi:")
    try:
        total_coins = User.objects.aggregate(models.Sum('coin_balance'))['coin_balance__sum'] or 0
        avg_coins = User.objects.filter(role='STUDENT').aggregate(models.Avg('coin_balance'))['coin_balance__avg'] or 0
        
        print(f"   ✓ Jami tangalar: {total_coins}")
        print(f"   ✓ O'quvchilarning o'rtacha tangalari: {avg_coins:.0f}")
        print()
    except Exception as e:
        errors.append(f"Tanga testi: {str(e)}")
    
    # Barcha testlarning xulosa
    print("=" * 60)
    if errors:
        print("❌ XATOLAR TOPILDI:")
        for error in errors:
            print(f"   - {error}")
    else:
        print("✅ BARCHA TESTLAR MUVAFFAQIYATLI O'TGAN!")
    print("=" * 60)
    
    return len(errors) == 0

def main():
    """Asosiy funksiya"""
    print("\n" + "="*60)
    print("🚀 FULL SYSTEM TEST SETUP - BOSHLANG'ICH")
    print("="*60 + "\n")
    
    try:
        # 1. Tozalash
        clear_all_data()
        
        # 2. Foydalanuvchilar
        users = create_users()
        
        # 3. Kurslar
        courses = create_courses()
        
        # 4. Gruppalar
        groups = create_groups(courses, users['teachers'])
        
        # 5. O'quvchilarni guruhlar bilan bog'lash
        assign_students_to_groups(groups, users['students'])
        
        # 6. Market produktlari
        products = create_market_products()
        
        # 7. Vazifalar
        homeworks = create_homeworks(groups, users['teachers'])
        
        # 8. Topshirishlar
        create_submissions(homeworks, groups, users['students'])
        
        # 9. Market xaridlari
        create_market_purchases(users['students'], products)
        
        # 10. Sertifikatlar
        create_certificates(users['students'], courses)
        
        # 11. Testlar
        print("\n" + "="*60)
        success = run_system_tests()
        
        print("\n" + "="*60)
        print("✨ SETUP KOMPLETTI!")
        print("="*60)
        print("\n📌 LOGIN BILLARI:")
        print("   Admin: admin1 / password123")
        print("   Teacher: teacher1 / password123")
        print("   Student: student1 / password123")
        print("\n")
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"\n❌ XATO: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    from django.db import models
    exit(main())
