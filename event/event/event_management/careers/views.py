from django.shortcuts import render
from .models import Worker

def career_page(request):
    if request.method == "POST":
        Worker.objects.create(
            name=request.POST['name'],
            email=request.POST['email'],
            phone=request.POST['phone'],
            skills=request.POST['skills']
        )
    return render(request, 'careers/career.html')

# Create your views here.
