from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from event_services.models import Service, SubService, Booking
from .models import Feedback
import os, json
import joblib
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# ----------------------------
# STATIC EVENT DATA (for Services)
# Put the images in: static/img/
# Example usage in template: {% static e.image %}
# ----------------------------
EVENTS = [
    {
        "title": "Wedding Events",
        "category": "Personal",
        "image": "img/event-wedding.jpg",
        "desc": "Venue, décor, catering, photography, invitations & full coordination."
    },
    {
        "title": "Engagement & Reception",
        "category": "Personal",
        "image": "img/event-engagement.jpg",
        "desc": "Stage décor, flowers, lighting, catering, entry concepts & music."
    },
    {
        "title": "Birthday Parties",
        "category": "Personal",
        "image": "img/event-birthday.jpg",
        "desc": "Theme décor, cake, games, entertainers, photo booth & return gifts."
    },
    {
        "title": "Baby Shower",
        "category": "Personal",
        "image": "img/event-babyshower.jpg",
        "desc": "Theme décor, props, games, customized gifts, catering & coordination."
    },
    {
        "title": "Corporate Events",
        "category": "Corporate",
        "image": "img/event-corporate.jpg",
        "desc": "Conferences, product launches, seminars, offsites & branding setups."
    },
    {
        "title": "Exhibitions & Stalls",
        "category": "Corporate",
        "image": "img/event-exhibition.jpg",
        "desc": "Stall design, vendor setup, banners, lighting, registrations & coordination."
    },
    {
        "title": "College/School Events",
        "category": "Large Scale",
        "image": "img/event-college.jpg",
        "desc": "Annual days, culturals, stage programs, sound, lighting & crowd management."
    },
    {
        "title": "Concerts & Shows",
        "category": "Large Scale",
        "image": "img/event-concert.jpg",
        "desc": "Stage production, lighting rigs, sound systems, security & audience flow."
    },
    {
        "title": "Private Parties",
        "category": "Personal",
        "image": "img/event-private.jpg",
        "desc": "House parties, surprise events, anniversaries—tailored packages & themes."
    },
]


# ✅ BASE PAGE (Landing Page)
def base_page(request):
    return render(request, "base.html")


