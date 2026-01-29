from django.db import models
from django.conf import settings
from academy.models import Group

class Homework(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    deadline = models.DateTimeField()
    max_score = models.IntegerField(default=100)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='homeworks')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_homeworks'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    sequence = models.IntegerField(default=1)

    class Meta:
        ordering = ['sequence', 'created_at']

    def __str__(self):
        return f"{self.title} - {self.group.name}"

class Submission(models.Model):
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='submissions'
    )
    content = models.TextField(blank=True)
    file = models.FileField(upload_to='submissions/', blank=True, null=True)
    is_code = models.BooleanField(default=False, verbose_name="Kod sifatida topshirilgan")
    code_language = models.CharField(max_length=50, blank=True, default='python')
    score_percent = models.IntegerField(default=0)
    is_graded = models.BooleanField(default=False)
    teacher_comment = models.TextField(blank=True, verbose_name="O'qituvchi izohi")
    submitted_at = models.DateTimeField(auto_now_add=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='graded_submissions'
    )

    class Meta:
        unique_together = ('homework', 'student')

    def __str__(self):
        return f"{self.student.username} - {self.homework.title}"

    @property
    def is_late(self):
        return self.submitted_at > self.homework.deadline


class Notification(models.Model):
    """Foydalanuvchilarga ogohlantirish yuborish uchun"""
    
    class NotificationType(models.TextChoices):
        DEADLINE_WARNING = 'DEADLINE', 'Deadline ogohlantirish'
        NEW_HOMEWORK = 'NEW_HW', 'Yangi vazifa'
        GRADED = 'GRADED', 'Baholandi'
        SYSTEM = 'SYSTEM', 'Tizim xabari'
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    related_homework = models.ForeignKey(
        Homework,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"

