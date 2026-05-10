from django.urls import path
from .views import estimate
from . import views

urlpatterns = [
    path('estimate/', estimate, name='estimate'),
    path('api/predict-budget/', views.predict_budget, name='predict_budget_api'),
]
