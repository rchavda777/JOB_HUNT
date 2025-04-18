from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from users.models import UserProfile, Recruiter, JobSeeker
from jobs.models import Job,JobApplication
from django.contrib import messages
from django.db import transaction
from .forms import SignupForm, LoginForm, UserProfileUpdateForm, JobSeekerUpdateForm, RecruiterProfileUpdateForm, CompanyProfileUpdateForm

def SignupPage(request):
    if request.method == "POST":
        form = SignupForm(request.POST)  

        if form.is_valid():
            with transaction.atomic():
                user = form.save(commit=False)
                user.selected_role = form.cleaned_data.get("role")
                user.save()
                  
            messages.success(request, "Account created sucessfully !")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SignupForm()

    return render(request, "users/signup.html", {"form": form})


def LoginPage(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            uname = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=uname, password=password)

            if user is not None:
                login(request, user)
                # Get user role and redirect accordingly
                try:
                    profile = UserProfile.objects.get(user=user)
                except UserProfile.DoesNotExist:
                    messages.error(request, "User profile not found.")
                    return redirect('login')

                print(profile)
                if profile.role == 'recruiter':
                    return redirect("recruiter_dashboard")
                else:
                    return redirect("jobseeker_dashboard")    
            else:
                messages.error(request, "Invalid username or password")
    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form})

@login_required
def recruiter_dashboard(request):
    try:
        # Get the logged-in user instance
        user = request.user  

        # Get the user's profile
        user_profile = UserProfile.objects.get(user=user)

        if not user_profile.is_recruiter():
            return HttpResponseForbidden("You are not authorized to access this page.")

        # Get the recruiter instance
        recruiter = Recruiter.objects.get(user_profile=user_profile)  
        
        company_profile = recruiter.company  
        jobs = Job.objects.filter(posted_by=recruiter.user_profile.user)  

        # Count 
        total_jobs = jobs.count()
        active_jobs = jobs.filter(is_active=True).count()  
        total_applications = JobApplication.objects.filter(job__in=jobs).count()

    except (UserProfile.DoesNotExist, Recruiter.DoesNotExist):
        return HttpResponseForbidden("Recruiter profile not found.")

    # Pass data to the template
    context = {
        'company_profile': company_profile,
        'jobs': jobs,
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_applications': total_applications,
    }
    return render(request, "users/recruiter_dashboard.html", context)


@login_required
def jobseeker_dashboard(request):
    try:
        user = request.user
        user_profile = UserProfile.objects.get(user=user)

        if not user_profile.is_jobseeker():
            return HttpResponseForbidden("You are not authorized to access the page.")
        
        # Fetch JobSeeker profile
        job_seeker = JobSeeker.objects.get(user_profile=user_profile)

        # Fetch job applications with related job details
        applications = JobApplication.objects.select_related('job', 'job__company').filter(job_seeker=job_seeker)

    except (UserProfile.DoesNotExist, JobSeeker.DoesNotExist):
        return HttpResponseForbidden("Jobseeker profile not found.")

    # Pass data to template
    return render(request, "users/jobseeker_dashboard.html", {
        "job_seeker": job_seeker,
        "applications": applications
    })

@login_required
def Logout_user(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('home')

@login_required 
def update_user_profile(request):
    user_profile = request.user.profile  # Get the logged-in user's profile
    
    if request.method == "POST":
        user_form = UserProfileUpdateForm(request.POST, request.FILES, instance=user_profile)
        
        # If the user is a job seeker, include the JobSeekerUpdateForm
        if user_profile.is_jobseeker:
            job_seeker_form = JobSeekerUpdateForm(request.POST, request.FILES, instance=user_profile.jobseeker_profile)
        else:
            job_seeker_form = None
        
        if user_form.is_valid() and (job_seeker_form is None or job_seeker_form.is_valid()):
            user_form.save()
            if job_seeker_form:
                job_seeker_form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect("jobseeker_profile")  # Redirect to the same page after update
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        user_form = UserProfileUpdateForm(instance=user_profile)
        job_seeker_form = JobSeekerUpdateForm(instance=user_profile.jobseeker_profile) if user_profile.is_jobseeker() else None
    
    context = {
        "user_form": user_form,
        "job_seeker_form": job_seeker_form,
    }
    return render(request, "users/user_profile_update.html", context)

@login_required
def edit_recruiter_profile(request):
    user_profile = request.user.profile

    # Check if the user is a recruiter
    if not user_profile.is_recruiter():
        return HttpResponseForbidden("You are not authorized to access this page.")

    # Fetch recruiter and company data from the profile
    recruiter = user_profile.recruiter_profile
    company = recruiter.company

    # Process the form data
    if request.method == "POST":
        user_form = UserProfileUpdateForm(request.POST, request.FILES, instance=user_profile)
        recruiter_form = RecruiterProfileUpdateForm(request.POST, instance=recruiter)
        company_form = CompanyProfileUpdateForm(request.POST, instance=company)

        if user_form.is_valid() and recruiter_form.is_valid() and company_form.is_valid():
            user_form.save()
            recruiter_form.save()
            company_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("recruiter_dashboard")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        user_form = UserProfileUpdateForm(instance=user_profile)
        recruiter_form = RecruiterProfileUpdateForm(instance=recruiter)
        company_form = CompanyProfileUpdateForm(instance=company)

    # Prepare context for template rendering
    context = {
        'user_profile_form': user_form,
        'recruiter_form': recruiter_form,
        'company_form': company_form,
        'user': request.user  # Add user to access profile picture, etc.
    }

    return render(request, 'users/recruiter_profile_update.html', context)


@login_required
def remove_company(request):
    if request.method == 'POST':
        recruiter = request.user
        if recruiter.company:
            recruiter.company = None
            recruiter.save()
            messages.success(request, "Company removed successfully.")
        else:
            messages.warning(request, "No company associated.")
    return redirect('edit_recruiter_profile')