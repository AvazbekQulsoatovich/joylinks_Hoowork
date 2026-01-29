from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseForbidden
from django.db.models import Avg, Count
from .models import Course, Group
from .forms import CourseForm, GroupForm, AddStudentsToGroupForm
from homeworks.models import Homework, Submission
from users.models import User


class AdminRequiredMixin(UserPassesTestMixin):
    """Faqat Admin uchun"""
    def test_func(self):
        return self.request.user.role == 'ADMIN'


class AdminModeratorMixin(UserPassesTestMixin):
    """Admin va Moderator uchun"""
    def test_func(self):
        return self.request.user.role in ['ADMIN', 'MODERATOR']


# ============== COURSE VIEWS ==============

class CourseListView(LoginRequiredMixin, ListView):
    """Kurslar ro'yxati"""
    model = Course
    template_name = 'academy/course_list.html'
    context_object_name = 'courses'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for course in context['courses']:
            course.group_count = course.groups.count()
            course.student_count = sum(g.students.count() for g in course.groups.all())
        return context


class CourseDetailView(LoginRequiredMixin, DetailView):
    """Kurs tafsilotlari"""
    model = Course
    template_name = 'academy/course_detail.html'
    context_object_name = 'course'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        
        groups = course.groups.all()
        context['groups'] = groups
        
        # Statistika
        total_students = sum(g.students.count() for g in groups)
        total_homeworks = Homework.objects.filter(group__in=groups).count()
        
        subs = Submission.objects.filter(
            homework__group__in=groups,
            is_graded=True
        )
        avg_score = subs.aggregate(avg=Avg('score_percent'))['avg'] or 0
        
        context['total_students'] = total_students
        context['total_homeworks'] = total_homeworks
        context['avg_score'] = round(avg_score, 1)
        
        return context


class CourseCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Yangi kurs yaratish"""
    model = Course
    form_class = CourseForm
    template_name = 'academy/course_form.html'
    success_url = reverse_lazy('course_list')
    
    def form_valid(self, form):
        messages.success(self.request, "Kurs muvaffaqiyatli yaratildi!")
        return super().form_valid(form)


class CourseUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Kursni tahrirlash"""
    model = Course
    form_class = CourseForm
    template_name = 'academy/course_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, "Kurs yangilandi!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('course_detail', kwargs={'pk': self.object.pk})


class CourseDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Kursni o'chirish"""
    model = Course
    template_name = 'academy/course_confirm_delete.html'
    success_url = reverse_lazy('course_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Kurs o'chirildi!")
        return super().delete(request, *args, **kwargs)


# ============== GROUP VIEWS ==============

class GroupListView(LoginRequiredMixin, ListView):
    """Guruhlar ro'yxati"""
    model = Group
    template_name = 'academy/group_list.html'
    context_object_name = 'groups'

    def get_queryset(self):
        user = self.request.user
        queryset = Group.objects.select_related('course').prefetch_related('teachers', 'students')
        
        if user.role in ['ADMIN', 'MODERATOR']:
            return queryset.all()
        elif user.role == 'TEACHER':
            return queryset.filter(teachers=user)
        elif user.role == 'STUDENT':
            return queryset.filter(students=user)
        return Group.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for group in context['groups']:
            group.student_count = group.students.count()
            group.teacher_list = ', '.join([t.get_full_name() or t.username for t in group.teachers.all()])
        return context


class GroupDetailView(LoginRequiredMixin, DetailView):
    """Guruh tafsilotlari"""
    model = Group
    template_name = 'academy/group_detail.html'
    context_object_name = 'group'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = self.object
        user = self.request.user
        
        context['students'] = group.students.all().order_by('last_name', 'first_name')
        context['teachers'] = group.teachers.all()
        context['homeworks'] = Homework.objects.filter(group=group).order_by('sequence')
        
        # All teachers for the change teacher modal
        if user.role == 'ADMIN':
            context['all_teachers'] = User.objects.filter(role='TEACHER', is_active=True)

        
        # O'quvchilar statistikasi (teacher/admin uchun)
        if user.role in ['ADMIN', 'MODERATOR', 'TEACHER']:
            student_stats = []
            for student in context['students']:
                subs = Submission.objects.filter(
                    homework__group=group,
                    student=student,
                    is_graded=True
                )
                avg = subs.aggregate(avg=Avg('score_percent'))['avg'] or 0
                student_stats.append({
                    'student': student,
                    'avg_score': round(avg, 1),
                    'submitted': subs.count(),
                    'total': context['homeworks'].count()
                })
            context['student_stats'] = student_stats
            
            # Guruh o'rtachasi
            if student_stats:
                context['group_avg'] = round(
                    sum(s['avg_score'] for s in student_stats) / len(student_stats), 1
                )
            else:
                context['group_avg'] = 0
        
        return context


class GroupCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Yangi guruh yaratish"""
    model = Group
    form_class = GroupForm
    template_name = 'academy/group_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, "Guruh muvaffaqiyatli yaratildi!")
        response = super().form_valid(form)
        return response
    
    def get_success_url(self):
        return reverse('group_detail', kwargs={'pk': self.object.pk})


class GroupUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Guruhni tahrirlash"""
    model = Group
    form_class = GroupForm
    template_name = 'academy/group_form.html'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Mavjud o'qituvchini ko'rsatish
        teachers = self.object.teachers.first()
        if teachers:
            form.fields['teacher'].initial = teachers
        return form
    
    def form_valid(self, form):
        group = form.save()
        # Eski o'qituvchilarni olib tashlash va yangisini qo'shish
        group.teachers.clear()
        teacher = form.cleaned_data.get('teacher')
        if teacher:
            group.teachers.add(teacher)
        messages.success(self.request, "Guruh yangilandi!")
        return redirect('group_detail', pk=group.pk)


class GroupDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Guruhni o'chirish"""
    model = Group
    template_name = 'academy/group_confirm_delete.html'
    success_url = reverse_lazy('group_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Guruh o'chirildi!")
        return super().delete(request, *args, **kwargs)


@login_required
def add_students_to_group(request, group_id):
    """Guruhga o'quvchilar qo'shish"""
    if request.user.role != 'ADMIN':
        return HttpResponseForbidden("Faqat Admin qo'shishi mumkin.")
    
    group = get_object_or_404(Group, pk=group_id)
    
    if request.method == 'POST':
        form = AddStudentsToGroupForm(request.POST, group=group)
        if form.is_valid():
            students = form.cleaned_data['students']
            for student in students:
                group.students.add(student)
            messages.success(request, f"{len(students)} ta o'quvchi qo'shildi!")
            return redirect('group_detail', pk=group_id)
    else:
        form = AddStudentsToGroupForm(group=group)
    
    return render(request, 'academy/add_students.html', {
        'form': form,
        'group': group
    })


@login_required
def remove_student_from_group(request, group_id, student_id):
    """Guruhdan o'quvchini olib tashlash"""
    if request.user.role != 'ADMIN':
        return HttpResponseForbidden("Faqat Admin olib tashlashi mumkin.")
    
    group = get_object_or_404(Group, pk=group_id)
    student = get_object_or_404(User, pk=student_id)
    
    if request.method == 'POST':
        group.students.remove(student)
        messages.success(request, f"{student.username} guruhdan olib tashlandi!")
    
    return redirect('group_detail', pk=group_id)


@login_required
def change_group_teacher(request, group_id):
    """Guruh o'qituvchisini almashtirish"""
    if request.user.role != 'ADMIN':
        return HttpResponseForbidden("Faqat Admin.")
    
    group = get_object_or_404(Group, pk=group_id)
    
    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id')
        if teacher_id:
            teacher = get_object_or_404(User, pk=teacher_id, role='TEACHER')
            group.teachers.clear()
            group.teachers.add(teacher)
            messages.success(request, f"O'qituvchi {teacher.username} ga o'zgartirildi!")
    
    return redirect('group_detail', pk=group_id)
