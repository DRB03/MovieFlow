from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'default_avatar', 'updated_at')
	search_fields = ('user__username', 'user__email')
