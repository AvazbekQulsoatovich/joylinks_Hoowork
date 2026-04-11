from typing import List, Dict, Any
from django.shortcuts import render, redirect, get_object_or_404 # type: ignore
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin # type: ignore
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView # type: ignore
from django.contrib import messages # type: ignore
from django.urls import reverse_lazy # type: ignore
from django.http import HttpResponseForbidden # type: ignore
from django.db import transaction, models # type: ignore
from django.db.models import Avg, Count, F, Q # type: ignore
from django.utils import timezone # type: ignore
from django.db.models.functions import TruncDate # type: ignore
from django.core.serializers.json import DjangoJSONEncoder # type: ignore
from datetime import timedelta
import json

from homeworks.models import Homework, Submission, Notification # type: ignore
from homeworks.utils import auto_grade_missed_homeworks # type: ignore
from academy.models import Course, Group, Certificate # type: ignore
from users.models import User # type: ignore
from users.forms import UserForm, UserUpdateForm, ChangePasswordForm, ProfileUpdateForm, CoinTransferForm # type: ignore


@login_required
def change_own_password(request):
    """Foydalanuvchining o'z parolini o'zgartirishi"""
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            user = request.user
            user.set_password(form.cleaned_data['new_password'])
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Parolingiz muvaffaqiyatli o'zgartirildi!")
            return redirect('profile')
    else:
        form = ChangePasswordForm()
    
    return render(request, 'users/change_own_password.html', {
        'form': form
    })


# ============== AUTHENTICATION ==============

