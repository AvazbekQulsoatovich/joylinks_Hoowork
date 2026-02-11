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


from django.db.models import Q

class AddStudentsToGroupForm(forms.Form):
    """Guruhga o'quvchilar qo'shish formasi"""
    
    students = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(role='STUDENT', is_active=True),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'student-checkbox'}),
        label="O'quvchilarni tanlang"
    )
    
    def __init__(self, *args, group=None, search_query=None, **kwargs):
        super().__init__(*args, **kwargs)
        if group:
            # Allaqachon guruhda bo'lmagan o'quvchilarni ko'rsatish
            existing_students = group.students.all()
            qs = User.objects.filter(
                role='STUDENT', 
                is_active=True
            ).exclude(id__in=existing_students)
            
            if search_query:
                qs = qs.filter(
                    Q(username__icontains=search_query) |
                    Q(first_name__icontains=search_query) |
                    Q(last_name__icontains=search_query)
                )
            
            self.fields['students'].queryset = qs


class AssignUserToGroupsForm(forms.Form):
    """Foydalanuvchini guruhlarga biriktirish formasi"""
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'group-checkbox'}),
        label="Guruhlarni tanlang"
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            # Foydalanuvchi turiga qarab guruhlarni filtrlash
            if user.role == 'TEACHER':
                self.fields['groups'].queryset = Group.objects.all()
                self.fields['groups'].initial = user.teaching_groups.all()
            elif user.role == 'STUDENT':
                self.fields['groups'].queryset = Group.objects.all()
                self.fields['groups'].initial = user.study_groups.all()
