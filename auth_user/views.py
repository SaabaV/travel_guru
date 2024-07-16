from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.views.decorators.csrf import csrf_protect
from rest_framework import viewsets
from .models import CustomUser
from .serializers import UserSerializer
from .forms import CustomUserCreationForm, CustomAuthenticationForm


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


@csrf_protect
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(request.GET.get('next', 'home'))
    else:
        form = CustomUserCreationForm()
    return render(request, 'auth_user/register.html', {'form': form})


@csrf_protect
def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect(request.GET.get('next', 'home'))
    else:
        form = CustomAuthenticationForm()
    return render(request, 'auth_user/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')



