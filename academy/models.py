from django.db import models
from django.conf import settings
from core.validators import validate_file_10mb, validate_file_extension
from core.image_processing import convert_to_webp


class Course(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=255)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="groups",
    )
    teachers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="teaching_groups",
        limit_choices_to={"role": "TEACHER"},
    )
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="study_groups",
        limit_choices_to={"role": "STUDENT"},
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"{self.name} ({self.course.name})"


class Certificate(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="certificates",
        limit_choices_to={"role": "STUDENT"},
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="certificates",
    )
    file = models.FileField(
        upload_to="certificates/",
        blank=True,
        null=True,
        validators=[validate_file_10mb, validate_file_extension]
    )
    issued_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.file and hasattr(self.file, 'file') and self.file.name.lower().endswith(('.jpg', '.jpeg', '.png')):
            self.file = convert_to_webp(self.file)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Certificate for {self.student.username} - {self.course.name}"


class MarketProduct(models.Model):
    """
    Marketdagi mahsulotlar (faqat admin CRUD qiladi).
    Narx tangalarda ko'rsatiladi.
    """

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price_coins = models.PositiveIntegerField()
    image = models.ImageField(
        upload_to="market_products/",
        blank=True,
        null=True,
        validators=[validate_file_10mb, validate_file_extension]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def save(self, *args, **kwargs):
        if self.image and hasattr(self.image, 'file') and self.image.name.lower().endswith(('.jpg', '.jpeg', '.png')):
            self.image = convert_to_webp(self.image)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.price_coins} tanga)"


class MarketPurchase(models.Model):
    """
    O'quvchilar tomonidan marketdan qilingan xaridlar.
    """

    product = models.ForeignKey(
        MarketProduct,
        on_delete=models.CASCADE,
        related_name="purchases",
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="market_purchases",
        limit_choices_to={"role": "STUDENT"},
    )
    coins_spent = models.PositiveIntegerField()
    admin_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        status = "(tasdiqlandi)" if self.admin_confirmed else "(kutmoqda)"
        return f"{self.student.username} -> {self.product.name} ({self.coins_spent} tanga) {status}"

