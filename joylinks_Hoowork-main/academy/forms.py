from django import forms # type: ignore
from django.db.models import Q # type: ignore
from .models import Course, Group, Certificate, MarketProduct # type: ignore
from users.models import User # type: ignore


class CertificateForm(forms.ModelForm):
    """Sertifikat yuklash formasi"""
    class Meta:
        model = Certificate
        fields = ['course', 'file']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'course': 'Kurs',
            'file': 'Sertifikat fayli (PDF, JPG, PNG)',
        }


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


class MarketProductForm(forms.ModelForm):
    """Admin uchun market mahsuloti formasi"""

    class Meta:
        model = MarketProduct
        fields = ["name", "description", "price_coins", "image", "is_active"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Mahsulot nomi, masalan: Redmi telefon",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Qisqacha tavsif...",
                }
            ),
            "price_coins": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                }
            ),
            "image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),
        }
        labels = {
            "name": "Mahsulot nomi",
            "description": "Tavsif",
            "price_coins": "Narx (tanga)",
            "image": "Rasm",
            "is_active": "Faol (marketda ko'rinsin)",
        }
