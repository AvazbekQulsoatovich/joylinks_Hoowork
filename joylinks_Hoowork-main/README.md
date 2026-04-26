# HooWork - Joylinks IT Academy Homework System

HooWork is a premium homework management platform designed for IT academies. It features role-based access control (Admin, Moderator, Teacher, Student), automated coin rewards, and a marketplace for students.

## 🚀 Quick Start (Local Development)

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd joylinks_Hoowork-main
   ```

2. **Create a virtual environment and install dependencies:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment:**
   Copy `.env.example` to `.env` and fill in the values.
   ```bash
   cp .env.example .env
   ```

4. **Initialize Database:**
   ```bash
   python manage.py migrate
   python manage.py create_cache_table
   ```

5. **Create Admin User:**
   ```bash
   python manage.py shell -c "from users.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin_password', role='ADMIN')"
   ```

6. **Run Server:**
   ```bash
   python manage.py runserver
   ```

---

## 🛠 Deployment Guide (Production)

This guide assumes a standard Ubuntu Server (22.04+) setup with Nginx and Gunicorn.

### 1. System Requirements
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx postgresql postgresql-contrib libpq-dev
```

### 2. Project Setup
Place the project in `/var/www/hoowork`.
Set up the virtual environment as described in the Quick Start.

### 3. Gunicorn Configuration
Create a Gunicorn service file: `/etc/systemd/system/hoowork.service`
```ini
[Unit]
Description=Gunicorn instance for HooWork
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/hoowork
EnvironmentFile=/var/www/hoowork/.env
ExecStart=/var/www/hoowork/.venv/bin/gunicorn --workers 3 --bind unix:/var/www/hoowork/hoowork.sock core.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 4. Nginx Configuration
Create a site configuration: `/etc/nginx/sites-available/hoowork`
```nginx
server {
    listen 80;
    server_name hoowork.uz;

    location /static/ {
        alias /var/www/hoowork/staticfiles/;
    }

    location /media/ {
        alias /var/www/hoowork/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/hoowork/hoowork.sock;
    }
}
```

### 5. Finalize Deployment
```bash
sudo ln -s /etc/nginx/sites-available/hoowork /etc/nginx/sites-enabled
sudo systemctl start hoowork
sudo systemctl enable hoowork
sudo systemctl restart nginx
```

---

## 🔒 Security Features
- **Brute-force protection**: Powered by `django-axes`.
- **Permission checks**: Strict object-level filtering for Courses, Groups, and Homework.
- **Production Headers**: Pre-configured SecurityMiddleware settings.
- **Asset Compression**: WhiteNoise compression for CSS/JS.

## 💰 Coin System
- **Admins**: Have a base balance of 1,000,000,000,000 coins.
- **Teachers**: Award coins to students upon grading.
- **Students**: Spend coins in the Market.
