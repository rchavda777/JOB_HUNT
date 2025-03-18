from django import forms
from home.models import Contact

class ContactForm(forms.ModelForm):
    
    class Meta:
        model = Contact
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': "Full Name",
            }),
            'email': forms.EmailInput(attrs={ 
                'placeholder': "Email Address",
            }),
            'message': forms.Textarea(attrs={
                'placeholder': "Message",
                'rows': 4  # Set textarea height
            })
        }
