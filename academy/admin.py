from django.contrib import admin
from .models import Course, Group

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'created_at')
    list_filter = ('course',)
    filter_horizontal = ('teachers', 'students')
