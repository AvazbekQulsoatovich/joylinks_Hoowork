from django.db import transaction
from django.utils import timezone

from .models import Homework, Submission
from users.models import User


from django.core.cache import cache

def auto_grade_missed_homeworks(student):
    """
    Checks all homeworks for the student's groups.
    Throttled: runs at most once every 10 minutes per student.
    """
    cache_key = f"auto_grade_throttled_{student.pk}"
    if cache.get(cache_key):
        return
    
    # Run the logic
    # Find homeworks that are past deadline and don't have a submission from this student
    missed_homeworks = Homework.objects.filter(
        group__students=student,
        deadline__lt=timezone.now()
    ).exclude(submissions__student=student)

    for hw in missed_homeworks:
        with transaction.atomic():
            # Double check inside transaction if a submission exists (to avoid race conditions)
            if not Submission.objects.filter(homework=hw, student=student).exists():
                Submission.objects.create(
                    homework=hw,
                    student=student,
                    score_percent=0,
                    is_graded=True,
                    content="Avtomatik 0% (Muddat o'tgan)",
                    coin_rewarded=True,
                    coin_amount_awarded=0
                )
                
                # Penalty logic
                s_user = User.objects.select_for_update().get(pk=student.pk)
                if s_user.coin_balance > 0:
                    s_user.coin_balance -= 1
                    s_user.save(update_fields=['coin_balance'])
                    
                    teacher = hw.group.teachers.first()
                    receiver = teacher if teacher else User.objects.filter(role=User.Role.ADMIN).first()
                    
                    if receiver:
                        r_user = User.objects.select_for_update().get(pk=receiver.pk)
                        r_user.coin_balance = (r_user.coin_balance or 0) + 1
                        r_user.save(update_fields=['coin_balance'])
    
    # Set throttle for 10 minutes
    cache.set(cache_key, True, 600)


def is_homework_locked_optimized(student, homework, submitted_hw_ids):
    """
    Optimized version of locking logic using a pre-fetched set of submitted IDs.
    """
    previous_homeworks = Homework.objects.filter(
        group=homework.group,
        sequence__lt=homework.sequence,
    ).only('id', 'deadline').order_by('sequence')

    for prev_hw in previous_homeworks:
        if prev_hw.id not in submitted_hw_ids:
            # If not submitted, check if it was missed (deadline passed)
            if prev_hw.deadline > timezone.now():
                return True
    return False


def is_homework_locked(student, homework):
    """
    Compatibility wrapper for old single-query calls.
    WARNING: This causes N+1 if used in loops.
    """
    submitted_ids = set(Submission.objects.filter(student=student).values_list('homework_id', flat=True))
    return is_homework_locked_optimized(student, homework, submitted_ids)


def award_coins_for_submission(submission: Submission, graded_by: User) -> int:
    """
    Baholashdan so'ng tanga berish logikasi.

    - 95% dan yuqori: 3 tanga
    - 75% dan yuqori: 2 tanga
    - 50% dan yuqori: 1 tanga
    - Aks holda: 0

    Tangalar har doim o'qituvchi (yoki admin) balansidan olinadi va
    o'quvchiga o'tkaziladi. Balans manfiy bo'lishiga yo'l qo'yilmaydi.
    """
    if submission.coin_rewarded:
        return submission.coin_amount_awarded

    if not graded_by or graded_by.role not in [User.Role.TEACHER, User.Role.ADMIN]:
        return 0

    score = submission.score_percent or 0
    if score >= 95:
        reward = 3
    elif score >= 75:
        reward = 2
    elif score >= 50:
        reward = 1
    else:
        reward = 0

    if reward <= 0:
        return 0

    with transaction.atomic():
        # Yangi qiymatlarni olish uchun obyektlarni yangilab olamiz
        teacher = User.objects.select_for_update().get(pk=graded_by.pk)
        student = User.objects.select_for_update().get(pk=submission.student.pk)

        available = max(teacher.coin_balance or 0, 0)
        actual_reward = min(reward, available)
        if actual_reward <= 0:
            return 0

        teacher.coin_balance = available - actual_reward
        student.coin_balance = max(student.coin_balance or 0, 0) + actual_reward
        teacher.save(update_fields=["coin_balance"])
        student.save(update_fields=["coin_balance"])

        submission.coin_rewarded = True
        submission.coin_amount_awarded = actual_reward
        submission.save(update_fields=["coin_rewarded", "coin_amount_awarded"])

    return actual_reward

