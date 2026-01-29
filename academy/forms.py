from django import forms
from .models import Course, Group
from users.models import User


class CourseForm(forms.ModelForm):
    """Kurs yaratish/tahrirlash formasi"""
    
    class Meta:
        model = Course
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Kurs nomi, masalan: Python Backend'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Kurs haqida qisqacha ma\'lumot...'
            }),
        }
        labels = {
            'name': 'Kurs nomi',
            'description': 'Tavsif',
        }


class GroupForm(forms.ModelForm):
    """Guruh yaratish/tahrirlash formasi"""
    
    teacher = forms.ModelChoiceField(
        queryset=User.objects.filter(role='TEACHER', is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="O'qituvchi",
        required=True
    )
    
    class Meta:
        model = Group
        fields = ['name', 'course']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Guruh nomi, masalan: Python-42'
            }),
            'course': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Guruh nomi',
            'course': 'Kurs',
        }
    
    def save(self, commit=True):
        group = super().save(commit=commit)
        teacher = self.cleaned_data.get('teacher')
        if teacher and commit:
            group.teachers.add(teacher)
        return group


class AddStudentsToGroupForm(forms.Form):
    """Guruhga o'quvchilar qo'shish formasi"""
    
    students = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(role='STUDENT', is_active=True),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'student-checkbox'}),
        label="O'quvchilarni tanlang"
    )
    
    def __init__(self, *args, group=None, **kwargs):
        super().__init__(*args, **kwargs)
        if group:
            # Allaqachon guruhda bo'lmagan o'quvchilarni ko'rsatish
            existing_students = group.students.all()
            self.fields['students'].queryset = User.objects.filter(
                role='STUDENT', 
                is_active=True
            ).exclude(id__in=existing_students)


class RemoveFromGroupForm(forms.Form):
    """Guruhdan o'quvchi/o'qituvchi olib tashlash"""
    
    user_id = forms.IntegerField(widget=forms.HiddenInput())
    user_type = forms.CharField(widget=forms.HiddenInput())  # 'student' or 'teacher'
