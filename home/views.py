from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib import messages
from home.forms import ContactForm
from jobs.models import Job
from django.core.mail import send_mail
from django.conf import settings 
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import datetime, timedelta
from django.utils import timezone

# Create your views here.
def home(request):
    jobs = Job.objects.filter(is_active=True).order_by('-posted_at')

    # Get filter parameters
    title_query = request.GET.get('title', '')
    company_query = request.GET.get('company', '')
    location_query = request.GET.get('location', '')
    job_type_query = request.GET.get('job_type', '')

    # Apply filters
    if title_query:
        jobs = jobs.filter(title__icontains=title_query)

    if company_query:
        jobs = jobs.filter(company__name__icontains=company_query)  

    if location_query:
        jobs = jobs.filter(location__icontains=location_query)

    if job_type_query:
        jobs = jobs.filter(job_type__iexact=job_type_query)

    # Count total resualts before pagination
    total_results = jobs.count()

    if total_results == 0:
        messages.info(request, "No results found for your search.")

    # Paginate
    paginator = Paginator(jobs, 6)  # 6 jobs per page
    page = request.GET.get('page')
    jobs = paginator.get_page(page)

    # For droupdown filter
    all_locations = Job.objects.values_list('location', flat=True).distinct()
    all_job_types = Job.objects.values_list('job_type', flat=True).distinct()

    return render(request, "home/home2.html", {
        'jobs': jobs,
        'total_resualts' : total_results,
        'filters': {
            'title': title_query,
            'company': company_query,
            'location': location_query,
            'job_type': job_type_query, 
        },
        'all_locations' : all_locations,
        'all_job_types' : all_job_types,
        'today_minus_3' : timezone.now() - timezone.timedelta(days=3),
    })

def contact_view(request):  
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form .is_valid():
            form.save()
            messages.success(request, "Your Message has been sent successfuly !")
            return redirect("contact")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ContactForm()

    return render(request, "home/contact.html", {"form" : form})

