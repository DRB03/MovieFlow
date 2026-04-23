from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from movies.models import Movie, MovieReview, MovieComment, Person, MovieCredit, MovieLike
from movies.forms import MovieReviewForm, MovieCommentForm
from django.db.models import Q, Avg, Count
from movies.models import Movie, Genre
from django.contrib.auth.decorators import login_required
from movies.recommendation_engine import RecommendationEngine
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST

def all_movies(request):
    movies= Movie.objects.all()
    context = {  'objetos':movies, 'message':'welcome' }
    return render(request,'movies/allmovies.html', context=context )

# Create your views here.
def index(request):
    # 1. Atrapamos los filtros que vienen del Header (Buscador y Barra Lateral)
    query = request.GET.get('search', '')
    genre_filter = request.GET.get('genre', '')
    sort_by = request.GET.get('sort', '-release_date') # Por defecto las más recientes

    # 2. Empezamos trayendo todas las películas
    movies = Movie.objects.all()

    # 3. Si el usuario escribió en el buscador, filtramos por título
    if query:
        movies = movies.filter(Q(title__icontains=query))

    # 4. Si el usuario seleccionó un género en la barra lateral, filtramos por género
    if genre_filter:
        movies = movies.filter(genres__name=genre_filter)

    # 5. Aplicamos el ordenamiento seleccionado
    valid_sorts = ['-release_date', 'release_date', 'title', '-title', '-revenue']
    if sort_by in valid_sorts:
        movies = movies.order_by(sort_by)
    else:
        movies = movies.order_by('-release_date')

    # 6. Calculamos la mitad exacta para el botón de "Mostrar Más" en index.html
    total_movies = movies.count()
    half_count = (total_movies + 1) // 2 

    # 7. Enviamos las variables al contexto para que el HTML sepa qué mostrar seleccionado
    context = {
        'movies': movies,
        'half_count': half_count,
        'search_value': query,           # Mantiene el texto en el buscador
        'selected_genre': genre_filter,  # Mantiene el género seleccionado en el menú
        'selected_sort': sort_by,        # Mantiene el orden seleccionado en el menú
    }
    return render(request, 'movies/index.html', context)
    
def movie(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    review_form = MovieReviewForm()
    review_stats = movie.moviereview_set.aggregate(avg_rating=Avg('rating'), total_reviews=Count('id'))
    recommender = RecommendationEngine(movie=movie, user=request.user, limit=6)
    recommendations = recommender.get_recommendations()
    user_liked = (
        request.user.is_authenticated
        and MovieLike.objects.filter(user=request.user, movie=movie).exists()
    )
    like_count = movie.likes.count()
    context = {
        'movie': movie,
        'saludo': 'welcome',
        'review_form': review_form,
        'avg_user_score': review_stats['avg_rating'],
        'total_user_reviews': review_stats['total_reviews'],
        'recommendations': recommendations,
        'user_liked': user_liked,
        'like_count': like_count,
    }
    return render(request,'movies/movie.html', context=context )

def movie_reviews(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    return render(request,'movies/reviews.html', context={'movie':movie } )

def add_comment(request, movie_id):
    form = None
    movie = Movie.objects.get(id=movie_id)
    if request.method == 'POST':
        form = MovieCommentForm(request.POST)
        if form.is_valid():
            review = form.cleaned_data['review']
            movie_comment = MovieComment(
                movie=movie,
                comment_text=review,
                user=request.user)
            movie_comment.save()
            return HttpResponseRedirect('/movies/')
    else:
        form = MovieCommentForm()
        return render(request,
                      'movies/movie_comment_form.html',
                        {'form': form, 'movie':movie})

@login_required(login_url='/users/login')
def add_review(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    
    if request.method == 'POST':
        form = MovieReviewForm(request.POST)
        if form.is_valid():
            rating = form.cleaned_data['rating']
            title  = form.cleaned_data['title']
            review = form.cleaned_data['review']
            
            # Guardamos la reseña en la base de datos
            movie_review = MovieReview(
                movie=movie,
                rating=rating,
                title=title,
                review=review,
                user=request.user
            )
            movie_review.save()
            
            # CAMBIO CLAVE: El profe pidió redirigir a la vista de la película
            # Usamos el 'name' que acabamos de agregar en urls.py
            return redirect('movie_detail', movie_id=movie.id)
    else:
        # Si entra por GET, solo le mostramos el formulario vacío
        form = MovieReviewForm()
        
    # Renderiza la página dedicada para crear la reseña
    return render(request, 'movies/movie_review_form.html', {
        'movie_review_form': form, 
        'movie': movie
    })

def actor_detail(request, actor_id):
    actor = get_object_or_404(Person, id=actor_id)
    # Only movies already stored in our DB
    movies = Movie.objects.filter(moviecredit__person=actor).distinct()
    context = {
        'actor': actor,
        'movies': movies,
    }
    return render(request, 'movies/actor.html', context=context)

@login_required(login_url='/users/login')
@require_POST
def toggle_like(request, movie_id):
    """Alterna el estado Like/Unlike del usuario sobre una película.
    Devuelve JSON con {liked: bool, count: int} para actualizar el botón sin recargar."""
    movie = get_object_or_404(Movie, id=movie_id)
    like, created = MovieLike.objects.get_or_create(user=request.user, movie=movie)
    if not created:
        # Ya existía → quitar like
        like.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({'liked': liked, 'count': movie.likes.count()})

@login_required(login_url='/users/login')
def collections(request):
    """Vista 'My Movies': muestra las películas a las que el usuario dio Like."""
    liked_movies = Movie.objects.filter(
        likes__user=request.user
    ).prefetch_related('genres').order_by('-likes__created_at')
    context = {
        'liked_movies': liked_movies,
    }
    return render(request, 'movies/collections.html', context=context)