# ✅ LOGIN PAGE (for Users/Clients, supports ?next=/somepage/)
def login_view(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in. Please log out first to switch accounts.")
        if request.user.is_staff:
            return redirect("staff_dashboard")
        elif hasattr(request.user, 'worker_profile'):
            return redirect("worker_dashboard")
        else:
            return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_staff:
                messages.error(request, "Please use the dedicated Staff Portal to log in.")
                return redirect("staff_login")
            
            if hasattr(user, 'worker_profile'):
                messages.error(request, "Please use the dedicated Worker Portal to log in.")
                return redirect("worker_login")
                
            login(request, user)
            request.session['portal'] = 'client'
            
            next_url = request.POST.get("next") or request.GET.get("next")
            if next_url:
                return redirect(next_url)
                
            return redirect("dashboard")  # Normal users go to Dashboard
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html")

# ✅ WORKER LOGIN PAGE
def worker_login_view(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in. Please log out first to switch accounts.")
        if request.user.is_staff:
            return redirect("staff_dashboard")
        elif hasattr(request.user, 'worker_profile'):
            return redirect("worker_dashboard")
        else:
            return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if hasattr(user, 'worker_profile') and user.worker_profile.is_approved:
                login(request, user)
                request.session['portal'] = 'worker'
                return redirect("worker_dashboard")
            else:
                messages.error(request, "Access Denied. Only Approved Workers can log in here. Use the username & password provided by the Admin.")
                return redirect("worker_login")
        else:
            messages.error(request, "Invalid Worker credentials. Please use the credentials provided by the Admin.")

    return render(request, "worker_login.html")

# ✅ STAFF LOGIN PAGE
def staff_login_view(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in. Please log out first to switch accounts.")
        if request.user.is_staff:
            return redirect("staff_dashboard")
        elif hasattr(request.user, 'worker_profile'):
            return redirect("worker_dashboard")
        else:
            return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_staff:
                login(request, user)
                request.session['portal'] = 'staff'
                
                next_url = request.POST.get("next") or request.GET.get("next")
                if next_url:
                    return redirect(next_url)
                    
                return redirect("staff_dashboard")
            else:
                messages.error(request, "This portal is strictly for authorized administrative personnel.")
        else:
            messages.error(request, "Invalid staff credentials")

    return render(request, "staff_login.html")

# ✅ REGISTER PAGE
def register_view(request):
    # ✅ Clear any old messages when user first opens register page
    if request.method == "GET":
        storage = messages.get_messages(request)
        for _ in storage:
            pass
        return render(request, "register.html")

    # POST
    username = request.POST.get("username", "").strip()
    email = request.POST.get("email", "").strip()
    password = request.POST.get("password", "")
    confirm_password = request.POST.get("password2", "")

    if password != confirm_password:
        messages.error(request, "Passwords do not match!")
        return render(request, "register.html")

    try:
        validate_password(password)
    except ValidationError as e:
        for error in e.messages:
            messages.error(request, error)
        return render(request, "register.html")

    if User.objects.filter(username=username).exists():
        messages.error(request, "Username already exists!")
        return render(request, "register.html")

    if User.objects.filter(email=email).exists():
        messages.error(request, "Email already registered!")
        return render(request, "register.html")

    staff_token = request.POST.get("staff_token", "").strip()

    user = User.objects.create_user(username=username, email=email, password=password)
    
    # ✅ Secret feature to allow Admins to sign up via UI
    if staff_token == "EVENTADMIN2026":
        user.is_staff = True
        user.is_superuser = True
        user.save()
        messages.success(request, "Registration successful! You are now an Admin.")
    else:
        messages.success(request, "Registration successful! Please login.")
        
    return redirect("login")



# ✅ HOME PAGE (LOGIN REQUIRED)
def home(request):
    feedbacks = Feedback.objects.all().order_by('-created_at')[:6]
    return render(request, "home.html", {"feedbacks": feedbacks})

# ✅ DASHBOARD PAGE (EVENT HISTORY)
@login_required(login_url="login")
def dashboard(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-event_date')
    first_unpaid = bookings.filter(payment_status='Unpaid').first()
    return render(request, "dashboard.html", {"bookings": bookings, "first_unpaid": first_unpaid})

# ✅ STAFF DASHBOARD PAGE
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_staff)
def staff_dashboard(request):
    from careers.models import Worker
    
    all_bookings = Booking.objects.all().order_by('-created_at')
    active_bookings = all_bookings.filter(status__in=["Pending", "Confirmed"])
    history_bookings = all_bookings.filter(status__in=["Completed", "Cancelled"])
    
    # Worker Separation
    approved_workers = Worker.objects.filter(is_approved=True).order_by('-id')
    worker_applications = Worker.objects.filter(is_approved=False).order_by('-id')
    
    # Calculate Admin Metrics
    total_bookings = all_bookings.count()
    pending_bookings = all_bookings.filter(status="Pending").count()
    completed_bookings = all_bookings.filter(status="Completed").count()
    
    from django.db.models import Sum
    # Sum of budget estimates for confirmed/completed bookings
    revenue_agg = all_bookings.filter(status__in=["Confirmed", "Completed"]).aggregate(Sum('budget_estimate'))
    total_revenue = revenue_agg['budget_estimate__sum'] or 0
    
    from django.contrib.auth.models import User
    from event_services.models import Service, WorkerAssignment
    from .models import ContactMessage
    
    all_users = User.objects.all().order_by('-date_joined')
    all_services = Service.objects.all().order_by('-id')
    all_messages = ContactMessage.objects.all().order_by('-created_at')
    all_assignments = WorkerAssignment.objects.all().select_related('booking', 'worker').order_by('-assigned_at')
    
    context = {
        "active_bookings": active_bookings,
        "history_bookings": history_bookings,
        "approved_workers": approved_workers,
        "worker_applications": worker_applications,
        "total_bookings": total_bookings,
        "pending_bookings": pending_bookings,
        "completed_bookings": completed_bookings,
        "total_revenue": total_revenue,
        "all_users": all_users,
        "all_services": all_services,
        "contact_messages": all_messages,
        "all_assignments": all_assignments,
    }
    
    return render(request, "staff_dashboard.html", context)


# ✅ ASSIGN WORKER (STAFF ONLY)
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_staff)
def assign_worker(request):
    if request.method == "POST":
        from event_services.models import Booking, WorkerAssignment
        from careers.models import Worker
        
        booking_id = request.POST.get("booking_id")
        worker_id = request.POST.get("worker_id")
        role = request.POST.get("role", "").strip()
        amount_due = request.POST.get("amount_due", 0)
        
        if booking_id and worker_id and role:
            try:
                booking = Booking.objects.get(id=booking_id)
                worker = Worker.objects.get(id=worker_id)
                WorkerAssignment.objects.create(
                    booking=booking,
                    worker=worker,
                    role=role,
                    amount_due=int(amount_due)
                )
                messages.success(request, f"Worker {worker.name} successfully assigned to booking #{booking.id}.")
            except Exception as e:
                messages.error(request, f"Error: {e}")
        else:
            messages.error(request, "All fields are required to assign a worker.")
            
    return redirect("staff_dashboard")

# ✅ PAY WORKER (STAFF ONLY)
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_staff)
def pay_worker(request, assignment_id):
    if request.method == "POST":
        from event_services.models import WorkerAssignment
        from django.contrib import messages
        
        try:
            assignment = WorkerAssignment.objects.get(id=assignment_id)
            if assignment.payment_status == "Unpaid":
                assignment.payment_status = "Paid"
                assignment.save()
                messages.success(request, f"Payment of ₹{assignment.amount_due} successful to {assignment.worker.name}.")
            else:
                messages.info(request, "Worker is already paid.")
        except Exception as e:
            messages.error(request, f"Error processing payment: {str(e)}")
            
    return redirect("staff_dashboard")

# ✅ WORKER DASHBOARD PAGE
@login_required(login_url="login")
def worker_dashboard(request):
    if not hasattr(request.user, 'worker_profile') or not request.user.worker_profile.is_approved:
        messages.error(request, "You do not have access to the Worker Dashboard.")
        return redirect("dashboard")

    from event_services.models import WorkerAssignment
    from django.db.models import Sum

    worker = request.user.worker_profile
    assignments = WorkerAssignment.objects.filter(worker=worker).select_related('booking').order_by('-assigned_at')
    
    total_gigs = assignments.count()
    completed_gigs = assignments.filter(booking__status="Completed").count()
    
    pending_earnings_agg = assignments.filter(payment_status="Unpaid").aggregate(Sum('amount_due'))
    pending_earnings = pending_earnings_agg['amount_due__sum'] or 0
    
    total_earnings_agg = assignments.filter(payment_status="Paid").aggregate(Sum('amount_due'))
    total_earnings = total_earnings_agg['amount_due__sum'] or 0

    context = {
        "worker": worker,
        "assignments": assignments,
        "total_gigs": total_gigs,
        "completed_gigs": completed_gigs,
        "pending_earnings": pending_earnings,
        "total_earnings": total_earnings,
    }
    
    return render(request, "worker_dashboard.html", context)

# ✅ WORKER APPROVAL LOGIC (STAFF ONLY)
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_staff)
def approve_worker(request, worker_id):
    from careers.models import Worker
    worker = get_object_or_404(Worker, id=worker_id)
    worker.is_approved = True
    
    if not worker.user:
        # Generate user automatically
        base_username = worker.email.split('@')[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        new_user = User.objects.create_user(username=username, email=worker.email, password="password123")
        worker.user = new_user
        worker.save()
        messages.success(request, f"Worker {worker.name} APPROVED! Account generated - Username: {username} | Password: password123")
    else:
        worker.save()
        messages.success(request, f"Worker application for {worker.name} has been APPROVED.")
        
    return redirect("staff_dashboard")

@login_required(login_url="login")
@user_passes_test(lambda u: u.is_staff)
def reject_worker(request, worker_id):
    from careers.models import Worker
    if request.method == "POST":
        worker = get_object_or_404(Worker, id=worker_id)
        worker.delete() # Or set a rejected flag, but deleting cleans up the queue
        messages.success(request, f"Worker application for {worker.name} has been REJECTED and removed.")
    return redirect("staff_dashboard")

# ✅ UPDATE BOOKING STATUS (STAFF ONLY)
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_staff)
def update_booking_status(request, booking_id):
    if request.method == "POST":
        booking = get_object_or_404(Booking, id=booking_id)
        new_status = request.POST.get("status")
        if new_status in dict(Booking.STATUS_CHOICES):
            booking.status = new_status
            booking.save()
            messages.success(request, f"Booking #{booking.id} status updated to {new_status}.")
    return redirect("staff_dashboard")

