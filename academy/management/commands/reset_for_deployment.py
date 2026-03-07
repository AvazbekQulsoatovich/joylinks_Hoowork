from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from academy.models import Course, Group
from homeworks.models import Homework, Submission

User = get_user_model()

class Command(BaseCommand):
    help = 'Reset database for deployment - keeps only admin user'

    def handle(self, *args, **options):
        self.stdout.write("Starting database reset for deployment...")
        
        # Delete all users
        self.stdout.write("Deleting all users...")
        User.objects.all().delete()
        
        # Clear Academy data
        self.stdout.write("Clearing Academy data...")
        Course.objects.all().delete()
        Group.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("✓ Academy data cleared"))
        
        # Clear Homeworks data
        self.stdout.write("Clearing Homeworks data...")
        Homework.objects.all().delete()
        Submission.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("✓ Homeworks data cleared"))
        
        # Create admin user
        self.stdout.write("\nCreating admin user...")
        admin = User.objects.create_superuser(
            username='avazbek',
            password='jumanazarov2',
            email='admin@academy.com'
        )
        self.stdout.write(self.style.SUCCESS(f"✓ Admin user created: {admin.username}"))
        self.stdout.write(self.style.SUCCESS(f"  Password: jumanazarov2"))
        
        self.stdout.write(self.style.SUCCESS("\n✓ Database prepared for deployment!"))
