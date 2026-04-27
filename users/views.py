from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from movies.models import Movie, MovieReview
from .forms import ProfileAvatarForm
from .models import Profile, UserFollow

@login_required(login_url='/users/login')
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        avatar_form = ProfileAvatarForm(request.POST, request.FILES, instance=profile)
        if avatar_form.is_valid():
            avatar_form.save()
            return HttpResponseRedirect(reverse('profile'))
    else:
        avatar_form = ProfileAvatarForm(instance=profile)

    reviews = (
        MovieReview.objects.filter(user=request.user, parent__isnull=True)
        .select_related("movie")
        .order_by("-created_at", "-id")
    )
    liked_movies = Movie.objects.filter(
        likes__user=request.user
    ).prefetch_related('genres').order_by('-likes__created_at')
    followers_count = UserFollow.objects.filter(following=request.user).count()
    following_count = UserFollow.objects.filter(follower=request.user).count()
    context = {
        'profile_user': request.user,
        'profile': profile,
        'avatar_form': avatar_form,
        'reviews': reviews,
        'liked_movies': liked_movies,
        'followers_count': followers_count,
        'following_count': following_count,
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


def public_profile(request, username):
    profile_user = get_object_or_404(User, username__iexact=username)
    profile, _ = Profile.objects.get_or_create(user=profile_user)
    review_qs = MovieReview.objects.filter(user=profile_user, parent__isnull=True)
    review_count = review_qs.count()
    reviews = review_qs.select_related("movie").order_by("-created_at", "-id")[:50]
    followers_count = UserFollow.objects.filter(following=profile_user).count()
    following_count = UserFollow.objects.filter(follower=profile_user).count()
    is_own = request.user.is_authenticated and request.user.pk == profile_user.pk
    is_following = False
    if request.user.is_authenticated and not is_own:
        is_following = UserFollow.objects.filter(follower=request.user, following=profile_user).exists()
    context = {
        "profile_user": profile_user,
        "profile": profile,
        "reviews": reviews,
        "review_count": review_count,
        "followers_count": followers_count,
        "following_count": following_count,
        "is_own_profile": is_own,
        "is_following": is_following,
    }
    return render(request, "users/profile_public.html", context)


@login_required(login_url='/users/login')
@require_POST
def toggle_follow(request, username):
    target = get_object_or_404(User, username__iexact=username)
    if target.pk == request.user.pk:
        return HttpResponseRedirect(reverse("user_public_profile", kwargs={"username": target.username}))
    rel = UserFollow.objects.filter(follower=request.user, following=target).first()
    if rel:
        rel.delete()
    else:
        UserFollow.objects.create(follower=request.user, following=target)
    return HttpResponseRedirect(reverse("user_public_profile", kwargs={"username": target.username}))


@login_required(login_url='/users/login')
@require_POST
def delete_review(request, review_id):
    review = get_object_or_404(MovieReview, id=review_id, user=request.user, parent__isnull=True)
    review.delete()
    return HttpResponseRedirect(reverse('profile'))
