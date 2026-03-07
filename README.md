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

## 🔑 Konfiguratsiya va Deploy

Loyihani serverga (VPS, Heroku, Railway va h.k.) yuklash uchun:

1.  **Muhit o'zgaruvchilari (`.env`):**
    `.env` faylini yaratib quyidagi o'zgaruvchilarni sozlang:
    ```bash
    DJANGO_SECRET_KEY=your-secret-key
    DEBUG=False
    ALLOWED_HOSTS=yourdomain.com,localhost
    # Ma'lumotlar bazasi (PostgreSQL tavsiya etiladi)
    DATABASE_URL=postgres://user:password@host:port/dbname
    ```

2.  **Statik fayllar:**
    ```bash
    python manage.py collectstatic --noinput
    ```

3.  **Rich Admin yaratish (100 mlrd tanga bilan):**
    Tizimda cheksiz imkoniyatga ega admin yaratish uchun maxsus skriptni ishga tushiring:
    ```bash
    python create_admin.py <username> <password> <email>
    ```
    *Misol: `python create_admin.py admin parolingiz admin@example.com`*

4.  **Gunicorn bilan ishga tushirish:**
    ```bash
    gunicorn core.wsgi --bind 0.0.0.0:8000
    ```

## 📱 Texnologiyalar

- **Backend**: Django 6.0
- **Database**: SQLite (PostgreSQL compatible)
- **Frontend**: Django Templates + CSS Variables
- **PWA**: Manifest + Service Worker

---
© 2026 Joylinks IT Academy
