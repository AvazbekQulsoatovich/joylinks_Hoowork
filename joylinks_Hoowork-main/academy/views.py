from django.db import transaction, models
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseForbidden
from django.db.models import Avg, Count, Q

from .models import Course, Group, Certificate, MarketProduct, MarketPurchase
from .forms import (
    CourseForm,
    GroupForm,
    AddStudentsToGroupForm,
    AssignUserToGroupsForm,
    CertificateForm,
    MarketProductForm,
)
from homeworks.models import Homework, Submission, Notification
from users.models import User
from users.views import redirect_by_role


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
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN', 'MODERATOR']:
            return Course.objects.all()
        # Teachers and Students only see courses they belong to via groups
        group_courses = Group.objects.filter(
            Q(teachers=user) | Q(students=user)
        ).values_list('course_id', flat=True)
        return Course.objects.filter(id__in=group_courses)
    
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
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN', 'MODERATOR']:
            return Course.objects.all()
        # Teachers and Students only see courses they belong to
        group_courses = Group.objects.filter(
            Q(teachers=user) | Q(students=user)
        ).values_list('course_id', flat=True)
        return Course.objects.filter(id__in=group_courses)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        user = self.request.user
        
        if user.role in ['ADMIN', 'MODERATOR']:
            groups = course.groups.all()
        else:
            groups = course.groups.filter(Q(teachers=user) | Q(students=user))
            
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
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN', 'MODERATOR']:
            return Group.objects.all()
        return Group.objects.filter(Q(teachers=user) | Q(students=user))

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
    if request.user.role not in ['ADMIN', 'MODERATOR']:
        return HttpResponseForbidden("Faqat Admin yoki Moderator qo'shishi mumkin.")
    
    group = get_object_or_404(Group, pk=group_id)
    
    if request.method == 'POST':
        # Search query is not needed for POST unless we want to keep the list filtered if validation fails,
        # but here we just process IDs. However, if the user submits, the form validation checks if IDs are in queryset.
        # So we MUST pass the search_query to POST as well if the form uses it to set queryset.
        # But usually ModelMultipleChoiceField validates against the full queryset or the one set in __init__.
        # If we limit the queryset in __init__, and user submits an ID that is NOT in the limited queryset (e.g. they cleared search before submit?), 
        # it might be an issue. But here, if they submit, they submit what they see.
        # Let's pass search_query from GET (if present in URL action) or input... 
        # Actually, standard pattern is to keep form consistent.
        search_query = request.GET.get('search')
        form = AddStudentsToGroupForm(request.POST, group=group, search_query=search_query)
        if form.is_valid():
            students = form.cleaned_data['students']
            for student in students:
                group.students.add(student)
            messages.success(request, f"{len(students)} ta o'quvchi qo'shildi!")
            return redirect('group_detail', pk=group_id)
    else:
        search_query = request.GET.get('search')
        form = AddStudentsToGroupForm(group=group, search_query=search_query)
    
    return render(request, 'academy/add_students.html', {
        'form': form,
        'group': group,
        'available_students': form.fields['students'].queryset,
        'current_search': search_query
    })


@login_required
def remove_student_from_group(request, group_id, student_id):
    """Guruhdan o'quvchini olib tashlash"""
    if request.user.role not in ['ADMIN', 'MODERATOR']:
        return HttpResponseForbidden("Faqat Admin yoki Moderator olib tashlashi mumkin.")
    
    group = get_object_or_404(Group, pk=group_id)
    student = get_object_or_404(User, pk=student_id)
    
    if request.method == 'POST':
        group.students.remove(student)
        messages.success(request, f"{student.username} guruhdan olib tashlandi!")
    
    return redirect('group_detail', pk=group_id)


@login_required
def change_group_teacher(request, group_id):
    """Guruh o'qituvchisini almashtirish"""
    if request.user.role not in ['ADMIN', 'MODERATOR']:
        return HttpResponseForbidden("Faqat Admin yoki Moderator.")
    
    group = get_object_or_404(Group, pk=group_id)
    
    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id')
        if teacher_id:
            teacher = get_object_or_404(User, pk=teacher_id, role='TEACHER')
            group.teachers.clear()
            group.teachers.add(teacher)
            messages.success(request, f"O'qituvchi {teacher.username} ga o'zgartirildi!")
    
    return redirect('group_detail', pk=group_id)
@login_required
def assign_user_to_groups(request, user_id):
    """Foydalanuvchini guruhlarga biriktirish"""
    if request.user.role not in ['ADMIN', 'MODERATOR']:
        return HttpResponseForbidden("Faqat Admin yoki Moderator guruhlarga biriktira oladi.")
    
    target_user = get_object_or_404(User, pk=user_id)
    
    if request.method == 'POST':
        form = AssignUserToGroupsForm(request.POST, user=target_user)
        if form.is_valid():
            new_groups = form.cleaned_data['groups']
            if target_user.role == 'TEACHER':
                target_user.teaching_groups.set(new_groups)
            elif target_user.role == 'STUDENT':
                target_user.study_groups.set(new_groups)
            
            messages.success(request, f"{target_user.username} guruhlari yangilandi!")
            return redirect('user_detail', pk=user_id)
    else:
        form = AssignUserToGroupsForm(user=target_user)
    
    return render(request, 'academy/assign_groups.html', {
        'form': form,
        'target_user': target_user,
    })


