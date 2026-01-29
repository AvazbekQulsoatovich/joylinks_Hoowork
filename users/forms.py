from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class UserForm(forms.ModelForm):
    """Foydalanuvchi yaratish/tahrirlash formasi"""
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Parol'
        }),
        label='Parol',
        required=True
    )
    
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Parolni tasdiqlang'
        }),
        label='Parolni tasdiqlang',
        required=True
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'phone']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Foydalanuvchi nomi'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ism'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Familiya'
            }),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+998901234567'
            }),
        }
        labels = {
            'username': 'Foydalanuvchi nomi',
            'email': 'Email',
            'first_name': 'Ism',
            'last_name': 'Familiya',
            'role': 'Rol',
            'phone': 'Telefon',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Parollar mos kelmadi!")
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    """Foydalanuvchini tahrirlash formasi (parolsiz)"""
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'phone', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'username': 'Foydalanuvchi nomi',
            'email': 'Email',
            'first_name': 'Ism',
            'last_name': 'Familiya',
            'role': 'Rol',
            'phone': 'Telefon',
            'is_active': 'Faol',
        }


class ChangePasswordForm(forms.Form):
    """Parolni o'zgartirish formasi"""
    
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Yangi parol'
        }),
        label='Yangi parol',
        min_length=6
    )
    
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Parolni tasdiqlang'
        }),
        label='Parolni tasdiqlang'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Parollar mos kelmadi!")
        
        return cleaned_data
