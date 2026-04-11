from django.db import models
from django.conf import settings
from academy.models import Group

from django.core.exceptions import ValidationError


from core.validators import validate_file_10mb, validate_file_extension
from core.image_processing import convert_to_webp

# Keep old names as aliases for migration compatibility
validate_file_size_7mb = validate_file_10mb
validate_file_size_5mb = validate_file_10mb


class Homework(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    file = models.FileField(
        upload_to="homework_files/",
        blank=True,
        null=True,
        validators=[validate_file_10mb, validate_file_extension],
    )
    deadline = models.DateTimeField(db_index=True)
    max_score = models.IntegerField(default=100)
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="homeworks",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_homeworks",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    sequence = models.IntegerField(default=1)

    def save(self, *args, **kwargs):
        if self.file and hasattr(self.file, 'file') and self.file.name.lower().endswith(('.jpg', '.jpeg', '.png')):
            self.file = convert_to_webp(self.file)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.group.name}"


class Submission(models.Model):
    homework = models.ForeignKey(
        Homework,
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    content = models.TextField(blank=True)
    file = models.FileField(
        upload_to="submissions/",
        blank=True,
        null=True,
        validators=[validate_file_10mb, validate_file_extension],
    )
    is_code = models.BooleanField(
        default=False,
        verbose_name="Kod sifatida topshirilgan",
    )
    code_language = models.CharField(max_length=50, blank=True, default="python")
    score_percent = models.IntegerField(default=0)
    is_graded = models.BooleanField(default=False, db_index=True)
    teacher_comment = models.TextField(
        blank=True,
        verbose_name="O'qituvchi izohi",
    )
    submitted_at = models.DateTimeField(auto_now_add=True, db_index=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="graded_submissions",
    )
    # Coin reward info (for "Mening tangalarim")
    coin_rewarded = models.BooleanField(default=False, db_index=True)
    coin_amount_awarded = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.file and hasattr(self.file, 'file') and self.file.name.lower().endswith(('.jpg', '.jpeg', '.png')):
            self.file = convert_to_webp(self.file)
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ("homework", "student")

    def __str__(self):
        return f"{self.student.username} - {self.homework.title}"

    @property
    def is_late(self):
        return self.submitted_at > self.homework.deadline


class Notification(models.Model):
    """Foydalanuvchilarga ogohlantirish yuborish uchun"""

    class NotificationType(models.TextChoices):
        DEADLINE_WARNING = "DEADLINE", "Deadline ogohlantirish"
        NEW_HOMEWORK = "NEW_HW", "Yangi vazifa"
        GRADED = "GRADED", "Baholandi"
        SYSTEM = "SYSTEM", "Tizim xabari"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM,
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False, db_index=True)
    related_homework = models.ForeignKey(
        Homework,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.title}"

