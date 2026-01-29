from django.contrib import admin
from .models import Homework, Submission, Notification

@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'group', 'deadline', 'sequence', 'created_by')
    list_filter = ('group', 'deadline', 'created_by')
    search_fields = ('title', 'description')

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'homework', 'score_percent', 'is_graded', 'is_code', 'submitted_at')
    list_filter = ('is_graded', 'is_code', 'submitted_at')
    search_fields = ('student__username', 'homework__title')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')

