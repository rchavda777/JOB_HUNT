from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, HttpResponse
from django.contrib.auth.decorators import login_required
from jobs.forms import CompanyForm, JobForm
from jobs.models import Job, JobApplication
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from users.models import Recruiter, CompanyProfile, UserProfile
from .utils import send_notification_email


@login_required
def create_company_profile(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save(commit=False)

            # Get or create the user's profile
            user_profile, created = UserProfile.objects.get_or_create(user=request.user)

            # Save company and link to user profile
            company.user_profile = user_profile
            company.save()

            # Link the company to the recruiter's profile
            recruiter = Recruiter.objects.get(user_profile=user_profile)
            recruiter.company = company
            recruiter.save()

            messages.success(request, "Company profile created and linked successfully!")
            return redirect('edit_recruiter_profile')  # or wherever you want to go next
    else:
        form = CompanyForm()

    return render(request, 'jobs/recruiter/c.html', {'form': form})

@login_required
def post_job(request):
    try:
        recruiter = Recruiter.objects.get(user_profile=request.user.profile)
    except Recruiter.DoesNotExist:
        print("Recruiter profile not found!")  # Debugging
        raise PermissionDenied  # User is not allowed to post jobs

    if not recruiter.company:
        print("Recruiter has no company profile!")  # Debugging
        return redirect("create_company_profile")  #  Redirect to create company profile

    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = recruiter.user_profile.user
            job.company = recruiter.company  # Assign company from recruiter profile
            job.save()
            return redirect("job_list")
        else:
            print("Form errors:", form.errors)  # Debugging

    form = JobForm()
    return render(request, "jobs/recruiter/post_job.html", {"form": form})

def job_details(request, job_id):
    job = get_object_or_404(Job, pk=job_id)    
    has_applied = False

    if request.user.is_authenticated:
        user_profile = getattr(request.user, "profile", None)
        job_seeker = getattr(user_profile, "jobseeker_profile", None)

        if job_seeker:
            has_applied = job.applications.filter(job_seeker = job_seeker, job=job)
    return render(request, "jobs/job_details.html", {"job": job, "has_applied" : has_applied})

# List of Job Posted by Recruiter
@login_required
def job_list(request):
    jobs = Job.objects.none()  # Default to an empty queryset

    if request.user.is_authenticated:
        try:
            recruiter = request.user.profile.recruiter_profile  # Get recruiter profile
            jobs = Job.objects.filter(company=recruiter.company, posted_by=request.user, is_active=True)
        except Recruiter.DoesNotExist:
            pass  # If not a recruiter, jobs remain empty

    return render(request, "jobs/job_list.html", {"jobs": jobs})

# Apply for Job
@login_required
def apply_job(request, job_id):
    user = request.user  # Ensure user is authenticated

    # Check if user has a profile
    user_profile = getattr(user, "profile", None)
    if not user_profile:
        messages.error(request, "Your profile is incomplete. Please update your profile before applying.")
        return redirect("jobseeker_profile")

    # Check if user is a job seeker
    job_seeker = getattr(user_profile, "jobseeker_profile", None)
    if not job_seeker:
        messages.error(request, "Only job seekers can apply for jobs.")
        return redirect("job_details", job_id=job_id)

    # Retrieve the job
    job = get_object_or_404(Job, pk=job_id)

    # Check if the job already has an application from this user
    if JobApplication.objects.filter(job_seeker=job_seeker, job=job).exists():
        messages.warning(request, "You have already applied for this job.")
        return redirect("job_details", job_id=job_id)

    # Create job application
    JobApplication.objects.create(job_seeker=job_seeker, job=job)

    # Send email notification to job seeker
    try:
        send_notification_email(
            subject="Job Application Submitted",
            message=f"Dear {user.username},\n\nYou have successfully applied for the job '{job.title}'.\n\nBest of luck!",
            recipient_email=user.email,
        )

        # Send email to recruiter
        if job.posted_by and job.posted_by.email:
            send_notification_email(
                subject="New Job Application",
                message=(
                f"Hello {job.posted_by.username},\n\n"
                f"You've received a new application for your job posting titled \"{job.title}\".\n\n"
                f"Please log in to your recruiter dashboard to review the applicant's profile and take the next steps.\n\n"
                f"Regards,\nJob Hunt Team"
                ),
                recipient_email=job.posted_by.email,
            )
    except Exception as e:
        messages.error(request, f"Error sending email: {e}")

    messages.success(request, "Job application submitted successfully.")
    return redirect("job_details", job_id=job_id)

# View All job Application of All Job Posted by Recruiter
def view_all_applications(request):
    applications = JobApplication.objects.none()  #empty queryset
    search_query = request.GET.get( "search", "") 

    try:
        # Fetch all jobs posted by the current logged-in recruiter
        jobs_posted_by_recruiter = Job.objects.filter(posted_by=request.user)
        # Fetch applications for those jobs
        applications = JobApplication.objects.filter(job__in=jobs_posted_by_recruiter) 

        if search_query:
            applications = applications.filter(
                job_seeker__user_profile__user__username__icontains = search_query
            )
    except Job.DoesNotExist:
        pass  # No jobs found, return empty applications

    return render(request, "jobs/view_application.html", {"applications": applications})

# view all jobappliactions of a particular Jobseeker    
def my_application(request):
    user_profile = getattr(request.user, "profile", None)
    job_seeker = getattr(user_profile, "jobseeker_profile", None)

    if not job_seeker:
        messages.error(request, "No job applications found.")
        return redirect("job_list")

    applications = JobApplication.objects.select_related('job', 'job__company').filter(job_seeker=job_seeker)

    return render(request, "jobs/jobseeker/application_list.html", {"applications": applications})

# withrawal of job application by Job Seeker
@login_required
def withdraw_application(request, application_id):
    user_profile = getattr(request.user, "profile", None)
    job_seeker = getattr(user_profile, "jobseeker_profile", None)

    if not job_seeker:
        messages.error(request, "You are not authorized to withdraw applications.")
        return redirect(request.META.get("HTTP_REFERER", "jobseeker_dashboard"))

    application = get_object_or_404(JobApplication, id=application_id, job_seeker=job_seeker)

    if application.status.lower() == "pending":  
        application.delete()
        messages.success(request, "Your job application has been successfully withdrawn.")
    else:
        messages.error(request, "You can only withdraw pending applications.")

    return redirect(request.META.get("HTTP_REFERER", "jobseeker_dashboard"))

# Manage job Application
def view_appliaction(request, job_id):
    job = get_object_or_404(Job,pk = job_id)

    search_query = request.GET.get('search', '')
    applications = job.applications.select_related("job_seeker__user_profile__user")  

    if search_query :
        applications = applications.filter(
            job_seeker__user_profile__user__username__icontains = search_query
        )
    return render(request,"jobs/view_application.html", {"jobs" : job, "applications" : applications, "search_query" : search_query})
    
# Update JobApplication status (Accept/Reject) by Recruiter
def update_application_status(request, app_id, status):
    job_application = get_object_or_404(JobApplication, id=app_id)
    job_application.status = status  # Updating the status field
    job_application.save()  # Save the updated instance

    # Send email notification to job seeker
    subject = "Job Application Status Updated"
    message = f"Dear {job_application.job_seeker.user_profile.user.username},\n\nYour job application for '{job_application.job.title}' has been {status}.\n\nBest of luck!"
    send_notification_email(subject, message, job_application.job_seeker.user_profile.user.email)
    
    return redirect("view_applications", job_id=job_application.job.id)    

# Manage Job 
@login_required
def update_job_application(request, app_id, status):
    # Fetch job application instance
    job_application = get_object_or_404(JobApplication, id=app_id)

    # Ensure the logged-in user is the job seeker who applied
    if job_application.job_seeker.user_profile.user != request.user:
        return redirect("job_list")  # Redirect to job listings if unauthorized

    # Update the status
    job_application.status = status
    job_application.save()

    return redirect("job_detail", job_id=job_application.job.id)  # Redirect to job details

# Update Job
def update_job(request, job_id):
    job = get_object_or_404(Job, pk = job_id)
    if request.method == "POST":
        form = JobForm(request.POST, instance = job)
        if form.is_valid():
            form.save()
            return redirect('job_list')
    else:
        form = JobForm(instance = job)
    
    return render(request, 'jobs/recruiter/update_job.html', {'form' : form})

# Delete Job
def delete_job(request, job_id):
    job = get_object_or_404(Job, pk = job_id)
    if request.method == "POST":
        job.delete()
        return redirect('job_list')
    
    return render(request, 'jobs/recruiter/delete_job.html', {'job' : 'job'})


@login_required
def recommended_jobs(request):
    user_profile = getattr(request.user, "profile", None)
    job_seeker = getattr(user_profile, "jobseeker_profile", None)

    if not job_seeker:
        messages.error(request, "You must be jobseeker to view recommended jobs.")
        return redirect("job_list")
    
    seeker_skills = job_seeker.skills or []
    seeker_skills_lower = [skill.lower() for skill in seeker_skills]

    # get active jobs
    active_jobs = Job.objects.filter(
        is_active=True,
    ).order_by('-posted_at')

    # Filter jobs based on skills manually
    recommended_jobs = [
        job for job in active_jobs
        if any(skill.lower() in seeker_skills_lower for skill in job.required_skills)
    ]

    return render(
        request,
        "jobs/jobseeker/recommended_jobs.html",
        {"jobs": recommended_jobs}
    )