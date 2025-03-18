from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, HttpResponse
from django.contrib.auth.decorators import login_required
from jobs.forms import CompanyForm, JobForm
from jobs.models import Job, JobApplication
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from users.models import Recruiter, CompanyProfile, UserProfile

@login_required
def create_company_profile(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save(commit=False)  # Do not save yet
            
            # Ensure user has a UserProfile
            user_profile, created = UserProfile.objects.get_or_create(user=request.user)
            
            company.user_profile = user_profile  # Assign UserProfile to company
            company.save()  # Save the form with UserProfile
            return redirect('company_list')  # Redirect after successful creation
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

# Apply for Job.
def apply_job(request, job_id):
    user_profile = getattr(request.user, "profile", None)
    job_seeker = getattr(user_profile, "jobseeker_profile", None)
    
    if not job_seeker:
        messages.error(request, "Only job seekers can apply for jobs.")
        return redirect("job_details", job_id = job_id)

    job = get_object_or_404(Job, pk = job_id)

    JobApplication.objects.create(job_seeker = job_seeker, job = job)
    messages.success(request, "Job application submitted successfully.")
    return redirect("job_details", job_id = job_id)

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
    jobseeker = request.user.profile.jobseeker_profile
    applications = JobApplication.objects.filter(job_seeker=jobseeker).select_related("job", "job__company")

    # Debugging: Print job details in console
    # for app in applications:
    #     print(f"Job Title: {app.job.title}, Company: {app.job.company.name}, Location: {app.job.location}")

    # return HttpResponse(f"Total Applications: {applications.count()}")
    return render(request, "jobs/jobseeker/application_list.html", {"applications" : applications})

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