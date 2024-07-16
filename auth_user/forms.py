from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'name', 'password1', 'password2', 'is_landlord')
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email'}),
            'name': forms.TextInput(attrs={'placeholder': 'Enter your name'}),
        }


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'name', 'is_landlord')
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email'}),
            'name': forms.TextInput(attrs={'placeholder': 'Enter your name'}),
        }


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email', max_length=255,
                                widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'}))

    class Meta:
        model = CustomUser
        fields = ('username', 'password')



