from django.db.models import Avg, F
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.utils import get_student_progress, get_group_average
from academy.models import Group, Course
from homeworks.models import Homework, Submission
from .models import User

class AnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == 'STUDENT':
            return Response({
                "average_score": get_student_progress(user),
                "total_homeworks": Homework.objects.filter(group__students=user).count(),
                "submitted_count": Submission.objects.filter(student=user).count(),
                "late_submissions": Submission.objects.filter(student=user, submitted_at__gt=F('homework__deadline')).count()
            })
        
        elif user.role == 'TEACHER':
            groups = user.teaching_groups.all()
            group_data = []
            for group in groups:
                group_data.append({
                    "id": group.id,
                    "name": group.name,
                    "average_score": get_group_average(group),
                    "students_count": group.students.count()
                })
            return Response({
                "my_groups": group_data
            })
            
        elif user.role in ['ADMIN', 'MODERATOR']:
            return Response({
                "total_students": User.objects.filter(role='STUDENT').count(),
                "total_groups": Group.objects.count(),
                "total_courses": Course.objects.count(),
                "system_average": Submission.objects.aggregate(Avg('score_percent'))['score_percent__avg'] or 0
            })
        
        return Response({"error": "No analytics for your role"}, status=400)
