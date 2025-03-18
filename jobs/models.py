from django.db import models
from django.core.validators import MinValueValidator
from users.models import CompanyProfile, JobSeeker, User

# Job Model
class Job(models.Model):
    class JobType(models.TextChoices):
        FULL_TIME = "Full-time", "Full-time"
        PART_TIME = "Part-time", "Part-time"
        INTERNSHIP = "Internship", "Internship"
        CONTRACT = "Contract", "Contract"

    company = models.ForeignKey(
        CompanyProfile,
        on_delete=models.CASCADE,
        related_name="jobs",
        verbose_name="Company"
    )
    title = models.CharField(
        max_length=100,
        verbose_name="Job Title"
    )
    description = models.TextField(
        verbose_name="Job Description"
    )
    location = models.CharField(
        max_length=100,
        verbose_name="Job Location"
    )
    required_skills = models.JSONField(
        default=list,

        verbose_name="Required Skills"
    )
    job_type = models.CharField(
        max_length=20,
        choices=JobType.choices,
        default=JobType.FULL_TIME,
        verbose_name="Job Type"
    )
    salary_min = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Minimum Salary",
        validators=[MinValueValidator(1)]
    )
    salary_max = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Maximum Salary",
        validators=[MinValueValidator(1)]
    )
    posted_by = models.ForeignKey(
        User,  # Link job posting to a user
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posted_jobs",
        verbose_name="Posted By"
    )
    posted_at = models.DateField(
        auto_now_add=True,
        verbose_name="Job Posted Date"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Is Active"
    )

    class Meta:
        verbose_name = "Job"
        verbose_name_plural = "Jobs"
        ordering = ["-posted_at"]

    def save(self, *args, **kwargs):
        if self.salary_min and self.salary_max and self.salary_max < self.salary_min:
            raise ValueError("Maximum salary cannot be lower than minimum salary.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} at {self.company.name}"

# Job Application Model
class JobApplication(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "Pending", "Pending"
        ACCEPTED = "Accepted", "Accepted"
        REJECTED = "Rejected", "Rejected"

    job_seeker = models.ForeignKey(
        JobSeeker, 
        on_delete=models.CASCADE,
        verbose_name="Job Seeker Name",
        related_name="applications"
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="applications"
    )
    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
        verbose_name="Application Status"
    )
    applied_at = models.DateField(
        auto_now_add=True,
        verbose_name="Job Application Date"
    )

    class Meta:
        verbose_name = "Job Application"
        verbose_name_plural = "Job Applications"
        ordering = ["-applied_at"]

    def __str__(self):
        return f"{self.job_seeker.user_profile.user.username} applied for {self.job.title}"
