from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.templatetags.static import static


def user_avatar_upload_to(instance, filename):
	return f"avatars/users/user_{instance.user_id}/{filename}"


class Profile(models.Model):
	DEFAULT_AVATAR_CHOICES = [
		("users/avatars/default-1.svg", "Default avatar 1"),
		("users/avatars/default-2.svg", "Default avatar 2"),
		("users/avatars/default-3.svg", "Default avatar 3"),
		("users/avatars/default-4.svg", "Default avatar 4"),
	]

	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
	profile_image = models.ImageField(upload_to=user_avatar_upload_to, blank=True, null=True)
	default_avatar = models.CharField(max_length=120, choices=DEFAULT_AVATAR_CHOICES, default="users/avatars/default-1.svg")
	updated_at = models.DateTimeField(auto_now=True)

	@property
	def avatar_url(self):
		if self.profile_image:
			return self.profile_image.url
		return static(self.default_avatar)

	def __str__(self):
		return f"Profile<{self.user.username}>"


class UserFollow(models.Model):
	"""follower follows following (asymmetric social graph)."""

	follower = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="following_relations",
	)
	following = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="follower_relations",
	)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=["follower", "following"], name="unique_user_follow_pair"),
		]
		indexes = [
			models.Index(fields=["follower"]),
			models.Index(fields=["following"]),
		]

	def __str__(self):
		return f"{self.follower_id} → {self.following_id}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
	profile, _ = Profile.objects.get_or_create(user=instance)
	profile.save()
