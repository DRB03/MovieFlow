
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout

def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    else:
        return render(request,'users/profile.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a success page.
            return HttpResponseRedirect(reverse('index'))
        else:
            # Return an 'invalid login' error message.
            return render(request, 'users/login.html', {'errors':['Invalid Login']})
    else:
        return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))
