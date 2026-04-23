from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import users.models


def create_profiles_for_existing_users(apps, schema_editor):
    User = apps.get_model(settings.AUTH_USER_MODEL.split('.')[0], settings.AUTH_USER_MODEL.split('.')[1])
    Profile = apps.get_model("users", "Profile")
    for user in User.objects.all():
        Profile.objects.get_or_create(user=user)


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Profile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("profile_image", models.ImageField(blank=True, null=True, upload_to=users.models.user_avatar_upload_to)),
                (
                    "default_avatar",
                    models.CharField(
                        choices=[
                            ("users/avatars/default-1.svg", "Default avatar 1"),
                            ("users/avatars/default-2.svg", "Default avatar 2"),
                            ("users/avatars/default-3.svg", "Default avatar 3"),
                            ("users/avatars/default-4.svg", "Default avatar 4"),
                        ],
                        default="users/avatars/default-1.svg",
                        max_length=120,
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="profile", to=settings.AUTH_USER_MODEL),
                ),
            ],
        ),
        migrations.RunPython(create_profiles_for_existing_users, migrations.RunPython.noop),
    ]
