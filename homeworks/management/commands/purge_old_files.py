import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from homeworks.models import Homework, Submission

class Command(BaseCommand):
    help = 'Purges homeworks and submissions older than 2 months (60 days) and deletes physical files.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=60,
            help='Delete records older than this many days (default is 60)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        cutoff_date = timezone.now() - timedelta(days=days)

        self.stdout.write(f"Calculating files and records older than {days} days (Cutoff: {cutoff_date})...")

        # 1. Fetch and process Submissions
        submissions = Submission.objects.filter(submitted_at__lt=cutoff_date)
        sub_count = submissions.count()
        deleted_files_sub = 0

        for sub in submissions:
            if sub.file:
                try:
                    file_path = sub.file.path
                    if os.path.exists(file_path):
                        if not dry_run:
                            os.remove(file_path)
                        deleted_files_sub += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Could not delete file for submission {sub.id}: {e}"))

        if not dry_run:
            submissions.delete()

        self.stdout.write(self.style.SUCCESS(
            f"{'[DRY RUN] Would delete' if dry_run else 'Successfully deleted'} {sub_count} submissions "
            f"and {deleted_files_sub} physical submission files."
        ))

        # 2. Fetch and process Homeworks
        homeworks = Homework.objects.filter(created_at__lt=cutoff_date)
        hw_count = homeworks.count()
        deleted_files_hw = 0

        for hw in homeworks:
            if hw.file:
                try:
                    file_path = hw.file.path
                    if os.path.exists(file_path):
                        if not dry_run:
                            os.remove(file_path)
                        deleted_files_hw += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Could not delete file for homework {hw.id}: {e}"))

        if not dry_run:
            homeworks.delete()

        self.stdout.write(self.style.SUCCESS(
            f"{'[DRY RUN] Would delete' if dry_run else 'Successfully deleted'} {hw_count} homeworks "
            f"and {deleted_files_hw} physical homework files."
        ))

        self.stdout.write(self.style.SUCCESS("Purge operation completed successfully."))