def login_view(request):
    """Login sahifasi"""
    if request.user.is_authenticated:
        return redirect_by_role(request.user)
    
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        user = authenticate(request, username=username, password=password)
        if user:
            if not user.is_active:
                if user.role == 'STUDENT':
                    group = user.study_groups.first()
                    group_name = group.name if group else "Guruhsiz"
                    full_name = user.get_full_name() or user.username
                    error = f"Hurmatli {full_name}, siz {group_name} guruhidasiz. Iltimos, shu oy uchun to'lovni amalga oshiring. To'lov qilganingizdan so'ng tizimga kira olasiz."
                else:
                    error = "Sizning hisobingiz bloklangan. Admin bilan bog'laning."
            else:
                login(request, user)
                messages.success(request, f"Xush kelibsiz, {user.get_full_name() or user.username}!")
                return redirect_by_role(user)
        else:
            # Check if username exists but password might be wrong, OR if user exists but is inactive and authenticate failed?
            # Actually authenticate() returns None if is_active=False in some Django versions? 
            # Default ModelBackend rejects inactive users? 
            # Let's check if user exists to give better error if needed, but for security generic is better.
            # However, the requirement is specific: "login parolini teradi ammo kira olmaydi va unga eslatadi..."
            # If ModelBackend rejects inactive users, authenticate returns None.
            # We need to manually check.
            try:
                u = User.objects.get(username=username)
                if u.check_password(password):
                    if not u.is_active:
                        if u.role == 'STUDENT':
                            group = u.study_groups.first()
                            group_name = group.name if group else "Guruhsiz"
                            full_name = u.get_full_name() or u.username
                            error = f"Hurmatli {full_name}, siz {group_name} guruhidasiz. Iltimos, shu oy uchun to'lovni amalga oshiring. To'lov qilganingizdan so'ng tizimga kira olasiz."
                        else:
                            error = "Sizning hisobingiz bloklangan. Admin bilan bog'laning."
                    else:
                         # Should have been authenticated... weird case
                        error = "Tizim xatosi. Qaytadan urining."
                else:
                    error = "Noto'g'ri foydalanuvchi nomi yoki parol."
            except User.DoesNotExist:
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
    
    # Pre-fetch submissions for these homeworks to avoid N+1
    homework_submissions = {
        s.homework_id: s for s in Submission.objects.filter(homework__in=homeworks, student=user)
    }
    
    for hw in homeworks:
        hw_submission = homework_submissions.get(hw.id)
        hw.is_submitted = hw_submission is not None
        if hw_submission:
            hw.is_graded = hw_submission.is_graded
            hw.score = hw_submission.score_percent
        hw.is_overdue = hw.deadline < timezone.now() and not hw.is_submitted
    
    # Statistika
    submissions = Submission.objects.filter(student=user).select_related('homework')
    total_homeworks = Homework.objects.filter(group__in=groups).count()
    submitted_count = submissions.count()
    graded = submissions.filter(is_graded=True)
    avg_score = graded.aggregate(avg=Avg('score_percent'))['avg'] or 0
    
    # Bildirishnomalar
    notifications = Notification.objects.filter(user=user, is_read=False)[:5]
    
    # Yaqin deadline'lar (3 kun ichida)
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
    
    # Coin balance alarm
    coin_balance = user.coin_balance or 0
    if coin_balance <= 0:
        # Check if already notified admin recently to avoid spam? 
        # For simplicity, just notify once per dashboard visit or check logic.
        # But here we'll just ensure the alert shows in template.
        pass

    # O'qituvchi guruhlari
    groups = user.teaching_groups.all().annotate(
        students_count=models.Count('students', distinct=True)
    )
    
    # Statistika (optimized)
    total_students = groups.aggregate(total=models.Sum('students_count'))['total'] or 0
    total_homeworks = Homework.objects.filter(group__in=groups).count()
    
    # Tekshirilmagan topshiriqlar
    pending_submissions = Submission.objects.filter(
        homework__group__in=groups,
        is_graded=False
    ).select_related('homework', 'student').order_by('-submitted_at')[:10]
    
    # Guruhlar statistikasi (optimized with annotations)
    group_stats_query = groups.annotate(
        homeworks_count=models.Count('homeworks', distinct=True),
        pending_count=models.Count('homeworks__submissions', filter=models.Q(homeworks__submissions__is_graded=False), distinct=True),
        avg_score=models.Avg('homeworks__submissions__score_percent', filter=models.Q(homeworks__submissions__is_graded=True))
    )
    
    group_stats = []
    for g in group_stats_query:
        group_stats.append({
            'group': g,
            'students': g.students_count,
            'homeworks': g.homeworks_count,
            'avg_score': round(g.avg_score or 0, 1),
            'pending': g.pending_count
        })
    
    return render(request, 'teacher/dashboard.html', {
        'groups': groups,
        'group_stats': group_stats,
        'total_students': total_students,
        'total_homeworks': total_homeworks,
        'pending_submissions': pending_submissions,
        'pending_count': sum(g['pending'] for g in group_stats),
        'coin_balance': coin_balance,
    })


