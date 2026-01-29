from django.urls import path
from .views import (
    # Course views
    CourseListView, CourseDetailView, CourseCreateView, 
    CourseUpdateView, CourseDeleteView,
    # Group views
    GroupListView, GroupDetailView, GroupCreateView,
    GroupUpdateView, GroupDeleteView,
    # Student management
    add_students_to_group, remove_student_from_group, change_group_teacher
)

urlpatterns = [
    # Courses
    path('courses/', CourseListView.as_view(), name='course_list'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course_detail'),
    path('courses/create/', CourseCreateView.as_view(), name='course_create'),
    path('courses/<int:pk>/edit/', CourseUpdateView.as_view(), name='course_update'),
    path('courses/<int:pk>/delete/', CourseDeleteView.as_view(), name='course_delete'),
    
    # Groups
    path('groups/', GroupListView.as_view(), name='group_list'),
    path('groups/<int:pk>/', GroupDetailView.as_view(), name='group_detail'),
    path('groups/create/', GroupCreateView.as_view(), name='group_create'),
    path('groups/<int:pk>/edit/', GroupUpdateView.as_view(), name='group_update'),
    path('groups/<int:pk>/delete/', GroupDeleteView.as_view(), name='group_delete'),
    
    # Student management
    path('groups/<int:group_id>/add-students/', add_students_to_group, name='add_students_to_group'),
    path('groups/<int:group_id>/remove-student/<int:student_id>/', remove_student_from_group, name='remove_student_from_group'),
    path('groups/<int:group_id>/change-teacher/', change_group_teacher, name='change_group_teacher'),
]
