from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from homeworks.models import Homework, Submission, Notification
from users.models import User

class Command(BaseCommand):
    help = 'Check deadlines, auto-grade missed homeworks and send warnings'

    def handle(self, *args, **options):
        now = timezone.now()
        one_hour_later = now + timedelta(hours=1)
        
        # 1. Auto-grade missed homeworks (expired)
        expired_hws = Homework.objects.filter(deadline__lt=now)
        for hw in expired_hws:
            students = hw.group.students.all()
            for student in students:
                if not Submission.objects.filter(homework=hw, student=student).exists():
                    Submission.objects.create(
                        homework=hw,
                        student=student,
                        score_percent=0,
                        is_graded=True,
                        content="Muddat o'tganligi sababli tizim tomonidan 0% ball qo'yildi."
                    )
                    self.stdout.write(self.style.SUCCESS(f"Auto-graded {student.username} for HW {hw.pk}"))

        # 2. Deadline warning (1 hour left)
        upcoming_hws = Homework.objects.filter(
            deadline__gt=now,
            deadline__lte=one_hour_later
        )
        for hw in upcoming_hws:
            students = hw.group.students.all()
            for student in students:
                # Topshirmagan bo'lsa ogohlantirish
                if not Submission.objects.filter(homework=hw, student=student).exists():
                    # Allaqachon ogohlantirilganmi?
                    if not Notification.objects.filter(
                        user=student, 
                        related_homework=hw, 
                        notification_type='DEADLINE'
                    ).exists():
                        Notification.objects.create(
                            user=student,
                            notification_type='DEADLINE',
                            title='Vazifa muddati tugamoqda!',
                            message=f'"{hw.title}" vazifasini topshirishga 1 soatdan kam vaqt qoldi. Shoshiling!',
                            related_homework=hw
                        )
                        self.stdout.write(self.style.NOTICE(f"Warning sent to {student.username} for HW {hw.pk}"))

        self.stdout.write(self.style.SUCCESS('Deadline check completed.'))
