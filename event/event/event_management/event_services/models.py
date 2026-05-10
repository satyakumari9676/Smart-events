from django.db import models
from django.utils import timezone


class Service(models.Model):
    CATEGORY_CHOICES = [
        ("Personal", "Personal"),
        ("Corporate", "Corporate"),
        ("Large Scale", "Large Scale"),
    ]

    BADGE_TYPE_CHOICES = [
        ("primary", "Primary"),
        ("success", "Success"),
        ("warning", "Warning"),
        ("info", "Info"),
        ("secondary", "Secondary"),
        ("dark", "Dark"),
    ]

    BUTTON_LINK_CHOICES = [
        ("budget", "Budget Page"),
        ("contact", "Contact Page"),
    ]

    # Basic info
    title = models.CharField(max_length=120)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="Personal")
    description = models.TextField()

    # Card image (admin upload)
    image = models.ImageField(upload_to="services/", blank=True, null=True)

    # Badge (Popular / Business / Family / Premium ...)
    badge_text = models.CharField(max_length=30, blank=True, default="")
    badge_type = models.CharField(max_length=20, choices=BADGE_TYPE_CHOICES, default="secondary")

    # Tags line (store like: Decor, Catering, Music)
    tags = models.CharField(max_length=250, blank=True, default="")

    # Button at bottom of card
    button_text = models.CharField(max_length=80, default="View Details")
    button_link_type = models.CharField(max_length=20, choices=BUTTON_LINK_CHOICES, default="contact")

    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.title
class SubService(models.Model):
    parent = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="subservices")
    code = models.SlugField(max_length=40)
    name = models.CharField(max_length=120)
    cost_type = models.CharField(max_length=20, choices=[("fixed","Fixed"),("perGuest","Per Guest")], default="fixed")
    base_price = models.IntegerField(default=0)
    icon = models.CharField(max_length=10, blank=True, default="✨")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.parent.title} -> {self.name}"

class BudgetItem(models.Model):
    PRICING_TYPE = (
        ("fixed", "Fixed"),
        ("perGuest", "Per Guest"),
    )

    event = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="budget_items"
    )

    name = models.CharField(max_length=120)
    pricing_type = models.CharField(max_length=20, choices=PRICING_TYPE, default="fixed")
    base_price = models.IntegerField(default=0)
    icon = models.CharField(max_length=10, blank=True, default="✨")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.event.title} -> {self.name}"


from django.contrib.auth.models import User

class Booking(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("Unpaid", "Unpaid"),
        ("Advance Paid", "Advance Paid"),
        ("Fully Paid", "Fully Paid"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True)
    event_name = models.CharField(max_length=200, blank=True, null=True, help_text="Custom name if no service selected")
    event_date = models.DateField()
    guest_count = models.IntegerField(default=50)
    budget_estimate = models.IntegerField(default=0)
    advance_amount = models.IntegerField(default=0)
    total_amount_paid = models.IntegerField(default=0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default="Unpaid")
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.service.title if self.service else self.event_name} ({self.status})"


class WorkerAssignment(models.Model):
    PAYMENT_CHOICES = [
        ("Unpaid", "Unpaid"),
        ("Paid", "Paid"),
    ]
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='worker_assignments')
    worker = models.ForeignKey("careers.Worker", on_delete=models.CASCADE, related_name='assignments')
    role = models.CharField(max_length=100, help_text="e.g. Lead Decorator, Photographer")
    amount_due = models.IntegerField(default=0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default="Unpaid")
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.worker.name} assigned to {self.booking.id} as {self.role}"
