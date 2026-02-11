from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, CourseViewSet, GroupViewSet, 
    HomeworkViewSet, SubmissionViewSet
)

# Create a router and register viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'groups', GroupViewSet, basename='group')
router.register(r'homeworks', HomeworkViewSet, basename='homework')
router.register(r'submissions', SubmissionViewSet, basename='submission')

# API URLs
app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
]