# ============== CERTIFICATE VIEWS ==============

@login_required
def certificate_list(request):
    """Admin uchun o'quvchilar ro'yxati (sertifikat berish uchun)"""
    if request.user.role not in ['ADMIN', 'MODERATOR']:
        return HttpResponseForbidden("Faqat Admin yoki Moderator sertifikat berishi mumkin.")
    
    students = User.objects.filter(role='STUDENT', is_active=True).prefetch_related('certificates')
    
    return render(request, 'academy/certificate_list.html', {
        'students': students,
    })


@login_required
def certificate_upload(request, student_id):
    """Admin uchun sertifikat yuklash"""
    if request.user.role not in ['ADMIN', 'MODERATOR']:
        return HttpResponseForbidden("Faqat Admin yoki Moderator sertifikat yuklashi mumkin.")
    
    student = get_object_or_404(User, pk=student_id, role='STUDENT')
    
    if request.method == 'POST':
        form = CertificateForm(request.POST, request.FILES)
        if form.is_valid():
            certificate = form.save(commit=False)
            certificate.student = student
            certificate.save()
            messages.success(request, f"{student.username} uchun sertifikat yuklandi!")
            return redirect('certificate_list')
    else:
        form = CertificateForm()
    
    return render(request, 'academy/certificate_form.html', {
        'form': form,
        'student': student,
    })


@login_required
def student_certificates(request):
    """O'quvchi uchun o'z sertifikatlari"""
    if request.user.role != "STUDENT":
        return redirect_by_role(request.user)

    certificates = Certificate.objects.filter(student=request.user).order_by("-issued_at")

    coin_rewards = (
        Submission.objects.filter(student=request.user, coin_amount_awarded__gt=0)
        .select_related("homework", "graded_by")
        .order_by("-graded_at")
    )
    purchases = (
        MarketPurchase.objects.filter(student=request.user)
        .select_related("product")
        .order_by("-created_at")
    )

    return render(
        request,
        "student/certificates.html",
        {
            "certificates": certificates,
            "coin_rewards": coin_rewards,
            "coin_purchases": purchases,
        },
    )


@login_required
def student_coins(request):
    """Foydalanuvchi uchun 'Mening tangalarim' sahifasi"""
    user = request.user
    
    # Roziliklar (Tushumlar) - Barcha rollar uchun notification'lar orqali
    # Student uchun bu asosan avtomatik berilgan tangalar (Submission orqali alohida chiqadi quyida)
    # Teacher/Admin uchun bu Admin yuborgan tangalar
    transfers = Notification.objects.filter(
        user=user, 
        title="Tanga qabul qilindi"
    ).order_by("-created_at")

    # Chiqimlar/Mukofotlar (Student uchun tushum, Teacher uchun chiqim)
    if user.role == "STUDENT":
        coin_rewards = (
            Submission.objects.filter(student=user, coin_amount_awarded__gt=0)
            .select_related("homework", "graded_by")
            .order_by("-graded_at")
        )
        expenditures = (
            MarketPurchase.objects.filter(student=user)
            .select_related("product")
            .order_by("-created_at")
        )
    else:
        # Teacher/Admin uchun chiqim - o'quvchilarga berilgan tangalar
        coin_rewards = (
            Submission.objects.filter(graded_by=user, coin_amount_awarded__gt=0)
            .select_related("homework", "student")
            .order_by("-graded_at")
        )
        expenditures = MarketPurchase.objects.none()

    return render(
        request,
        "student/coins.html",
        {
            "coin_rewards": coin_rewards,
            "coin_purchases": expenditures,
            "transfers": transfers,
        },
    )


# ============== MARKET (STUDENT) ==============

@login_required
def student_market(request):
    """Market sahifasi.

    - Student: mahsulot ko'radi va sotib oladi
    - Teacher/Admin: faqat ko'rish (sotib olishga ruxsat yo'q)
    """
    if request.user.role not in ["STUDENT", "TEACHER", "ADMIN"]:
        return redirect_by_role(request.user)

    products = MarketProduct.objects.filter(is_active=True).order_by("-created_at")
    purchases = MarketPurchase.objects.none()
    if request.user.role == "STUDENT":
        purchases = (
            MarketPurchase.objects.filter(student=request.user)
            .select_related("product")
            .order_by("-created_at")
        )

    return render(
        request,
        "student/market.html",
        {
            "products": products,
            "purchases": purchases,
            "can_buy": request.user.role == "STUDENT",
        },
    )


