from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    class RoleChoices(models.TextChoices):
        JOBSEEKER = "jobseeker", "Jobseeker"
        RECRUITER = "recruiter", "Recruiter"

    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="User"
    )
    role = models.CharField(
        max_length=10,
        choices=RoleChoices.choices,
        verbose_name="User Role"
    )
    profile_picture = models.ImageField(
        upload_to="profile_picture",
        blank=True,
        null=True,
        verbose_name="Profile Picture"
    )
    mobile_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name="Mobile Number"
    )
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name="Address"
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        verbose_name="Date of Birth"
    )
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        verbose_name="Gender",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def is_jobseeker(self):
        return self.role == self.RoleChoices.JOBSEEKER

    def is_recruiter(self):
        return self.role == self.RoleChoices.RECRUITER

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    

# Recruiter Profile (linked with UserProfile)
class Recruiter(models.Model):
    user_profile = models.OneToOneField(
        "UserProfile",
        on_delete=models.CASCADE,
        verbose_name="User",
        related_name="recruiter_profile" 
    )
    company = models.ForeignKey(
        "CompanyProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Company",
        related_name="recruiters"
    )
    position = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Position in Company"
    )

    class Meta:
        verbose_name = "Recruiter"
        verbose_name_plural = "Recruiters"

    def __str__(self):
        return f"{self.user_profile.user.username} - {self.position or 'No Position'}"


# Job Seeker Profile (Linked to UserProfile)
class JobSeeker(models.Model):
    user_profile = models.OneToOneField(
        "UserProfile",
        on_delete=models.CASCADE,
        verbose_name="User",
        related_name="jobseeker_profile"
    )
    resume = models.FileField(
        upload_to="resumes/",
        blank=True,   
        null=True,
        verbose_name="Resume"
    )
    skills = models.JSONField(
        default = list,
        blank = True,
        verbose_name = "Skills"
    )
    job_preference = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Job Preference",
    )
    experience = models.PositiveIntegerField(
        verbose_name= "Years of Experience",
        blank=True,
        null=True,
        help_text= "Enter experience in years"
    )    
    class Meta:
        verbose_name = "Job Seeker"
        verbose_name_plural = "Job Seekers"

    def __str__(self):
        return f"{self.user_profile.user.username} (Job Seeker)"


# Company Profile (linked to Recruiter)
class CompanyProfile(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Company Name",
    )
    industry = models.CharField(
        max_length=50,
        verbose_name="Industry Type"
    )
    location = models.CharField(
        max_length=50,
        verbose_name="Company Location"
    )
    website = models.URLField(
        blank=True,
        null=True,
        verbose_name="Company Website"
    )
    contact_info = models.EmailField(
        verbose_name="Email ID"
    )
    description = models.TextField(
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Company Profile"
        verbose_name_plural = "Company Profiles"

    def __str__(self):
        return self.name
