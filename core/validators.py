import os
from django.core.exceptions import ValidationError

def validate_file_30mb(value):
    """
    Fayl hajmini 30 MB gacha cheklash.
    """
    limit = 30 * 1024 * 1024
    if value.size > limit:
        raise ValidationError("Fayl hajmi 30 MB dan oshmasligi kerak.")

# Migration and import compatibility alias
validate_file_10mb = validate_file_30mb

def validate_file_extension(value):
    """
    Xavfsizlik uchun faqat xavfli skript va ijro etiluvchi fayllarni bloklash.
    Hamma hujjatlar (excel, word, ppt, pdf) va python (.py) fayllariga ruxsat beriladi.
    """
    ext = os.path.splitext(value.name)[1].lower()
    # Tizimga yoki foydalanuvchiga zarar yetkazuvchi skriptlar va dasturiy formatlar taqiqlanadi
    forbidden_extensions = [
        '.apk', '.exe', '.bat', '.sh', '.php', '.cgi', '.pl', 
        '.jsp', '.asp', '.aspx', '.vbs', '.vbe', '.js', '.jse', 
        '.wsf', '.wsh', '.msc', '.scr', '.pif'
    ]
    if ext in forbidden_extensions:
        raise ValidationError(f"Xavfsizlik nuqtai nazaridan {ext} formatidagi fayllarni yuklash taqiqlangan.")
