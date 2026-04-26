#!/bin/bash

# Exit on error
set -e

PROJECT_NAME="joylinks"
PROJECT_DIR="/home/webdevaj/joylinks_Hoowork"
REPO_URL="https://github.com/AvazbekQulsoatovich/joylinks_Hoowork.git"
SERVER_IP="95.182.119.84"

echo "🚀 Starting deployment for $PROJECT_NAME..."

# 1. Update system and install dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev git nginx curl

# 2. Clone repository (if not exists)
if [ ! -d "$PROJECT_DIR" ]; then
    echo "📂 Cloning repository..."
    git clone $REPO_URL $PROJECT_DIR
else
    echo "📂 Repository already exists, pulling latest changes..."
    cd $PROJECT_DIR
    git pull origin main
fi

cd $PROJECT_DIR

# 3. Setup Virtual Environment
if [ ! -d ".venv" ]; then
    echo "🐍 Creating virtual environment with Python 3.12..."
    python3.12 -m venv .venv
fi

source .venv/bin/activate
echo "📦 Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. Configure .env for Production
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat <<EOF > .env
SECRET_KEY=$(python3.12 -c 'import secrets; print(secrets.token_urlsafe(50))')
DEBUG=False
ALLOWED_HOSTS=$SERVER_IP,hoowork.uz,www.hoowork.uz
DATABASE_URL=sqlite:///db.sqlite3
SECURE_SSL_REDIRECT=False
CSRF_TRUSTED_ORIGINS=http://$SERVER_IP
CORS_ALLOWED_ORIGINS=http://$SERVER_IP
TIME_ZONE=Asia/Tashkent
EOF
fi

# 5. Database and Static Files
echo "🗄️ Running migrations..."
python manage.py migrate --noinput
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput

# 6. Setup Systemd Gunicorn Service
echo "⚙️ Setting up Systemd service..."
sudo bash -c "cat <<EOF > /etc/systemd/system/$PROJECT_NAME.service
[Unit]
Description=Gunicorn instance to serve $PROJECT_NAME
After=network.target

[Service]
User=webdevaj
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment=\"PATH=$PROJECT_DIR/.venv/bin\"
ExecStart=$PROJECT_DIR/.venv/bin/gunicorn \
    --access-logfile - \
    --workers 3 \
    --bind unix:/run/$PROJECT_NAME.sock \
    core.wsgi:application

[Install]
WantedBy=multi-user.target
EOF"

sudo systemctl start $PROJECT_NAME
sudo systemctl enable $PROJECT_NAME

# 7. Setup Nginx
echo "🌐 Configuring Nginx..."
sudo bash -c "cat <<EOF > /etc/nginx/sites-available/$PROJECT_NAME
server {
    listen 80;
    server_name $SERVER_IP;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root $PROJECT_DIR;
    }

    location /media/ {
        root $PROJECT_DIR;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/$PROJECT_NAME.sock;
    }
}
EOF"

sudo ln -sf /etc/nginx/sites-available/$PROJECT_NAME /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx

echo "✅ Deployment complete! Visit http://$SERVER_IP"
