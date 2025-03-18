import re
import os
from dotenv import load_dotenv
import requests
from django.db import transaction
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from users.models import UserProfile, Recruiter, JobSeeker

load_dotenv()

class SignupForm(forms.ModelForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-input'}),
        label="Password",
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'form-input'}),
        label="Confirm Password",
    )

    # Role selection field (jobseeker/recruiter)
    ROLE_CHOICES = (
        ('jobseeker', 'Jobseeker'),
        ('recruiter', 'Recruiter'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.Select(attrs={'class': 'custom-select'}), label="Register as")

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'form-input'}),
        }

    # Validate username (ensure it is unique)
    def clean_username(self):
        username = self.cleaned_data.get('username')

        if not username:
            raise forms.ValidationError("Username is required.")

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username is already taken. Please choose another one.")
        return username

    # Validate email (ensure it is unique & only allow gmail)
    def clean_email(self):
        email = self.cleaned_data.get('email')

        if not email:
            raise forms.ValidationError("Email is required.")

        # Corrected Regex for Gmail validation
        gmail_pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
        if not re.match(gmail_pattern, email, re.IGNORECASE):
            raise forms.ValidationError("Only Gmail addresses are allowed.")

        # Ensure email is unique
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")

        # # **MailboxLayer API Validation**
        API_KEY = os.getenv("MAILBOXLAYER_APIKEY")

        if not API_KEY:
            raise ValidationError("API key is missing. Please contact the site administrator.")

        # Make API request
        try:
            url = f"https://apilayer.net/api/check?access_key={API_KEY}&email={email}"
            response = requests.get(url)

            response.raise_for_status()  # Raise an error if API call fails
            data = response.json()

            # **Check email validation status**
            valid_statuses = ["valid", "catch-all"]  # Acceptable statuses
            if not data.get("format_valid"):
                raise ValidationError("Invalid email format.")
            
            # if not data.get("smtp_check"):
            #     raise ValidationError("Email server did not validate this email.")

            if data.get("disposable"):
                raise ValidationError("Disposable email addresses are not allowed.")

        except requests.exceptions.RequestException as e:
            raise ValidationError(f"Error validating email: {e}")

        return email.lower()


    # Password strength validation
    def validate_password_strength(self, password):
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", password):
            raise ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r"[0-9]", password):
            raise ValidationError("Password must contain at least one digit.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValidationError("Password must contain at least one special character.")

    # Validate passwords
    def clean(self):
        cleaned_data = super().clean()
        #cleaned_data.get("role")
        print("Cleaned Data :", cleaned_data) #Debugging to check the role
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if not password1:
            self.add_error('password1', "Password is required.")
        if not password2:
            self.add_error('password2', "Confirm Password is required.")

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Passwords do not match.")

        if password1:
            try:
                self.validate_password_strength(password1)
            except ValidationError as e:
                self.add_error('password1', e)

        return cleaned_data

    def save(self, commit=True):
        with transaction.atomic(): # Either all or do nothing. User,UserProfile,(Jobseeker/Recruiter) profile create or none 
            user = super().save(commit=False)
            user.set_password(self.cleaned_data["password1"])
            role = self.cleaned_data.get("role")

            user.selected_role = role
            # Debugging: Check role value
            print(f"Role from form: {role}")

            if commit:
                user.save()

                # Check if UserProfile already exists, and create it only if not
                user_profile, created = UserProfile.objects.get_or_create(user=user)
                if created:
                    user_profile.role = role  # Explicitly assign the role here
                    user_profile.save()

                # Ensure no existing profiles before creating new ones
                if role == UserProfile.RoleChoices.RECRUITER:
                    if not hasattr(user_profile, 'recruiter'):
                        Recruiter.objects.create(user_profile=user_profile)
                elif role == UserProfile.RoleChoices.JOBSEEKER:
                    if not hasattr(user_profile, 'jobseeker'):
                        JobSeeker.objects.create(user_profile=user_profile)

        return user


# login Form
class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'placeholder': 'Enter Username', 'id': 'username', 'class': 'form-input'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Password', 'id': 'password', 'class': 'form-input'
    }))

class UserProfileUpdateForm(forms.ModelForm):
    
    class Meta:
        model = UserProfile
        fields = [
            "profile_picture", "mobile_number", "address", "date_of_birth", "gender"
        ]

        labels = {
            "mobile_number" : "Mobile Number",
            "address" : "Address",
            "date_of_birth" : "Date of Birth",
            "gender" : "Gender"
        }

        widgets = {
            "mobile_number" : forms.TextInput(attrs={"placeholder": "Mobile Number", "class": "form-input"}),
            "address" : forms.Textarea(attrs={"placeholder": "Address", "class": "form-input"}),
            "date_of_birth" : forms.DateInput(attrs={"placeholder": "Date of Birth", "type" : "date"}),
            "gender" : forms.Select(attrs={"class" : "form-input"}),
        }

    def clean_profile_picture(self):
        picture = self.cleaned_data.get("profile_picture")
        if picture:
            if picture.size > 2 * 1024 * 1024:  # 2MB limit
                raise forms.ValidationError("Profile picture size should not exceed 2MB.")
        return picture

class JobSeekerUpdateForm(forms.ModelForm):
    
    class Meta:
        model = JobSeeker
        fields = [
            "resume", "skills", "job_preference", "experience"
        ]

        labels = {
            "resume" : "Resume",
            "skills" : "Skills",
            "job_preference" : "Job Preference Title",
            "experience" : "Year of Experiences"
        }

        widgets = {
            "skills" : forms.TextInput(attrs={"placeholder" : "Seprated by commas"}),
            "experience" : forms.TextInput(attrs={"placeholder" : "Years of Experience"}),
        }
        
    def clean_resume(self):
        resume = self.cleaned_data.get("resume")

        if resume:
            if resume.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("Resume size should not exceed 5MB.")
            if not resume.name.endswith(('.pdf', '.docx')):
                raise forms.ValidationError("Only PDF or DOCX files are allowed.")
        return resume
