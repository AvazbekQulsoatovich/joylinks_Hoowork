import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import User

def create_rich_admin(username, password, email=None):
    if User.objects.filter(username=username).exists():
        print(f"User {username} already exists. Updating balance...")
        user = User.objects.get(username=username)
    else:
        print(f"Creating superuser {username}...")
        user = User.objects.create_superuser(username=username, password=password, email=email)
    
    user.coin_balance = 100000000000
    user.save()
    print(f"Success! {username} now has {user.coin_balance} coins.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python create_admin.py <username> <password> [email]")
    else:
        email = sys.argv[3] if len(sys.argv) > 3 else ""
        create_rich_admin(sys.argv[1], sys.argv[2], email)
