from django.urls import path
from .views import (
    login_view, logout_view, 
    student_dashboard, teacher_dashboard, admin_dashboard,
    UserListView, UserCreateView, UserUpdateView, UserDeleteView, UserDetailView,
    toggle_user_status, change_user_password,
    profile_view, ProfileUpdateView, change_own_password,
    request_coins, admin_transfer_coins,
    notifications_view, settings_view, statistics_view
)

urlpatterns = [
    # User management (Admin)
    path('', UserListView.as_view(), name='user_list'),
    path('create/', UserCreateView.as_view(), name='user_create'),
    path('statistics/', statistics_view, name='statistics'),
    path('<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('<int:pk>/edit/', UserUpdateView.as_view(), name='user_update'),
    path('<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
    path('<int:user_id>/toggle-status/', toggle_user_status, name='toggle_user_status'),
    path('<int:user_id>/change-password/', change_user_password, name='change_user_password'),
    
    # Profile (Self)
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),
    path('profile/change-password/', change_own_password, name='change_own_password'),
    # coin-related actions
    path('request-coins/', request_coins, name='request_coins'),
    path('admin/transfer-coins/', admin_transfer_coins, name='admin_transfer_coins'),
    
    # Notifications and Settings
    path('notifications/', notifications_view, name='notifications'),
    path('settings/', settings_view, name='settings'),
]

