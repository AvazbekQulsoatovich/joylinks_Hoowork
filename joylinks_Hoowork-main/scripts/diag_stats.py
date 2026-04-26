from homeworks.models import Submission, Homework # type: ignore
from academy.models import Group # type: ignore
from users.models import User # type: ignore
from django.db.models import Min, Max, Count, Avg # type: ignore
from django.utils import timezone # type: ignore
from datetime import timedelta

print("--- Data Diagnostic ---")
print(f"Total Users: {User.objects.count()}")
print(f"Total Groups: {Group.objects.count()}")
print(f"Total Homeworks: {Homework.objects.count()}")
print(f"Total Submissions: {Submission.objects.count()}")

last_30_days = timezone.now() - timedelta(days=30)
recent_subs = Submission.objects.filter(submitted_at__gte=last_30_days).count()
print(f"Submissions in last 30 days: {recent_subs}")

graded_subs = Submission.objects.filter(is_graded=True).count()
print(f"Graded Submissions: {graded_subs}")

if Submission.objects.exists():
    aggregate_data = Submission.objects.aggregate(min_date=Min('submitted_at'), max_date=Max('submitted_at'))
    print(f"Min Date: {aggregate_data['min_date']}")
    print(f"Max Date: {aggregate_data['max_date']}")

groups_with_scores = Group.objects.annotate(
    avg_score=Avg('homeworks__submissions__score_percent')
).filter(avg_score__gt=0).count()
print(f"Groups with average score > 0: {groups_with_scores}")
