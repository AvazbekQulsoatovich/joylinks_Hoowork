from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", _("Admin")
        MODERATOR = "MODERATOR", _("Moderator")
        TEACHER = "TEACHER", _("Teacher")
        STUDENT = "STUDENT", _("Student")

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        db_index=True,
    )
    phone = models.CharField(max_length=15, blank=True, null=True)
    coin_balance = models.PositiveBigIntegerField(default=0)

    def save(self, *args, **kwargs):
        # Admins always get 1 trillion coins if they don't have enough
        if self.role == self.Role.ADMIN and (self.coin_balance is None or self.coin_balance < 1000000000000):
            self.coin_balance = 1000000000000
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def display_coin_balance(self) -> int:
        """
        Helper for templates – always returns non-negative balance.
        """
        return max(self.coin_balance or 0, 0)
    @property
    def unread_notifications_count(self) -> int:
        """
        Returns the number of unread notifications for the user.
        """
        return self.notifications.filter(is_read=False).count()
