from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from users.views import login_view, logout_view, student_dashboard, teacher_dashboard, admin_dashboard, redirect_by_role
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('academy/', include('academy.urls')),
    path('homeworks/', include('homeworks.urls')),
    
    # API endpoints (v1)
    path('api/v1/', include('api.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Direct access views
    path('login/', login_view, name='login'),
    path('accounts/login/', login_view), # Handle default Django redirect
    path('logout/', logout_view, name='logout'),
    path('student/', student_dashboard, name='student_dashboard'),
    path('teacher/', teacher_dashboard, name='teacher_dashboard'),
    path('admin-panel/', admin_dashboard, name='admin_dashboard'),
    path('', login_view),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

def custom_page_not_found(request, exception=None):
    if request.user.is_authenticated:
        return redirect_by_role(request.user)
    return redirect('login')

handler404 = 'core.urls.custom_page_not_found'
