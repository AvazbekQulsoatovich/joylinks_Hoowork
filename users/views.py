from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden
from django.db.models import Avg, Count
from homeworks.models import Homework, Submission, Notification
from homeworks.utils import auto_grade_missed_homeworks
from academy.models import Course, Group
from .models import User
from .forms import UserForm, UserUpdateForm, ChangePasswordForm


# ============== AUTHENTICATION ==============

def login_view(request):
    """Login sahifasi"""
    if request.user.is_authenticated:
        return redirect_by_role(request.user)
    
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        user = authenticate(username=username, password=password)
        if user:
            if not user.is_active:
                error = "Sizning hisobingiz bloklangan. Admin bilan bog'laning."
            else:
                login(request, user)
                messages.success(request, f"Xush kelibsiz, {user.get_full_name() or user.username}!")
                return redirect_by_role(user)
        else:
            error = "Noto'g'ri foydalanuvchi nomi yoki parol."
    
    return render(request, 'auth/login.html', {'error': error})


def redirect_by_role(user):
    """Role bo'yicha yo'naltirish"""
    if user.role == 'ADMIN':
        return redirect('admin_dashboard')
    elif user.role == 'MODERATOR':
        return redirect('admin_dashboard')
    elif user.role == 'TEACHER':
        return redirect('teacher_dashboard')
    return redirect('student_dashboard')


def logout_view(request):
    """Logout"""
    logout(request)
    messages.info(request, "Tizimdan chiqdingiz.")
    return redirect('login')


# ============== DASHBOARDS ==============

@login_required
def student_dashboard(request):
    """O'quvchi dashboardi"""
    user = request.user
    
    if user.role != 'STUDENT':
        return redirect_by_role(user)
    
    # Avtomatik 0% berish (deadline o'tgan vazifalar uchun)
    auto_grade_missed_homeworks(user)
    
    # O'quvchi guruhlari
    groups = user.study_groups.all()
    
    # Vazifalar
    homeworks = Homework.objects.filter(group__in=groups).order_by('-created_at')[:10]
    
    # Topshiriqlar
    submissions = Submission.objects.filter(student=user).select_related('homework')
    
    # Statistika
    total_homeworks = Homework.objects.filter(group__in=groups).count()
    submitted_count = submissions.count()
    graded = submissions.filter(is_graded=True)
    avg_score = graded.aggregate(avg=Avg('score_percent'))['avg'] or 0
    
    # Bildirishnomalar
    notifications = Notification.objects.filter(user=user, is_read=False)[:5]
    
    # Yaqin deadline'lar
    from django.utils import timezone
    from datetime import timedelta
    upcoming = Homework.objects.filter(
        group__in=groups,
        deadline__gt=timezone.now(),
        deadline__lt=timezone.now() + timedelta(days=3)
    ).exclude(
        submissions__student=user
    ).order_by('deadline')[:5]
    
    return render(request, 'student/dashboard.html', {
        'groups': groups,
        'homeworks': homeworks,
        'total_homeworks': total_homeworks,
        'submitted_count': submitted_count,
        'avg_score': round(avg_score, 1),
        'notifications': notifications,
        'upcoming_deadlines': upcoming,
    })


@login_required
def teacher_dashboard(request):
    """O'qituvchi dashboardi"""
    user = request.user
    
    if user.role != 'TEACHER':
        return redirect_by_role(user)
    
    # O'qituvchi guruhlari
    groups = user.teaching_groups.all()
    
    # Statistika
    total_students = sum(g.students.count() for g in groups)
    total_homeworks = Homework.objects.filter(group__in=groups).count()
    
    # Tekshirilmagan topshiriqlar
    pending_submissions = Submission.objects.filter(
        homework__group__in=groups,
        is_graded=False
    ).select_related('homework', 'student').order_by('-submitted_at')[:10]
    
    # Guruhlar statistikasi
    group_stats = []
    for group in groups:
        subs = Submission.objects.filter(homework__group=group, is_graded=True)
        avg = subs.aggregate(avg=Avg('score_percent'))['avg'] or 0
        group_stats.append({
            'group': group,
            'students': group.students.count(),
            'homeworks': Homework.objects.filter(group=group).count(),
            'avg_score': round(avg, 1),
            'pending': Submission.objects.filter(homework__group=group, is_graded=False).count()
        })
    
    return render(request, 'teacher/dashboard.html', {
        'groups': groups,
        'group_stats': group_stats,
        'total_students': total_students,
        'total_homeworks': total_homeworks,
        'pending_submissions': pending_submissions,
        'pending_count': sum(g['pending'] for g in group_stats)
    })


