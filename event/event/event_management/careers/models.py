from django.db import models
from django.contrib.auth.models import User

class Worker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='worker_profile')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    skills = models.TextField()
    is_approved = models.BooleanField(default=False)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
# Create your models here.
