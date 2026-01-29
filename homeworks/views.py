from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.db.models import Avg, Count, Q
from .models import Homework, Submission, Notification
from .forms import HomeworkForm, SubmissionForm, GradeSubmissionForm
from .utils import is_homework_locked, auto_grade_missed_homeworks
from academy.models import Group


class HomeworkListView(LoginRequiredMixin, ListView):
    """Barcha vazifalar ro'yxati (role bo'yicha filtrlangan)"""
    model = Homework
    template_name = 'homeworks/homework_list.html'
    context_object_name = 'homeworks'

    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN', 'MODERATOR']:
            return Homework.objects.select_related('group', 'created_by').all()
        elif user.role == 'TEACHER':
            return Homework.objects.select_related('group', 'created_by').filter(group__teachers=user)
        elif user.role == 'STUDENT':
            return Homework.objects.select_related('group', 'created_by').filter(group__students=user)
        return Homework.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        now = timezone.now()
        
        if user.role == 'STUDENT':
            for hw in context['homeworks']:
                hw.is_locked = is_homework_locked(user, hw)
                hw.is_submitted = Submission.objects.filter(homework=hw, student=user).exists()
                hw.is_overdue = hw.deadline < now and not hw.is_submitted
                # Check for deadline warning (1 hour)
                if hw.deadline > now and (hw.deadline - now).total_seconds() <= 3600:
                    hw.deadline_warning = True
        elif user.role == 'TEACHER':
            for hw in context['homeworks']:
                submissions = Submission.objects.filter(homework=hw)
                hw.total_students = hw.group.students.count()
                hw.submitted_count = submissions.count()
                hw.graded_count = submissions.filter(is_graded=True).count()
                hw.pending_count = hw.submitted_count - hw.graded_count
        
        context['now'] = now
        return context


class HomeworkDetailView(LoginRequiredMixin, DetailView):
    """Vazifa tafsilotlari"""
    model = Homework
    template_name = 'homeworks/homework_detail.html'
    context_object_name = 'homework'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = request.user
        
        # Student uchun lock tekshirish
        if user.role == 'STUDENT' and is_homework_locked(user, self.object):
            return render(request, 'homeworks/locked.html', {'homework': self.object})
        
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        homework = self.object
        
        if user.role == 'STUDENT':
            context['submission'] = Submission.objects.filter(
                homework=homework, student=user
            ).first()
            context['can_submit'] = timezone.now() <= homework.deadline
        elif user.role in ['TEACHER', 'ADMIN']:
            submissions = Submission.objects.filter(homework=homework).select_related('student')
            context['submissions'] = submissions
            context['submitted_students'] = [s.student for s in submissions]
            context['all_students'] = homework.group.students.all()
            context['not_submitted'] = homework.group.students.exclude(
                id__in=[s.student.id for s in submissions]
            )
            # Statistika
            context['avg_score'] = submissions.filter(is_graded=True).aggregate(
                avg=Avg('score_percent')
            )['avg'] or 0
        
        return context


class HomeworkCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Yangi vazifa yaratish (O'qituvchi uchun)"""
    model = Homework
    form_class = HomeworkForm
    template_name = 'homeworks/homework_form.html'
    
    def test_func(self):
        return self.request.user.role in ['TEACHER', 'ADMIN']

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user.role == 'TEACHER':
            kwargs['teacher'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        homework = form.save()
        
        # Guruhdagi barcha o'quvchilarga notification yuborish
        students = homework.group.students.all()
        notifications = [
            Notification(
                user=student,
                notification_type='NEW_HW',
                title='Yangi uyga vazifa',
                message=f'"{homework.title}" vazifasi berildi. Deadline: {homework.deadline.strftime("%d.%m.%Y %H:%M")}',
                related_homework=homework
            )
            for student in students
        ]
        Notification.objects.bulk_create(notifications)
        
        messages.success(self.request, "Vazifa muvaffaqiyatli yaratildi!")
        return redirect('homework_detail', pk=homework.pk)


class HomeworkUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Vazifani tahrirlash"""
    model = Homework
    form_class = HomeworkForm
    template_name = 'homeworks/homework_form.html'

    def test_func(self):
        homework = self.get_object()
        user = self.request.user
        return user.role == 'ADMIN' or (user.role == 'TEACHER' and homework.created_by == user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user.role == 'TEACHER':
            kwargs['teacher'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Vazifa yangilandi!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('homework_detail', kwargs={'pk': self.object.pk})


class HomeworkDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Vazifani o'chirish"""
    model = Homework
    template_name = 'homeworks/homework_confirm_delete.html'
    success_url = reverse_lazy('homework_list')

    def test_func(self):
        homework = self.get_object()
        user = self.request.user
        return user.role == 'ADMIN' or (user.role == 'TEACHER' and homework.created_by == user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Vazifa o'chirildi!")
        return super().delete(request, *args, **kwargs)


class SubmissionCreateView(LoginRequiredMixin, CreateView):
    """Vazifani topshirish (O'quvchi uchun)"""
    model = Submission
    form_class = SubmissionForm
    template_name = 'homeworks/submission_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        homework_id = self.kwargs.get('homework_id')
        context['homework'] = get_object_or_404(Homework, pk=homework_id)
        return context

    def form_valid(self, form):
        homework_id = self.kwargs.get('homework_id')
        homework = get_object_or_404(Homework, pk=homework_id)
        user = self.request.user
        
        # Deadline tekshirish
        if timezone.now() > homework.deadline:
            messages.error(self.request, "Muddat o'tib ketgan! Topshirish mumkin emas.")
            return redirect('homework_detail', pk=homework_id)
        
        # Allaqachon topshirganmi tekshirish
        if Submission.objects.filter(homework=homework, student=user).exists():
            messages.warning(self.request, "Siz bu vazifani allaqachon topshirgansiz!")
            return redirect('homework_detail', pk=homework_id)
        
        # Student guruhga tegishlimi tekshirish
        if not homework.group.students.filter(id=user.id).exists():
            return HttpResponseForbidden("Siz bu guruhga tegishli emassiz.")
        
        form.instance.homework = homework
        form.instance.student = user
        submission = form.save()
        
        messages.success(self.request, "Vazifa muvaffaqiyatli topshirildi!")
        return redirect('homework_detail', pk=homework_id)


class SubmissionDetailView(LoginRequiredMixin, DetailView):
    """Topshiriq tafsilotlari"""
    model = Submission
    template_name = 'homeworks/submission_detail.html'
    context_object_name = 'submission'

    def get_queryset(self):
        user = self.request.user
        if user.role == 'STUDENT':
            return Submission.objects.filter(student=user)
        elif user.role in ['TEACHER', 'ADMIN', 'MODERATOR']:
            return Submission.objects.all()
        return Submission.objects.none()


class GradeSubmissionView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Topshiriqni baholash (O'qituvchi uchun)"""
    model = Submission
    form_class = GradeSubmissionForm
    template_name = 'homeworks/grade_submission.html'
    context_object_name = 'submission'

    def test_func(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return True
        if user.role == 'TEACHER':
            submission = self.get_object()
            return submission.homework.group.teachers.filter(id=user.id).exists()
        return False

    def form_valid(self, form):
        submission = form.save(commit=False)
        submission.is_graded = True
        submission.graded_at = timezone.now()
        submission.graded_by = self.request.user
        submission.save()
        
        # O'quvchiga notification yuborish
        Notification.objects.create(
            user=submission.student,
            notification_type='GRADED',
            title='Vazifangiz baholandi',
            message=f'"{submission.homework.title}" vazifangiz baholandi. Ball: {submission.score_percent}%',
            related_homework=submission.homework
        )
        
        messages.success(self.request, f"Baho qo'yildi: {submission.score_percent}%")
        return redirect('homework_detail', pk=submission.homework.pk)


class TeacherSubmissionsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """O'qituvchi uchun barcha topshiriqlar"""
    model = Submission
    template_name = 'homeworks/teacher_submissions.html'
    context_object_name = 'submissions'

    def test_func(self):
        return self.request.user.role in ['TEACHER', 'ADMIN']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return Submission.objects.select_related('homework', 'student', 'homework__group').all()
        return Submission.objects.select_related(
            'homework', 'student', 'homework__group'
        ).filter(homework__group__teachers=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pending'] = self.get_queryset().filter(is_graded=False)
        context['graded'] = self.get_queryset().filter(is_graded=True)
        return context


@login_required
def group_stats_view(request, group_id):
    """Guruh statistikasi"""
    group = get_object_or_404(Group, pk=group_id)
    user = request.user
    
    # Permission check
    if user.role == 'TEACHER' and not group.teachers.filter(id=user.id).exists():
        return HttpResponseForbidden("Sizning bu guruhga kirish huquqingiz yo'q.")
    elif user.role not in ['ADMIN', 'MODERATOR', 'TEACHER']:
        return HttpResponseForbidden("Sizning statistika ko'rish huquqingiz yo'q.")
    
    homeworks = Homework.objects.filter(group=group)
    students = group.students.all()
    
    stats = []
    for student in students:
        submissions = Submission.objects.filter(homework__group=group, student=student)
        total_homeworks = homeworks.count()
        submitted_count = submissions.count()
        graded = submissions.filter(is_graded=True)
        avg_score = graded.aggregate(avg=Avg('score_percent'))['avg'] or 0
        
        stats.append({
            'student': student,
            'submitted': submitted_count,
            'total': total_homeworks,
            'avg_score': round(avg_score, 1),
            'completion': round((submitted_count / total_homeworks * 100) if total_homeworks > 0 else 0, 1)
        })
    
    # Guruh o'rtachasi
    group_avg = sum(s['avg_score'] for s in stats) / len(stats) if stats else 0
    
    return render(request, 'homeworks/group_stats.html', {
        'group': group,
        'stats': stats,
        'group_avg': round(group_avg, 1),
        'homeworks': homeworks
    })


@login_required
def mark_notification_read(request, notification_id):
    """Bildirishnomani o'qilgan deb belgilash"""
    notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    if notification.related_homework:
        return redirect('homework_detail', pk=notification.related_homework.pk)
    return redirect('student_dashboard')


@login_required
def notifications_list(request):
    """Barcha bildirishnomalar"""
    notifications = Notification.objects.filter(user=request.user)
    return render(request, 'homeworks/notifications.html', {
        'notifications': notifications
    })
