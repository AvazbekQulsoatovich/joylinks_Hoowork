from django.urls import path
from .views import (
    login_view, logout_view, 
    student_dashboard, teacher_dashboard, admin_dashboard,
    UserListView, UserCreateView, UserUpdateView, UserDeleteView, UserDetailView,
    toggle_user_status, change_user_password
)

urlpatterns = [
    # User management (Admin)
    path('', UserListView.as_view(), name='user_list'),
    path('create/', UserCreateView.as_view(), name='user_create'),
    path('<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('<int:pk>/edit/', UserUpdateView.as_view(), name='user_update'),
    path('<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
    path('<int:user_id>/toggle-status/', toggle_user_status, name='toggle_user_status'),
    path('<int:user_id>/change-password/', change_user_password, name='change_user_password'),
]
