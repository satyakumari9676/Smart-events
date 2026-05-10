from django.urls import path
from . import views


urlpatterns = [
    path('', views.base_page, name='base'),
    path('login/', views.login_view, name='login'),
    path('worker-login/', views.worker_login_view, name='worker_login'),
    path('staff-login/', views.staff_login_view, name='staff_login'),
    path('register/', views.register_view, name='register'),
    path('home/', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('worker-dashboard/', views.worker_dashboard, name='worker_dashboard'),
    path('staff-dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/password/', views.change_password_view, name='change_password'),
    path('update-booking/<int:booking_id>/', views.update_booking_status, name='update_booking_status'),
    path('book-event/', views.book_event, name='book_event'),
    path('checkout/<int:booking_id>/', views.checkout, name='checkout'),
    path('process-payment/<int:booking_id>/', views.process_payment, name='process_payment'),
    path('api/create-budget-booking/', views.create_budget_booking, name='create_budget_booking'),
    
    path('worker-approve/<int:worker_id>/', views.approve_worker, name='approve_worker'),
    path('worker-reject/<int:worker_id>/', views.reject_worker, name='reject_worker'),
    path('assign-worker/', views.assign_worker, name='assign_worker'),
    path('pay-worker/<int:assignment_id>/', views.pay_worker, name='pay_worker'),
    
    path('add-service/', views.add_service, name='add_service'),

    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('career/', views.career, name='career'),
    path('wedding_budget/', views.wedding_budget, name='wedding_budget'),
    path('birthday_budget/', views.birthday_budget, name='birthday_budget'),
    path('engage_budget/', views.enagage_budget, name='engage_budget'),
    path('school_budget/', views.school_budget, name='school_budget'),
    path('shows_budget/', views.shows_budget, name='shows_budget'),
    path('baby_budget/', views.baby_budget, name='baby_budget'),
    path('corporate_budget/', views.corporate_budget, name='corporate_budget'),
    path('stalls_budget/', views.stalls_budget, name='stalls_budget'),
    path('party_budget/', views.party_budget, name='party_budget'),
    path('festival_budget/', views.festival_budget, name='festival_budget'),

    
    path('contact/', views.contact, name='contact'),
    path('feedback/', views.feedback_view, name='feedback'),
    path('logout/', views.logout_view, name='logout'),
    
    path("api/predict-budget/", views.predict_budget, name="predict_budget"),
]
