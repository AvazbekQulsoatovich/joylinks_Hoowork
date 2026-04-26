# setup_test_data.py
from users.models import User
def ensure_admin_coins():
    admin = User.objects.filter(role='ADMIN').first()
    if admin:
        admin.coin_balance = 100_000_000
        admin.save(update_fields=['coin_balance'])