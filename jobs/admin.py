from django.contrib import admin
from .models import CompanyProfile, JobApplication, Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "job_type", "location", "posted_at", "is_active")
    search_fields = ("job_type", "is_active", "company")
    list_filter = ("title", "company__name", "location", "required_skills")

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ("job_seeker", "job", "status", "applied_at")
    list_filter = ("status", "applied_at")
    search_fields = ("job_seeker__user_profile__user__username", "job__title")