# ✅ BOOK EVENT PAGE (LOGIN REQUIRED)
@login_required(login_url="login")
def book_event(request):
    if request.method == "POST":
        event_name = request.POST.get("event_name", "").strip()
        event_date = request.POST.get("event_date", "")
        guest_count = request.POST.get("guest_count", 50)
        budget_estimate = request.POST.get("budget_estimate", 0)

        if event_name and event_date:
            booking = Booking.objects.create(
                user=request.user,
                event_name=event_name,
                event_date=event_date,
                guest_count=int(guest_count) if guest_count else 50,
                budget_estimate=int(budget_estimate) if budget_estimate else 0,
                status="Pending",
                payment_status="Unpaid"
            )
            # Calculate advance (20%)
            booking.advance_amount = int(booking.budget_estimate * 0.20)
            booking.save()
            
            messages.info(request, "Almost there! Please complete the advance payment to finalize your booking.")
            return redirect("checkout", booking_id=booking.id)
        else:
            messages.error(request, "Event name and date are required.")
    
    return render(request, "book_event.html")


@login_required(login_url="login")
def checkout(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.payment_status != "Unpaid":
        messages.info(request, "Payment for this booking has already been processed.")
        return redirect("dashboard")
        
    return render(request, "checkout.html", {"booking": booking})

@login_required(login_url="login")
def process_payment(request, booking_id):
    if request.method == "POST":
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        
        # In a real app, you'd process the payment here.
        # Since this is dummy, we just update the status.
        import uuid
        payment_option = request.POST.get("payment_amount_split", "total")
        
        if payment_option == "total":
            booking.payment_status = "Fully Paid"
            booking.total_amount_paid = booking.budget_estimate
            msg_amount = booking.budget_estimate
            msg_type = "Total"
        elif payment_option == "remaining":
            booking.payment_status = "Fully Paid"
            booking.total_amount_paid = booking.budget_estimate
            msg_amount = booking.budget_estimate - booking.advance_amount
            msg_type = "Remaining"
        else: # advance
            booking.payment_status = "Advance Paid"
            booking.total_amount_paid = booking.advance_amount
            msg_amount = booking.advance_amount
            msg_type = "Advance"
            
        booking.transaction_id = f"DUMMY-{uuid.uuid4().hex[:8].upper()}"
        booking.save()
        
        messages.success(request, f"{msg_type} payment of ₹{msg_amount} successful! Your booking is now being processed.")
        return redirect("dashboard")
        
    return redirect("checkout", booking_id=booking_id)


# ✅ SERVICES PAGE (LOGIN REQUIRED) + Search + Category Filter
@login_required(login_url="login")
def services(request):
    q = request.GET.get("q", "").strip()
    cat = request.GET.get("cat", "All").strip()

    results = EVENTS

    # Filter by category
    if cat and cat != "All":
        results = [e for e in results if e["category"].lower() == cat.lower()]

    # Search filter
    if q:
        q_lower = q.lower()
        results = [
            e for e in results
            if q_lower in e["title"].lower() or q_lower in e["desc"].lower()
        ]

    context = {"events": results, "q": q, "cat": cat}
    return render(request, "services.html", context)


# ✅ ADD SERVICE (STAFF ONLY)
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_staff)
def add_service(request):
    if request.method == "POST":
        from event_services.models import Service
        title = request.POST.get("title", "").strip()
        category = request.POST.get("category", "Personal")
        description = request.POST.get("description", "").strip()
        status = request.POST.get("status", "on")

        if title and description:
            is_active = True if status == "on" else False
            Service.objects.create(
                title=title,
                category=category,
                description=description,
                is_active=is_active
            )
            messages.success(request, f"Service '{title}' has been successfully added!")
        else:
            messages.error(request, "Title and description are required to add a service.")
            
    return redirect("staff_dashboard")

