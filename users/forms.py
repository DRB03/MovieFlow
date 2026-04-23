from django import forms

from .models import Profile


class ProfileAvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["profile_image", "default_avatar"]
        widgets = {
            "default_avatar": forms.RadioSelect,
        }

    def clean_profile_image(self):
        image = self.cleaned_data.get("profile_image")
        if image and image.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Profile image must be 5MB or smaller.")
        return image
