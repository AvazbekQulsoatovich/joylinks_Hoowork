from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users.views import login_view, logout_view, student_dashboard, teacher_dashboard, admin_dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('academy/', include('academy.urls')),
    path('homeworks/', include('homeworks.urls')),
    
    # Direct access views
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('student/', student_dashboard, name='student_dashboard'),
    path('teacher/', teacher_dashboard, name='teacher_dashboard'),
    path('admin-panel/', admin_dashboard, name='admin_dashboard'),
    path('', login_view),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
