from django import  forms
from users.models import CompanyProfile, UserProfile
from jobs.models import Job, JobApplication

class CompanyForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        exclude = ['id', 'user_profile']  # Exclude user_profile since it's set in the view

        # Customizing labels
        labels = {
            "name": "Company Name",
            "industry": "Industry Type",
            "location": "Company Location",
            "contact_email": "Contact Email",
        }

        # Customizing widgets
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Company Name", "class": "form-input"}),
            "industry": forms.TextInput(attrs={"placeholder": "Industry Type", "class": "form-input"}),
            "location": forms.TextInput(attrs={"placeholder": "Company Location", "class": "form-input"}),
            "website": forms.URLInput(attrs={"placeholder": "Company Website", "class": "form-input"}),
            "contact_email": forms.EmailInput(attrs={"placeholder": "Contact Email", "class": "form-input"}),
            "description": forms.Textarea(attrs={"placeholder": "Company Description", "class": "textarea"}),
            
        }

class JobForm(forms.ModelForm):
    required_skills = forms.CharField(
        widget=forms.Textarea(attrs={
            "placeholder": "Enter skills separated by commas",
            "class": "text-area",
            "rows": 3
        })
    )

    class Meta:
        model = Job
        fields = [
            "title",
            "description",
            "location",
            "required_skills",  
            "job_type",
            "salary_min",
            "salary_max",
            "is_active",
        ]

        widgets = {
            "title": forms.TextInput(attrs= {"placeholder": "Job Title", "class": "form-input"}),
            "description" : forms.TextInput(attrs= {"placeholder" : "Job Description", "class": "form-input"}),
            "location" : forms.TextInput(attrs= {"placeholder" : "Job Location", "class" : "form-input"}),
            "salary_min" : forms.NumberInput(attrs= {"placeholder" : "Minimum salary", "class" : "form-input"}),
            "salary_max" : forms.NumberInput(attrs = {"placeholder" : "Maximum salary", "class" : "form-input"}),
            "job_type" : forms.Select(attrs= {"class" : "form-select"}),
        }

    def clean_required_skills(self):
        """Convert the skills string to a list for JSONField storage"""
        skills = self.cleaned_data.get("required_skills", "")
        skills_list = [skill.strip() for skill in skills.split(",") if skill.strip()]

        if not skills_list:
            raise forms.ValidationError("Please enter at least one skill.")

        return skills_list  # Must return a list because the model expects JSON

    def __init__(self, *args, **kwargs):
        """Convert list from JSONField to a comma-separated string for display"""
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["required_skills"].initial = ", ".join(self.instance.required_skills or [])



