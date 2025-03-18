from django.db import models

# Create your models here.

class Contact(models.Model):
    name = models.CharField(
        max_length = 100,
        verbose_name = "Full Name"
    )

    email = models.EmailField(
        verbose_name = "Email Address",
    )

    message = models.TextField(
        verbose_name = "Your Message"
     )

    created_at = models.DateTimeField(
        auto_now_add= True,
        verbose_name = "Submitted On"
    )

    class Meta:
        verbose_name = "Contact Inquiry"
        verbose_name_plural = "Contact Inquiries"

    def __str__(self):
        return self.name