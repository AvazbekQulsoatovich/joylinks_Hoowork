# HooWork - Joylinks IT Academy CRM

HooWork - bu Joylinks IT Academy uchun maxsus ishlab chiqilgan o'quv jarayonini boshqarish tizimi. Bu platforma orqali o'qituvchilar uyga vazifalarni boshqarishi, talabalar esa ularni topshirishi va baholanishi mumkin.

## 🚀 Xususiyatlari

- **Rollar**: Admin, O'qituvchi, Talaba
- **Vazifalar**: Matn yoki Kod (Code block) ko'rinishida topshirish
- **Avtomatizatsiya**: Deadline o'tganda avtomatik 0% qo'yish
- **Statistika**: Guruhlar va o'quvchilar kesimida o'zlashtirish ko'rsatkichlari
- **Excel Export**: Hisobotlarni Excel formatda yuklab olish
- **PWA**: Mobil ilova sifatida o'rnatish imkoniyati

## 🛠 O'rnatish

Loyihani ishga tushirish uchun quyidagi qadamlarni bajaring:

1. **Repozitoriyani klonlash**
   ```bash
   git clone <repo-url>
   cd hoowork/backend
   ```

2. **Virtual muhit yaratish va faollashtirish**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Kutubxonalarni o'rnatish**
   ```bash
   pip install -r requirements.txt
   ```

4. **Migratsiyalarni amalga oshirish**
   ```bash
   python manage.py migrate
   ```

5. **Test ma'lumotlarini yuklash (ixtiyoriy)**
   ```bash
   python setup_test_data.py
   python reset_student_password.py
   ```

6. **Serverni ishga tushirish**
   ```bash
   python manage.py runserver
   ```

## 🔑 Konfiguratsiya

`.env` faylni yaratib quyidagi o'zgaruvchilarni qo'shish kerak:
```
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

**Ishga tushurishning oldida admin foydalanuvchini yaratish:**
```bash
python manage.py createsuperuser
```

## 📱 Texnologiyalar

- **Backend**: Django 6.0
- **Database**: SQLite (PostgreSQL compatible)
- **Frontend**: Django Templates + CSS Variables
- **PWA**: Manifest + Service Worker

---
© 2026 Joylinks IT Academy
