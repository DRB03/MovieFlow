from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from movies.models import Movie, MovieReview, MovieComment
from movies.forms import MovieReviewForm, MovieCommentForm

def all_movies(request):
    movies= Movie.objects.all()
    context = {  'objetos':movies, 'message':'welcome' }
    return render(request,'movies/allmovies.html', context=context )

# Create your views here.
def index(request):
    movies = Movie.objects.all()
    context = { 'movies':movies, 'message':'welcome' }
    return render(request,'movies/index.html', context=context )
    
def movie(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    review_form = MovieReviewForm()
    context = { 'movie':movie, 'saludo':'welcome', 'review_form':review_form }
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

def add_review(request, movie_id):
    form = None
    movie = Movie.objects.get(id=movie_id)
    if request.method == 'POST':
        form = MovieReviewForm(request.POST)
        if form.is_valid():
            rating = form.cleaned_data['rating']
            title  = form.cleaned_data['title']
            review = form.cleaned_data['review']
            movie_review = MovieReview(
                    movie=movie,
                    rating=rating,
                    title=title,
                    review=review,
                    user=request.user)
            movie_review.save()
            return HttpResponse(status=204,
                                headers={'HX-Trigger': 'listChanged'})
    else:
        form = MovieReviewForm()
        return render(request,
                  'movies/movie_review_form.html',
                  {'movie_review_form': form, 'movie':movie})
