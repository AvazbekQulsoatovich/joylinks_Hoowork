"""
Admin uchun Excel Export Views
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from .export import (
    export_all_submissions, export_group_report, 
    export_course_report, workbook_to_response
)
from academy.models import Course, Group


@login_required
def export_all_view(request):
    """Barcha natijalarni export qilish"""
    if request.user.role != 'ADMIN':
        return HttpResponseForbidden("Faqat Admin yuklab olishi mumkin.")
    
    course_id = request.GET.get('course')
    group_id = request.GET.get('group')
    
    wb = export_all_submissions(
        course_id=course_id if course_id else None,
        group_id=group_id if group_id else None
    )
    
    filename = "hoowork_natijalar.xlsx"
    if group_id:
        group = Group.objects.get(pk=group_id)
        filename = f"hoowork_{group.name}_natijalar.xlsx"
    elif course_id:
        course = Course.objects.get(pk=course_id)
        filename = f"hoowork_{course.name}_natijalar.xlsx"
    
    return workbook_to_response(wb, filename)


@login_required
def export_group_view(request, group_id):
    """Guruh hisobotini export qilish"""
    if request.user.role not in ['ADMIN', 'TEACHER']:
        return HttpResponseForbidden("Ruxsat yo'q.")
    
    group = get_object_or_404(Group, pk=group_id)
    
    # Teacher faqat o'z guruhlarini
    if request.user.role == 'TEACHER':
        if not group.teachers.filter(id=request.user.id).exists():
            return HttpResponseForbidden("Bu sizning guruhingiz emas.")
    
    wb = export_group_report(group_id)
    filename = f"hoowork_{group.name}_hisobot.xlsx"
    
    return workbook_to_response(wb, filename)


@login_required
def export_course_view(request, course_id):
    """Kurs hisobotini export qilish"""
    if request.user.role != 'ADMIN':
        return HttpResponseForbidden("Faqat Admin yuklab olishi mumkin.")
    
    course = get_object_or_404(Course, pk=course_id)
    wb = export_course_report(course_id)
    filename = f"hoowork_{course.name}_hisobot.xlsx"
    
    return workbook_to_response(wb, filename)
