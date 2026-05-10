from django.urls import path
from .views import services_page, book_event

urlpatterns = [
    path('', services_page, name='services'),
    path('book/', book_event, name='book_event'),
]

