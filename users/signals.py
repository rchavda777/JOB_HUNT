from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, Recruiter, JobSeeker

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a UserProfile when a new User is created."""
    if created:  # Only run when a new User is created
        role = getattr(instance, "selected_role", None)

        with transaction.atomic():  # Ensure atomicity
            user_profile, _ = UserProfile.objects.get_or_create(user=instance, defaults={'role': role})
            print(f"UserProfile created for {instance.username}")

            # Schedule role profile creation after the transaction commits
            transaction.on_commit(lambda: create_role_based_profile(user_profile))

def create_role_based_profile(user_profile):
    """Ensure a JobSeeker or Recruiter profile is created only after UserProfile is successfully saved."""
    with transaction.atomic():
        if user_profile.role == UserProfile.RoleChoices.RECRUITER:
            if not Recruiter.objects.filter(user_profile=user_profile).exists():
                Recruiter.objects.create(user_profile=user_profile)
                print(f"Recruiter profile created for {user_profile.user.username}")

        elif user_profile.role == UserProfile.RoleChoices.JOBSEEKER:
            if not JobSeeker.objects.filter(user_profile=user_profile).exists():
                JobSeeker.objects.create(user_profile=user_profile)
                print(f"JobSeeker profile created for {user_profile.user.username}")