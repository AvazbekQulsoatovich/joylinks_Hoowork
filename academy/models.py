from django.db import models
from django.conf import settings

class Course(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Group(models.Model):
    name = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='groups')
    teachers = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        related_name='teaching_groups',
        limit_choices_to={'role': 'TEACHER'}
    )
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        related_name='study_groups',
        limit_choices_to={'role': 'STUDENT'}
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.course.name})"