@login_required
def buy_product(request, product_id):
    """O'quvchi marketdan mahsulot sotib oladi"""
    if request.user.role != "STUDENT":
        return HttpResponseForbidden("Faqat o'quvchilar xarid qilishi mumkin.")

    product = get_object_or_404(MarketProduct, pk=product_id, is_active=True)

    if request.method != "POST":
        return redirect("student_market")

    with transaction.atomic():
        student = User.objects.select_for_update().get(pk=request.user.pk)
        admin_user = (
            User.objects.select_for_update()
            .filter(role=User.Role.ADMIN)
            .order_by("id")
            .first()
        )

        if not admin_user:
            messages.error(request, "Admin topilmadi. Iltimos, tizim sozlamalarini tekshiring.")
            return redirect("student_market")

        price = product.price_coins
        current_balance = max(student.coin_balance or 0, 0)

        if current_balance < price:
            messages.error(request, "Balansingizda yetarli tanga yo'q.")
            return redirect("student_market")

        # Balanslarni yangilash
        student.coin_balance = current_balance - price
        admin_user.coin_balance = max(admin_user.coin_balance or 0, 0) + price
        student.save(update_fields=["coin_balance"])
        admin_user.save(update_fields=["coin_balance"])

        purchase = MarketPurchase.objects.create(
            product=product,
            student=student,
            coins_spent=price,
        )

        # notify all admins about this purchase
        admins = User.objects.filter(role=User.Role.ADMIN)
        for admin in admins:
            Notification.objects.create(
                user=admin,
                notification_type=Notification.NotificationType.SYSTEM,
                title="Yangi market xaridi",
                message=f"{student.get_full_name() or student.username} '{product.name}' mahsulotini sotib oldi.",
            )

        # remind student that admin will hand over the gift
        Notification.objects.create(
            user=student,
            notification_type=Notification.NotificationType.SYSTEM,
            title="Xaridingiz qabul qilindi",
            message=(
                f"Siz '{product.name}' mahsulotini {price} tanga evaziga sotib oldingiz. "
                "Ma'lumot uchun: admin sizga sovg'ani berishga tayyor, iltimos uni topib oling."
            ),
        )

    messages.success(
        request,
        (
            f"Tabriklaymiz! Siz '{product.name}' mahsulotini {price} tanga evaziga sotib oldingiz. "
            "Iltimos, adminga murojaat qiling – sovg'ani topshirib beradi."
        ),
    )
    return redirect("student_market")


# ============== MARKET (ADMIN) ==============


class MarketProductListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """Admin uchun market mahsulotlari ro'yxati"""

    model = MarketProduct
    template_name = "market/product_list.html"
    context_object_name = "products"

    def get_queryset(self):
        return MarketProduct.objects.all().order_by("-created_at")


class MarketProductCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Yangi market mahsuloti yaratish"""

    model = MarketProduct
    form_class = MarketProductForm
    template_name = "market/product_form.html"
    success_url = reverse_lazy("market_product_list")

    def form_valid(self, form):
        messages.success(self.request, "Mahsulot muvaffaqiyatli qo'shildi!")
        return super().form_valid(form)


class MarketProductUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Market mahsulotini tahrirlash"""

    model = MarketProduct
    form_class = MarketProductForm
    template_name = "market/product_form.html"
    success_url = reverse_lazy("market_product_list")

    def form_valid(self, form):
        messages.success(self.request, "Mahsulot yangilandi!")
        return super().form_valid(form)


class MarketProductDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Market mahsulotini o'chirish"""

    model = MarketProduct
    template_name = "market/product_confirm_delete.html"
    success_url = reverse_lazy("market_product_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Mahsulot o'chirildi!")
        return super().delete(request, *args, **kwargs)


class MarketPurchaseListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """Admin uchun barcha xaridlar ro'yxati"""

    model = MarketPurchase
    template_name = "market/purchase_list.html"
    context_object_name = "purchases"

    def get_queryset(self):
        return (
            MarketPurchase.objects.select_related("product", "student")
            .order_by("-created_at")
        )


@login_required
def confirm_purchase(request, pk):
    """Admin marks a purchase as delivered and notifies the student."""
    if request.user.role != "ADMIN":
        return HttpResponseForbidden()

    purchase = get_object_or_404(MarketPurchase, pk=pk)
    if purchase.admin_confirmed:
        messages.info(request, "Ushbu xarid allaqachon tasdiqlangan.")
    else:
        purchase.admin_confirmed = True
        purchase.save(update_fields=["admin_confirmed"])
        Notification.objects.create(
            user=purchase.student,
            notification_type=Notification.NotificationType.SYSTEM,
            title="Sovg'a berildi",
            message=(
                f"'{purchase.product.name}' mahsulotingiz berildi. "
                "Iltimos, admin bilan bog'lanib sovg'ani oling."
            ),
        )
        messages.success(request, "Xarid tasdiqlandi va o'quvchiga xabar yuborildi.")
    return redirect("market_purchase_list")
