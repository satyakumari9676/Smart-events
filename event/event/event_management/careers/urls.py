from django.urls import path
from .views import career_page

urlpatterns = [
    path('', career_page, name='career'),
]