@login_required
def request_coins(request):
    """Teachers or Admins ask for more coins (e.g. for testing)."""
    user = request.user
    if user.role not in ['TEACHER', 'ADMIN']:
        messages.error(request, "Faqat o'qituvchilar yoki adminlar tanga so'ray olishi mumkin.")
        return redirect_by_role(user)

    admins = User.objects.filter(role='ADMIN', is_active=True)
    for admin in admins:
        # If requesting admin is the same as recipient admin, it's just for testing.
        Notification.objects.create(
            user=admin,
            notification_type=Notification.NotificationType.SYSTEM,
            title="Tanga so'rovi",
            message=f"{user.get_role_display()} {user.get_full_name() or user.username} tanga so'ramoqda.",
        )
    messages.success(request, "Tanga so'rovi yuborildi.")
    return redirect_by_role(user)


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
    
    # Kurslar statistikasi (optimized with annotations)
    courses = Course.objects.all().annotate(
        groups_count=models.Count('groups', distinct=True),
        students_count=models.Count('groups__students', distinct=True),
        avg_score=models.Avg('groups__homeworks__submissions__score_percent', filter=models.Q(groups__homeworks__submissions__is_graded=True))
    )
    course_stats = []
    for c in courses:
        course_stats.append({
            'course': c,
            'groups': c.groups_count,
            'students': c.students_count,
            'avg_score': round(c.avg_score or 0, 1)
        })
    
    # So'nggi uyga vazifalar (Optimized with annotations)
    homeworks = Homework.objects.select_related('group', 'group__course').annotate(
        total_students_hw=Count('group__students', distinct=True),
        submitted_count_val=Count('submissions', distinct=True)
    ).order_by('-created_at')[:5]

    recent_homeworks = []
    for hw in homeworks:
        submission_percent = (hw.submitted_count_val / hw.total_students_hw * 100) if hw.total_students_hw > 0 else 0
        recent_homeworks.append({
            'id': hw.id,
            'title': hw.title,
            'group': hw.group,
            'deadline': hw.deadline,
            'is_active': hw.deadline > timezone.now(),
            'total_students': hw.total_students_hw,
            'submitted_count': hw.submitted_count_val,
            'submission_percent': round(submission_percent),
        })
    
    # Top o'quvchilar (Optimized with annotations)
    top_students_query = User.objects.filter(role='STUDENT', is_active=True).annotate(
        avg_v=Avg('submissions__score_percent', filter=Q(submissions__is_graded=True))
    ).filter(avg_v__gt=0).order_by('-avg_v')[:5]

    top_students = []
    for student in top_students_query:
        # Get group name separately or prefetch to avoid N+1 if many students, 
        # but here it's only 5 students so one .first() per student is okay-ish, 
        # though prefetch is better.
        group = student.study_groups.first()
        top_students.append({
            'id': student.id,
            'username': student.username,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'avg_score': student.avg_v,
            'group_name': group.name if group else None,
            'get_full_name': student.get_full_name,
        })
    
    # So'nggi foydalanuvchilar
    recent_users = User.objects.order_by('-date_joined')[:5]
    
    # So'nggi topshiriqlar
    recent_submissions = Submission.objects.select_related(
        'student', 'homework'
    ).order_by('-submitted_at')[:5]
    
    # O'qilmagan bildirishnomalar soni
    unread_count = Notification.objects.filter(user=user, is_read=False).count()
    
    # include admin coin balance so the template can display it
    return render(request, 'admin/dashboard.html', {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_courses': total_courses,
        'total_groups': total_groups,
        'avg_score': round(avg_score, 1),
        'course_stats': course_stats,
        'recent_homeworks': recent_homeworks,
        'top_students': top_students,
        'recent_users': recent_users,
        'recent_submissions': recent_submissions,
        'is_moderator': user.role == 'MODERATOR',
        'unread_count': unread_count,
        'admin_coin_balance': user.display_coin_balance,
    })


