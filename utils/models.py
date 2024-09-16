from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.  

class Contactus(models.Model):
    """
    Model to store newsletter subscriptions.
    """
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255)
    message = models.TextField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

