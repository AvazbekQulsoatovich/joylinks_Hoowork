from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users.views import login_view, logout_view, student_dashboard, teacher_dashboard, admin_dashboard
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

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
