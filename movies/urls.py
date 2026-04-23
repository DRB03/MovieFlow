from django.urls import path
from .views import *

urlpatterns = [
    path('all/', all_movies),
    # CAMBIO: Le pusimos name='movie_detail' para usarlo en la redirección
    path('<int:movie_id>/', movie, name='movie_detail'),
    path('movie_comment/add/<int:movie_id>/', add_comment),
    path('movie_review/add/<int:movie_id>/', add_review, name='add_review'),
    path('movie_reviews/<int:movie_id>/', movie_reviews, name='movie_reviews'),
    path('actor/<int:actor_id>/', actor_detail, name='actor_detail'),
    path('like/<int:movie_id>/', toggle_like, name='toggle_like'),
    path('', index, name='index')
]