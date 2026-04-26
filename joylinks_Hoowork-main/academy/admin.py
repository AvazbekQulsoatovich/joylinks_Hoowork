from django.contrib import admin
from .models import Course, Group, Certificate, MarketProduct, MarketPurchase

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'created_at')
    list_filter = ('course',)
    filter_horizontal = ('teachers', 'students')

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'issued_at')
    list_filter = ('course', 'issued_at')
    search_fields = ('student__username', 'course__name')


@admin.register(MarketProduct)
class MarketProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_coins', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(MarketPurchase)
class MarketPurchaseAdmin(admin.ModelAdmin):
    list_display = ('student', 'product', 'coins_spent', 'admin_confirmed', 'created_at')
    list_filter = ('admin_confirmed', 'created_at')
    search_fields = ('student__username', 'product__name')
