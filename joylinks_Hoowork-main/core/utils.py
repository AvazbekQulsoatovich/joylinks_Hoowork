from django.db.models import Avg, Sum, Count
from homeworks.models import Homework, Submission
from django.utils import timezone

def get_student_progress(student):
    """
    Calculates average score and progress for a student.
    Every homework in their groups is considered 100 max.
    """
    groups = student.study_groups.all()
    total_homeworks = Homework.objects.filter(group__in=groups).count()
    if total_homeworks == 0:
        return 0
    
    # Sum of scores from submissions
    scored_sum = Submission.objects.filter(student=student).aggregate(Sum('score_percent'))['score_percent__sum'] or 0
    
    # We divide by total homeworks available to them (including ones they missed)
    average = scored_sum / total_homeworks
    return round(average, 2)

def get_group_average(group):
    # Total homeworks assigned to this group
    homework_ids = group.homeworks.values_list('id', flat=True)
    if not homework_ids:
        return 0
    
    # Total students in this group
    students = group.students.all()
    if not students.exists():
        return 0
    
    total_score = 0
    for student in students:
        total_score += get_student_progress(student)
        
    return round(total_score / students.count(), 2)

def update_missed_homeworks():
    """
    Finds homeworks past deadline where student didn't submit and creates 0% submissions.
    """
    now = timezone.now()
    late_homeworks = Homework.objects.filter(deadline__lt=now)
    
    for hw in late_homeworks:
        students = hw.group.students.all()
        for student in students:
            if not Submission.objects.filter(homework=hw, student=student).exists():
                Submission.objects.create(
                    homework=hw,
                    student=student,
                    score_percent=0,
                    is_graded=True,
                    content="Automatically graded 0% due to missed deadline."
                )