# ✅ ABOUT PAGE
def about(request):
    return render(request, "about.html")



# ✅ CAREER PAGE
def career(request):
    if request.method == "POST":
        from careers.models import Worker
        name = request.POST.get("fullName", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        event_category = request.POST.get("eventCategory", "").strip()
        role = request.POST.get("role", "").strip()
        experience = request.POST.get("experience", "").strip()
        city = request.POST.get("city", "").strip()
        message = request.POST.get("message", "").strip()
        resume = request.FILES.get("resume")
        
        skills_combined = f"Role: {role} ({event_category}) | Exp: {experience} | Loc: {city} | Msg: {message}"
        
        Worker.objects.create(
            user=None,
            name=name,
            email=email,
            phone=phone,
            skills=skills_combined,
            resume=resume,
            is_approved=False
        )
        messages.success(request, "Your application has been submitted successfully! We will contact you soon.")
        return redirect("career")

    return render(request, "career.html")


# ✅ BUDGET ESTIMATOR PAGE
@login_required(login_url="login")
def wedding_budget(request):
    return render(request, "wedding_budget.html")


def birthday_budget(request):
    return render(request, "birthday_budget.html")

def enagage_budget(request):
    return render(request, "engage_budget.html")

def school_budget(request):
    return render(request, "school_budget.html")

def shows_budget(request):
    return render(request, "shows_budget.html")

def baby_budget(request):
    return render(request, "baby_budget.html")

def corporate_budget(request):
    return render(request, "corporate_budget.html")

def stalls_budget(request):
    return render(request, "stalls_budget.html")
def party_budget(request):
    return render(request, "party_budget.html")
def festival_budget(request):
    return render(request, "festival_budget.html")
# ✅ CONTACT PAGE
def contact(request):
    if request.method == "POST":
        from .models import ContactMessage
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()
        
        if name and email and subject and message:
            ContactMessage.objects.create(
                name=name, email=email, phone=phone,
                subject=subject, message=message
            )
            messages.success(request, "Your message has been sent successfully!")
            return redirect("contact")
        else:
            messages.error(request, "Please fill out all required fields.")
            
    return render(request, "contact.html")


# ✅ LOGOUT
def logout_view(request):
    logout(request)
    return redirect("home")

# ✅ PROFILE VIEW
@login_required(login_url="login")
def profile_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        profile_image = request.FILES.get("profile_image")

        if username:
            if User.objects.filter(username=username).exclude(id=request.user.id).exists():
                messages.error(request, "Username is already taken.")
            else:
                request.user.username = username
                request.user.save()
                
                if profile_image:
                    request.user.profile.profile_image = profile_image
                    request.user.profile.save()

                messages.success(request, "Profile updated successfully!")
                return redirect("profile")
        else:
            messages.error(request, "Username cannot be empty.")

    return render(request, "profile.html")

# ✅ CHANGE PASSWORD VIEW
@login_required(login_url="login")
def change_password_view(request):
    if request.method == "POST":
        from django.contrib.auth import update_session_auth_hash
        current_password = request.POST.get("current_password", "")
        new_password = request.POST.get("new_password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not request.user.check_password(current_password):
            messages.error(request, "Incorrect current password.")
        elif new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
        else:
            try:
                validate_password(new_password, user=request.user)
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, "Password changed successfully!")
            except ValidationError as e:
                for error in e.messages:
                    messages.error(request, error)
            return redirect("profile")

    return redirect("profile")


# ✅ FEEDBACK PAGE
def feedback_view(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        rating = request.POST.get("rating", "5")
        message = request.POST.get("message", "").strip()

        if name and message:
            Feedback.objects.create(
                name=name,
                email=email,
                rating=int(rating),
                message=message
            )
            messages.success(request, "Thank you for your feedback!")
            return redirect("feedback")
        else:
            messages.error(request, "Name and message are required.")
    
    return render(request, "feedback.html")


PKG_MAP = {"simple": 1, "basic": 2, "luxury": 3}
LOC_MAP = {"rural": 1, "tier2": 2, "metro": 3, "premium": 4}

MODEL_CACHE = {}

def load_model(event_key):
    if event_key in MODEL_CACHE:
        return MODEL_CACHE[event_key]
    from django.conf import settings
    path = os.path.join(settings.BASE_DIR, "models", f"{event_key}_budget_model.pkl")

    if not os.path.exists(path):
        return None
    MODEL_CACHE[event_key] = joblib.load(path)
    return MODEL_CACHE[event_key]

@csrf_exempt
def predict_budget(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    data = json.loads(request.body.decode("utf-8"))

    event_key = data.get("event_key")  # wedding / birthday_private_party / corporate_event ...
    EVENT_KEY_MAP = {
        "wedding": "wedding",
        "wedding": "wedding",
        "engagement": "engage",
    }

    event_key = EVENT_KEY_MAP.get(event_key, event_key)
    guests = int(data.get("guests", 0))
    pkg = data.get("package", "simple")
    loc = data.get("location", "tier2")
    services_count = int(data.get("services_count", 0))

    model = load_model(event_key)
    if model is None:
        return JsonResponse({"error": f"Model not found for {event_key}"}, status=404)

    X = [[guests, PKG_MAP.get(pkg, 1), LOC_MAP.get(loc, 2), services_count]]
    pred = model.predict(X)[0]
    return JsonResponse({"predicted_total": int(round(pred))})

@csrf_exempt
def create_budget_booking(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            event_name = data.get('event_name', 'Custom Event').strip()
            event_date = data.get('event_date')
            guest_count = int(data.get('guest_count', 50))
            budget_estimate = int(data.get('budget_estimate', 0))
            
            if not event_date:
                return JsonResponse({'success': False, 'error': 'Event date is required'})

            # Create confirmed booking directly
            booking = Booking.objects.create(
                user=request.user if request.user.is_authenticated else User.objects.first(),
                event_name=event_name,
                event_date=event_date,
                guest_count=guest_count,
                budget_estimate=budget_estimate,
                advance_amount=int(budget_estimate * 0.20),
                total_amount_paid=0,
                status='Pending',
                payment_status='Unpaid'
            )
            return JsonResponse({'success': True, 'booking_id': booking.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
