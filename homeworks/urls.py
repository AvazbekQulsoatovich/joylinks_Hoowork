from django.urls import path
from .views import (
    HomeworkListView, HomeworkDetailView, HomeworkCreateView, 
    HomeworkUpdateView, HomeworkDeleteView,
    SubmissionCreateView, SubmissionDetailView,
    GradeSubmissionView, TeacherSubmissionsView,
    group_stats_view, mark_notification_read, notifications_list
)
from .export_views import export_all_view, export_group_view, export_course_view

urlpatterns = [
    # Homework CRUD
    path('', HomeworkListView.as_view(), name='homework_list'),
    path('<int:pk>/', HomeworkDetailView.as_view(), name='homework_detail'),
    path('create/', HomeworkCreateView.as_view(), name='homework_create'),
    path('<int:pk>/edit/', HomeworkUpdateView.as_view(), name='homework_update'),
    path('<int:pk>/delete/', HomeworkDeleteView.as_view(), name='homework_delete'),
    
    # Submissions
    path('<int:homework_id>/submit/', SubmissionCreateView.as_view(), name='submission_create'),
    path('submission/<int:pk>/', SubmissionDetailView.as_view(), name='submission_detail'),
    path('submission/<int:pk>/grade/', GradeSubmissionView.as_view(), name='grade_submission'),
    path('submissions/', TeacherSubmissionsView.as_view(), name='teacher_submissions'),
    
    # Stats
    path('group/<int:group_id>/stats/', group_stats_view, name='group_stats'),
    
    # Notifications
    path('notifications/', notifications_list, name='notifications'),
    path('notifications/<int:notification_id>/read/', mark_notification_read, name='mark_notification_read'),
    
    # Excel Export
    path('export/', export_all_view, name='export_all'),
    path('export/group/<int:group_id>/', export_group_view, name='export_group'),
    path('export/course/<int:course_id>/', export_course_view, name='export_course'),
]

