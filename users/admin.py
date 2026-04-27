from django.contrib import admin
from .models import Profile, UserFollow


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'default_avatar', 'updated_at')
	search_fields = ('user__username', 'user__email')


@admin.register(UserFollow)
class UserFollowAdmin(admin.ModelAdmin):
	list_display = ('follower', 'following', 'created_at')
	search_fields = ('follower__username', 'following__username')
