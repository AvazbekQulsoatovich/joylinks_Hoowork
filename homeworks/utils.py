from django.utils import timezone
from .models import Homework, Submission

def auto_grade_missed_homeworks(student):
    """
    Checks all homeworks for the student's groups.
    If deadline passed and no submission exists, create a 0% submission.
    """
    groups = student.study_groups.all()
    homeworks = Homework.objects.filter(group__in=groups, deadline__lt=timezone.now())
    
    for hw in homeworks:
        if not Submission.objects.filter(homework=hw, student=student).exists():
            Submission.objects.create(
                homework=hw,
                student=student,
                score_percent=0,
                is_graded=True,
                content="Avtomatik 0% (Muddat o'tgan)"
            )

def is_homework_locked(student, homework):
    """
    Content locking logic: student can only access homework if 
    all previous homeworks in the same group (by sequence) have been submitted.
    """
    previous_homeworks = Homework.objects.filter(
        group=homework.group,
        sequence__lt=homework.sequence
    )
    
    for prev_hw in previous_homeworks:
        submission = Submission.objects.filter(homework=prev_hw, student=student).first()
        if not submission or (submission.is_graded and submission.score_percent == 0):
            # If 0% due to missing deadline, it might still unlock if we allow it.
            # But the requirement says "vazifa bajarilgandan keyin".
            # Let's assume ANY submission (even 0% if deadline passed) unlocks it?
            # Or better: Must be submitted or deadline passed.
            if not submission:
                return True
    return False
