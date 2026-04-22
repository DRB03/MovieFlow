from django.urls import path
from .views import *

urlpatterns = [
    #path('', index, name='index'),
    path('login', login_view, name='login'),
    path('register', register_view, name='register'),
    path('logout', logout_view, name='logout'),
    path('profile', profile_view, name='users_profile'),
    path('reviews/<int:review_id>/delete', delete_review, name='delete_review'),
]