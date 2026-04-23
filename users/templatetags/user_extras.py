from django import template

from users.models import Profile

register = template.Library()


@register.simple_tag
def user_avatar_url(user):
    if not user or not user.is_authenticated:
        return ""
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile.avatar_url
