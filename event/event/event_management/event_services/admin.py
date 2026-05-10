from django.contrib import admin
from .models import Service, SubService, Booking


class SubServiceInline(admin.TabularInline):
    model = SubService
    extra = 2
    fields = ("code", "name", "cost_type", "base_price", "icon", "is_active")
    show_change_link = True


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("title",)
    inlines = [SubServiceInline]


@admin.register(SubService)
class SubServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "cost_type", "base_price", "is_active")
    list_filter = ("parent", "is_active")
    search_fields = ("name", "parent__title")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("user", "service", "event_name", "event_date", "status")
    list_filter = ("status", "event_date")
    search_fields = ("user__username", "event_name", "service__title")