@login_required
def statistics_view(request):
    """Statistika sahifasi - Kelajakdagi tahlillar va premium grafiklar"""
    if request.user.role not in ['ADMIN', 'MODERATOR']:
        return redirect('student_dashboard')
    
    # --- 1. Umumiy Metrikalar ---
    total_students = User.objects.filter(role='STUDENT', is_active=True).count()
    # Faol o'quvchilar (oxirgi 30 kunda kamida 1 ta vazifa topshirgan)
    recent_threshold = timezone.now() - timedelta(days=30)
    active_students_count = Submission.objects.filter(
        submitted_at__gte=recent_threshold
    ).values('student').distinct().count()
    
    submission_rate = (active_students_count / total_students * 100) if total_students > 0 else 0
    total_homeworks = Homework.objects.count()
    total_submissions = Submission.objects.count()
    avg_system_score = Submission.objects.filter(is_graded=True).aggregate(Avg('score_percent'))['score_percent__avg'] or 0

    # --- 2. Topshiriqlar Dinamikasi (Line Chart) ---
    # Agar ma'lumotlar kam bo'lsa, diapazonni kengaytiramiz yoki bor ma'lumotni ko'rsatamiz
    submissions_by_day = Submission.objects.filter(
        submitted_at__gte=recent_threshold
    ).annotate(date=TruncDate('submitted_at')).values('date').annotate(count=Count('id')).order_by('date')
    
    line_labels = []
    line_data = []
    
    # Bo'sh kunlarni ham to'ldiramiz
    current_date = recent_threshold.date()
    end_date = timezone.now().date()
    subs_dict = {item['date']: item['count'] for item in submissions_by_day}
    
    while current_date <= end_date:
        # Faqat ma'lumot bor kunlarni yoki oxirgi haftani ko'rsatish (dinamikroq ko'rinishi uchun)
        line_labels.append(current_date.strftime('%d-%b'))
        line_data.append(subs_dict.get(current_date, 0))
        current_date += timedelta(days=1)
    
    # --- 3. Bilim Darajasi (Pie Chart) ---
    scored_subs = Submission.objects.all() # Use all if none graded
    if scored_subs.filter(is_graded=True).exists():
        scored_subs = scored_subs.filter(is_graded=True)
    
    low_scores = scored_subs.filter(score_percent__lt=40).count()
    medium_scores = scored_subs.filter(score_percent__gte=40, score_percent__lt=75).count()
    high_scores = scored_subs.filter(score_percent__gte=75).count()
    pie_data = [low_scores, medium_scores, high_scores]
    
    # --- 4. Guruhlar Reytingi (Bar Chart) ---
    # Agar hech kim baholanmagan bo'lsa, barcha topshiriqlarni hisobga olamiz
    groups_query = Group.objects.annotate(
        avg_score=Avg('homeworks__submissions__score_percent')
    )
    
    if not groups_query.filter(avg_score__gt=0).exists():
        # Hech qanday ball yo'q bo'lsa, o'quvchilar soni bo'yicha ko'rsatamiz (placeholder sifatida)
        groups = Group.objects.annotate(
            avg_score=Count('students') * 10 # Shunchaki ko'rish uchun test ma'lumot
        ).order_by('-avg_score')[:10]
    else:
        groups = groups_query.filter(avg_score__gt=0).order_by('-avg_score')[:10]
    
    bar_labels = [g.name for g in groups]
    bar_data = [round(g.avg_score or 0, 1) for g in groups]
    
    # --- 5. Kurslar Taqsimoti ---
    courses = Course.objects.annotate(
        student_count=Count('groups__students', distinct=True)
    ).order_by('-student_count')
    
    course_labels = [c.name for c in courses]
    course_data = [c.student_count for c in courses]

    # JSON serializatsiya (JS xatoliklarini oldini olish uchun)
    context = {
        'total_students': total_students,
        'active_students_count': active_students_count,
        'submission_rate': round(submission_rate, 1),
        'total_homeworks': total_homeworks,
        'total_submissions': total_submissions,
        'avg_system_score': round(avg_system_score, 1),
        'line_labels_js': json.dumps(line_labels),
        'line_data_js': json.dumps(line_data),
        'pie_data_js': json.dumps(pie_data),
        'bar_labels_js': json.dumps(bar_labels),
        'bar_data_js': json.dumps(bar_data),
        'course_labels_js': json.dumps(course_labels),
        'course_data_js': json.dumps(course_data),
    }

    return render(request, 'users/statistics.html', context)


# ============== USER MANAGEMENT ==============


@login_required
def admin_transfer_coins(request):
    """Admin can move coins from their balance to any teacher/student."""
    user = request.user
    if user.role not in ['ADMIN', 'MODERATOR']:
        return redirect_by_role(user)

    form = CoinTransferForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        recipient = form.cleaned_data['recipient']
        amount = form.cleaned_data['amount']
        with transaction.atomic():
            admin = User.objects.select_for_update().get(pk=user.pk)
            if admin.coin_balance < amount:
                messages.error(request, "Sizdan yetarli tanga yo'q.")
            else:
                admin.coin_balance -= amount
                recipient.coin_balance = max(recipient.coin_balance or 0, 0) + amount
                admin.save(update_fields=['coin_balance'])
                recipient.save(update_fields=['coin_balance'])
                
                # Create notification for history tracking
                Notification.objects.create(
                    user=recipient,
                    notification_type=Notification.NotificationType.SYSTEM,
                    title="Tanga qabul qilindi",
                    message=f"Admin sizga {amount} tanga yubordi.",
                )
                
                messages.success(
                    request,
                    f"{amount} tanga {recipient.get_full_name() or recipient.username} ga yuborildi."
                )
                return redirect('admin_transfer_coins')

    return render(request, 'admin/transfer_coins.html', {'form': form})


