import os
from django.core.exceptions import ValidationError

def validate_file_10mb(value):
    """
    Fayl hajmini 10 MB gacha cheklash.
    """
    limit = 10 * 1024 * 1024
    if value.size > limit:
        raise ValidationError("Fayl hajmi 10 MB dan oshmasligi kerak.")

def validate_file_extension(value):
    """
    Dasturiy (.apk, .exe) fayllardan tashqari deyarli barcha formatlarni qabul qilish.
    """
    ext = os.path.splitext(value.name)[1].lower()
    # Foydalanuvchi talabiga ko'ra aynan .apk bloklanadi
    forbidden_extensions = ['.apk', '.exe', '.bat', '.sh']
    if ext in forbidden_extensions:
        raise ValidationError(f"Xavfsizlik nuqtai nazaridan {ext} formatidagi fayllarni yuklash taqiqlangan.")
