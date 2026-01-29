from django import forms
from .models import Homework, Submission
from academy.models import Group

class HomeworkForm(forms.ModelForm):
    """Uyga vazifa yaratish formasi"""
    
    deadline = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        }),
        label="Topshirish muddati"
    )
    
    class Meta:
        model = Homework
        fields = ['group', 'title', 'description', 'deadline', 'sequence']
        widgets = {
            'group': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vazifa sarlavhasi'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Vazifa tavsifi...'}),
            'sequence': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
        labels = {
            'group': 'Guruh',
            'title': 'Sarlavha',
            'description': 'Tavsif',
            'sequence': 'Tartib raqami',
        }
    
    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        if teacher:
            # Faqat o'qituvchining o'z guruhlarini ko'rsatish
            self.fields['group'].queryset = Group.objects.filter(teachers=teacher)


class SubmissionForm(forms.ModelForm):
    """O'quvchi topshirish formasi"""
    
    SUBMISSION_TYPE_CHOICES = [
        ('text', 'Oddiy matn'),
        ('code', 'Kod'),
    ]
    
    submission_type = forms.ChoiceField(
        choices=SUBMISSION_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'submission-type-radio'}),
        initial='text',
        label="Topshirish turi"
    )
    
    CODE_LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('java', 'Java'),
        ('cpp', 'C++'),
        ('csharp', 'C#'),
        ('html', 'HTML'),
        ('css', 'CSS'),
        ('sql', 'SQL'),
        ('other', 'Boshqa'),
    ]
    
    code_language = forms.ChoiceField(
        choices=CODE_LANGUAGE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='python',
        required=False,
        label="Dasturlash tili"
    )
    
    class Meta:
        model = Submission
        fields = ['content', 'file']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control code-textarea',
                'rows': 12,
                'placeholder': 'Javobingizni yozing...',
                'spellcheck': 'false'
            }),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'content': 'Javob',
            'file': 'Fayl (ixtiyoriy)',
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        submission_type = self.cleaned_data.get('submission_type', 'text')
        instance.is_code = (submission_type == 'code')
        if instance.is_code:
            instance.code_language = self.cleaned_data.get('code_language', 'python')
        if commit:
            instance.save()
        return instance


class GradeSubmissionForm(forms.ModelForm):
    """O'qituvchi baholash formasi"""
    
    score_percent = forms.IntegerField(
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0-100',
            'min': 0,
            'max': 100
        }),
        label="Ball (%)"
    )
    
    class Meta:
        model = Submission
        fields = ['score_percent', 'teacher_comment']
        widgets = {
            'teacher_comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': "Izoh qo'shing (ixtiyoriy)..."
            }),
        }
        labels = {
            'teacher_comment': "O'qituvchi izohi",
        }
