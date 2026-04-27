from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Count, Q
from django.utils import timezone

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


class MovieLike(models.Model):
    """Almacena los Me Gusta de cada usuario sobre una película."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movie_likes')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'movie')  # Un usuario solo puede dar like una vez

    def __str__(self):
        return f'{self.user.username} ❤ {self.movie.title}'


class MovieReview(models.Model):
    """Top-level rows are full reviews; rows with ``parent`` set are thread replies."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
    )
    # CAMBIO: Cambiamos MaxValueValidator a 10 (null for reply rows)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True,
        blank=True,
    )
    review = models.TextField(blank=True)
    title = models.TextField(blank=True, null=True, default="")
    created_at = models.DateTimeField(default=timezone.now)
    like_count = models.PositiveIntegerField(default=0)
    dislike_count = models.PositiveIntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=["movie", "parent"]),
        ]

    def clean(self):
        super().clean()
        if self.parent_id:
            if self.rating is not None or (self.title and self.title.strip()):
                raise ValidationError("Las respuestas no deben llevar título ni calificación.")
            if not (self.review or "").strip():
                raise ValidationError("El texto de la respuesta es obligatorio.")
            if self.parent_id == self.pk:
                raise ValidationError("Un comentario no puede ser padre de sí mismo.")
        else:
            if self.rating is None:
                raise ValidationError("La calificación es obligatoria para una reseña principal.")
            if not (self.title or "").strip():
                raise ValidationError("El título es obligatorio para una reseña principal.")

    def __str__(self):
        return f"MovieReview<{self.movie_id} by {self.user_id}>"

    def sync_reaction_counts(self):
        stats = self.reactions.aggregate(
            likes=Count("id", filter=Q(vote=MovieReviewReaction.VOTE_LIKE)),
            dislikes=Count("id", filter=Q(vote=MovieReviewReaction.VOTE_DISLIKE)),
        )
        MovieReview.objects.filter(pk=self.pk).update(
            like_count=stats["likes"] or 0,
            dislike_count=stats["dislikes"] or 0,
        )


class MovieReviewReaction(models.Model):
    """One row per user per review: like (+1) or dislike (-1), mutually exclusive."""

    VOTE_LIKE = 1
    VOTE_DISLIKE = -1
    VOTE_CHOICES = (
        (VOTE_LIKE, "like"),
        (VOTE_DISLIKE, "dislike"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="review_reactions")
    review = models.ForeignKey(MovieReview, on_delete=models.CASCADE, related_name="reactions")
    vote = models.SmallIntegerField(choices=VOTE_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "review"], name="unique_review_reaction_per_user"),
        ]
        indexes = [
            models.Index(fields=["review"]),
        ]

    def __str__(self):
        return f"{self.user_id} {self.vote} review {self.review_id}"
