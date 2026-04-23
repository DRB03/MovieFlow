from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.


class Genre(models.Model):
    name = models.CharField(max_length=80)
    
    def __str__(self):
        return self.name
    
class Person(models.Model):
    name = models.CharField(max_length=128)
    tmdb_id = models.IntegerField(unique=True, null=True, blank=True)
    biography = models.TextField(blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    place_of_birth = models.CharField(max_length=255, blank=True, null=True)
    profile_path = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.name


class Job(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=80)
    overview = models.TextField()
    release_date = models.DateField()
    running_time = models.IntegerField()
    budget = models.IntegerField(blank=True, null=True)
    tmdb_id = models.IntegerField(blank=True, null=True)
    revenue = models.IntegerField(blank=True, null=True)
    poster_path = models.URLField(blank=True, null=True)
    genres = models.ManyToManyField(Genre)
    credits = models.ManyToManyField(Person, through='MovieCredit')

    def __str__(self):
        return f'{self.title} {self.release_date}'


class MovieCredit(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)

class MovieComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    # Conservamos tu campo numérico
    like = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)], null=True, blank=True)
    # AGREGAMOS EL CAMPO PARA EL TEXTO:
    comment_text = models.TextField(blank=True, null=True)


class MovieReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    # CAMBIO: Cambiamos MaxValueValidator a 10
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    review = models.TextField(blank=True)
    title = models.TextField(blank=False, null=False, default="Reseña")
