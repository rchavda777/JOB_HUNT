from django.contrib import admin
from users.models import UserProfile, Recruiter, JobSeeker, CompanyProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role")
    search_fields = ("user__username",)
    list_filter = ("role",)

@admin.register(Recruiter)
class RecruiterAdmin(admin.ModelAdmin):
    list_display = ("user_profile", "company", "position")
    search_fields = ("user_profile__user__username", "company__name")
    autocomplete_fields = ["user_profile", "company"]  # Improved lookup in admin panel

@admin.register(JobSeeker)
class JobSeekerAdmin(admin.ModelAdmin):
    list_display = ("user_profile", "skills")
    search_fields = ("user_profile__user__username", "display_skills")
    autocomplete_fields = ["user_profile"]  # Optimized admin lookup

@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "industry", "location", "contact_info")
    search_fields = ("name", "industry", "location")
    list_filter = ("industry", "location")