@login_required
def admin_dashboard(request):
    """Admin dashboardi"""
    user = request.user
    
    if user.role not in ['ADMIN', 'MODERATOR']:
        return redirect_by_role(user)
    
    # Umumiy statistika
    total_students = User.objects.filter(role='STUDENT', is_active=True).count()
    total_teachers = User.objects.filter(role='TEACHER', is_active=True).count()
    total_courses = Course.objects.count()
    total_groups = Group.objects.count()
    
    # O'rtacha o'zlashtirish
    all_subs = Submission.objects.filter(is_graded=True)
    avg_score = all_subs.aggregate(avg=Avg('score_percent'))['avg'] or 0
    
    # Kurslar statistikasi
    courses = Course.objects.all()
    course_stats = []
    for course in courses:
        groups = course.groups.all()
        student_count = sum(g.students.count() for g in groups)
        subs = Submission.objects.filter(homework__group__in=groups, is_graded=True)
        course_avg = subs.aggregate(avg=Avg('score_percent'))['avg'] or 0
        course_stats.append({
            'course': course,
            'groups': groups.count(),
            'students': student_count,
            'avg_score': round(course_avg, 1)
        })
    
    # So'nggi foydalanuvchilar
    recent_users = User.objects.order_by('-date_joined')[:5]
    
    # So'nggi topshiriqlar
    recent_submissions = Submission.objects.select_related(
        'student', 'homework'
    ).order_by('-submitted_at')[:5]
    
    return render(request, 'admin/dashboard.html', {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_courses': total_courses,
        'total_groups': total_groups,
        'avg_score': round(avg_score, 1),
        'course_stats': course_stats,
        'recent_users': recent_users,
        'recent_submissions': recent_submissions,
        'is_moderator': user.role == 'MODERATOR'
    })


# ============== USER MANAGEMENT ==============

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == 'ADMIN'


class UserListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """Foydalanuvchilar ro'yxati"""
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    
    def get_queryset(self):
        queryset = User.objects.all().order_by('role', 'last_name', 'first_name')
        
        # Filtrlash
        role = self.request.GET.get('role')
        search = self.request.GET.get('search')
        status = self.request.GET.get('status')
        
        if role:
            queryset = queryset.filter(role=role)
        if search:
            queryset = queryset.filter(
                username__icontains=search
            ) | queryset.filter(
                first_name__icontains=search
            ) | queryset.filter(
                last_name__icontains=search
            )
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'blocked':
            queryset = queryset.filter(is_active=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['roles'] = User.Role.choices
        context['current_role'] = self.request.GET.get('role', '')
        context['current_search'] = self.request.GET.get('search', '')
        context['current_status'] = self.request.GET.get('status', '')
        
        # Statistika
        context['admin_count'] = User.objects.filter(role='ADMIN').count()
        context['teacher_count'] = User.objects.filter(role='TEACHER').count()
        context['student_count'] = User.objects.filter(role='STUDENT').count()
        context['blocked_count'] = User.objects.filter(is_active=False).count()
        
        return context


class UserCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Yangi foydalanuvchi yaratish"""
    model = User
    form_class = UserForm
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('user_list')
    
    def form_valid(self, form):
        messages.success(self.request, "Foydalanuvchi muvaffaqiyatli yaratildi!")
        return super().form_valid(form)


class UserUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Foydalanuvchini tahrirlash"""
    model = User
    form_class = UserUpdateForm
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('user_list')
    
    def form_valid(self, form):
        messages.success(self.request, "Foydalanuvchi yangilandi!")
        return super().form_valid(form)


class UserDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Foydalanuvchini o'chirish"""
    model = User
    template_name = 'users/user_confirm_delete.html'
    success_url = reverse_lazy('user_list')
    
    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        messages.success(request, f"{user.username} o'chirildi!")
        return super().delete(request, *args, **kwargs)


@login_required
def toggle_user_status(request, user_id):
    """Foydalanuvchini bloklash/faollashtirish"""
    if request.user.role != 'ADMIN':
        return HttpResponseForbidden("Faqat Admin.")
    
    user = get_object_or_404(User, pk=user_id)
    
    if user == request.user:
        messages.error(request, "O'zingizni bloklashingiz mumkin emas!")
        return redirect('user_list')
    
    user.is_active = not user.is_active
    user.save()
    
    status = "faollashtirildi" if user.is_active else "bloklandi"
    messages.success(request, f"{user.username} {status}!")
    
    return redirect('user_list')


@login_required
def change_user_password(request, user_id):
    """Foydalanuvchi parolini o'zgartirish"""
    if request.user.role != 'ADMIN':
        return HttpResponseForbidden("Faqat Admin.")
    
    user = get_object_or_404(User, pk=user_id)
    
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['new_password'])
            user.save()
            messages.success(request, f"{user.username} paroli o'zgartirildi!")
            return redirect('user_list')
    else:
        form = ChangePasswordForm()
    
    return render(request, 'users/change_password.html', {
        'form': form,
        'target_user': user
    })


class UserDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    """Foydalanuvchi profili"""
    model = User
    template_name = 'users/user_detail.html'
    context_object_name = 'target_user'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        
        if user.role == 'STUDENT':
            context['groups'] = user.study_groups.all()
            subs = Submission.objects.filter(student=user, is_graded=True)
            context['avg_score'] = subs.aggregate(avg=Avg('score_percent'))['avg'] or 0
            context['submission_count'] = subs.count()
        elif user.role == 'TEACHER':
            context['groups'] = user.teaching_groups.all()
            context['homework_count'] = Homework.objects.filter(created_by=user).count()
        
        return context