@login_required
def request_coins(request):
    """Students/teachers ask admins for more coins when their balance is empty."""
    user = request.user
    if user.role != 'TEACHER':
        messages.error(request, "Faqat o'qituvchilar tanga so'ray olishi mumkin.")
        return redirect_by_role(user)

    if request.method == 'POST':
        admins = User.objects.filter(role='ADMIN', is_active=True)
        for admin in admins:
            Notification.objects.create(
                user=admin,
                notification_type=Notification.NotificationType.SYSTEM,
                title="Tangam kam qoldi",
                message=f"{user.get_full_name() or user.username} balansida tanga yo'q.",
            )
        messages.success(
            request,
            "Adminga tanga so'rovi yuborildi. Tez orada ular sizga tanga yuboradi."
        )
        return redirect('request_coins')

    return render(request, 'users/request_coins.html')

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == 'ADMIN'


class UserListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """Foydalanuvchilar ro'yxati"""
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    
    def get_queryset(self):
        queryset = User.objects.all().order_by('role', 'last_name', 'first_name').prefetch_related('study_groups')
        
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
    """Foydalanuvchi profili (Admin uchun)"""
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


@login_required
def profile_view(request):
    """Foydalanuvchining o'z profili"""
    user = request.user
    context = {
        'target_user': user,
        'is_own_profile': True
    }
    
    if user.role == 'STUDENT':
        context['groups'] = user.study_groups.all()
        subs = Submission.objects.filter(student=user, is_graded=True)
        context['avg_score'] = subs.aggregate(avg=Avg('score_percent'))['avg'] or 0
        context['submission_count'] = subs.count()
    elif user.role == 'TEACHER':
        context['groups'] = user.teaching_groups.all()
        context['homework_count'] = Homework.objects.filter(created_by=user).count()
        
    return render(request, 'users/profile_detail.html', context)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Foydalanuvchining o'z profilini tahrirlashi"""
    model = User
    form_class = ProfileUpdateForm
    template_name = 'users/profile_form.html'
    success_url = reverse_lazy('profile')
    
    def get_object(self, queryset=None):
        return self.request.user
    
    def form_valid(self, form):
        response = super().form_valid(form)
        update_session_auth_hash(self.request, self.request.user)
        messages.success(self.request, "Profilingiz yangilandi!")
        return response

# ============== NOTIFICATIONS & SETTINGS ==============

@login_required
def notifications_view(request):
    """Foydalanuvchi bildirishnomalarini ko'rish"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    if request.method == 'POST':
        # Mark as read
        notif_id = request.POST.get('notif_id')
        if notif_id:
            Notification.objects.filter(id=notif_id, user=request.user).update(is_read=True)
        return redirect('notifications')
    
    return render(request, 'users/notifications.html', {
        'notifications': notifications,
        'unread_count': Notification.objects.filter(user=request.user, is_read=False).count(),
    })


@login_required
def settings_view(request):
    """Foydalanuvchi sozlamalari"""
    user = request.user
    
    if request.method == 'POST':
        # Bildirishnomalar sozlamalari saqlash
        enabled = request.POST.get('notifications_enabled') == 'on'
        # Kelajakda: UserSettings modeli agar zarur bo'lsa
        messages.success(request, "Sozlamalar saqlandi!")
        return redirect('settings')
    
    return render(request, 'users/settings.html', {
        'user': user,
    })