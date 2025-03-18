from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib import messages
from home.forms import ContactForm
from jobs.models import Job
from django.core.mail import send_mail
from django.conf import settings 

# Create your views here.
def home (request) :
    jobs = Job.objects.order_by("-posted_at")[:6]  # Fetch latest 6 jobs..
    return render(request, "home/home2.html", {"jobs": jobs})

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

def send_test_email(request):
    send_mail(
        subject="Hello from Django",
        message="This is a test email sent using SendGrid.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list= ["rchavda2690@gmail.com"],
        fail_silently=False,
    )
    return HttpResponse("Email sent successfully!")