
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from movies.models import MovieReview

@login_required(login_url='/users/login')
def profile_view(request):
    reviews = MovieReview.objects.filter(user=request.user).select_related('movie').order_by('-id')
    context = {
        'profile_user': request.user,
        'reviews': reviews,
    }
    return render(request, 'users/profile.html', context)


def index(request):
    return profile_view(request)

def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))

    next_url = request.GET.get('next') or request.POST.get('next') or reverse('index')
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(next_url)
        else:
            return render(request, 'users/login.html', {
                'errors': ['Invalid credentials. Please check your username and password.'],
                'next': next_url,
            })
    else:
        return render(request, 'users/login.html', {'next': next_url})


def register_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))

    next_url = request.GET.get('next') or request.POST.get('next') or reverse('index')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        errors = []

        if not username:
            errors.append('Username is required.')
        if not password:
            errors.append('Password is required.')
        if password != password_confirm:
            errors.append('Passwords do not match.')
        if User.objects.filter(username=username).exists():
            errors.append('That username is already taken.')

        if errors:
            return render(request, 'users/register.html', {
                'errors': errors,
                'username': username,
                'email': email,
                'next': next_url,
            })

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return HttpResponseRedirect(next_url)

    return render(request, 'users/register.html', {'next': next_url})

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))
