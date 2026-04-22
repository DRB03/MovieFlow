from collections import defaultdict
from math import sqrt

from django.db.models import Avg, Count, Q

from .models import Movie, MovieReview


class RecommendationEngine:
    def __init__(self, movie, user=None, limit=6):
        self.movie = movie
        self.user = user
        self.limit = limit

    def get_recommendations(self):
        if self.user and self.user.is_authenticated:
            collaborative = self._collaborative_recommendations()
            if len(collaborative) >= self.limit:
                return collaborative[: self.limit]

            excluded_ids = {item["movie"].id for item in collaborative}
            fallback = self._content_based_recommendations(excluded_ids=excluded_ids)
            return (collaborative + fallback)[: self.limit]

        return self._content_based_recommendations()[: self.limit]

    def _collaborative_recommendations(self):
        user_ratings = self._user_ratings_map(self.user.id)
        if len(user_ratings) < 2:
            return []

        movie_genre_ids = list(self.movie.genres.values_list("id", flat=True))
        watched_ids = set(user_ratings.keys())
        watched_ids.add(self.movie.id)

        peer_ids = MovieReview.objects.filter(movie=self.movie).exclude(user=self.user).values_list("user_id", flat=True).distinct()

        peer_similarities = {}
        for peer_id in peer_ids:
            peer_ratings = self._user_ratings_map(peer_id)
            similarity = self._cosine_similarity(user_ratings, peer_ratings)
            if similarity > 0:
                peer_similarities[peer_id] = similarity

        if not peer_similarities:
            return []

        scored_movies = defaultdict(lambda: {"weighted_sum": 0.0, "sim_sum": 0.0, "peer_votes": 0})

        peer_reviews = MovieReview.objects.filter(user_id__in=peer_similarities.keys()).exclude(movie_id__in=watched_ids).filter(movie__genres__id__in=movie_genre_ids).select_related("movie").distinct()

        for review in peer_reviews:
            sim = peer_similarities.get(review.user_id)
            if not sim:
                continue
            entry = scored_movies[review.movie_id]
            entry["weighted_sum"] += sim * review.rating
            entry["sim_sum"] += sim
            entry["peer_votes"] += 1

        if not scored_movies:
            return []

        movie_ids = list(scored_movies.keys())
        avg_map = {
            row["movie_id"]: row["avg_rating"]
            for row in MovieReview.objects.filter(movie_id__in=movie_ids).values("movie_id").annotate(avg_rating=Avg("rating"))
        }
        shared_genres_map = self._shared_genres_count(movie_ids)
        movie_map = {movie.id: movie for movie in Movie.objects.filter(id__in=movie_ids).prefetch_related("genres")}

        ranked = []
        for movie_id, values in scored_movies.items():
            if values["sim_sum"] <= 0:
                continue

            predicted_rating = values["weighted_sum"] / values["sim_sum"]
            global_avg = avg_map.get(movie_id) or 0
            genre_matches = shared_genres_map.get(movie_id, 0)
            final_score = (predicted_rating * 0.65) + (global_avg * 0.25) + (genre_matches * 2.5)

            movie_obj = movie_map.get(movie_id)
            if not movie_obj:
                continue

            ranked.append(
                {
                    "movie": movie_obj,
                    "avg_rating": global_avg,
                    "score": final_score,
                }
            )

        ranked.sort(key=lambda item: item["score"], reverse=True)
        return ranked[: self.limit]

    def _content_based_recommendations(self, excluded_ids=None):
        excluded_ids = excluded_ids or set()
        excluded_ids.add(self.movie.id)

        movie_genre_ids = list(self.movie.genres.values_list("id", flat=True))
        if not movie_genre_ids:
            return []

        candidates = (
            Movie.objects.filter(genres__id__in=movie_genre_ids)
            .exclude(id__in=excluded_ids)
            .annotate(avg_rating=Avg("moviereview__rating"), shared_genres=Count("genres", filter=Q(genres__id__in=movie_genre_ids), distinct=True))
            .order_by("-shared_genres", "-avg_rating", "-release_date")
            .distinct()
        )

        recommendations = []
        for movie_obj in candidates[: self.limit * 2]:
            avg_rating = movie_obj.avg_rating or 0
            recommendations.append(
                {
                    "movie": movie_obj,
                    "avg_rating": avg_rating,
                    "score": (movie_obj.shared_genres * 3) + (avg_rating * 0.4),
                }
            )

        recommendations.sort(key=lambda item: item["score"], reverse=True)
        return recommendations[: self.limit]

    @staticmethod
    def _user_ratings_map(user_id):
        return dict(MovieReview.objects.filter(user_id=user_id).values_list("movie_id", "rating"))

    def _shared_genres_count(self, movie_ids):
        movie_genre_ids = list(self.movie.genres.values_list("id", flat=True))
        rows = (
            Movie.objects.filter(id__in=movie_ids, genres__id__in=movie_genre_ids)
            .values("id")
            .annotate(matches=Count("genres", distinct=True))
        )
        return {row["id"]: row["matches"] for row in rows}

    @staticmethod
    def _cosine_similarity(user_a_ratings, user_b_ratings):
        overlap = set(user_a_ratings.keys()) & set(user_b_ratings.keys())
        if len(overlap) < 2:
            return 0.0

        dot_product = sum(user_a_ratings[mid] * user_b_ratings[mid] for mid in overlap)
        norm_a = sqrt(sum((user_a_ratings[mid] ** 2) for mid in overlap))
        norm_b = sqrt(sum((user_b_ratings[mid] ** 2) for mid in overlap))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)