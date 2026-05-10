from django.core.management.base import BaseCommand
from event_services.models import Service


class Command(BaseCommand):
    help = "Seed default event services"

    def handle(self, *args, **options):
        services_data = [
            {
                "title": "Wedding Events",
                "category": "Personal",
                "badge_text": "Popular",
                "badge_type": "primary",
                "description": "Venue, decor, catering, photography, invitations & full coordination.",
                "tags": "Decor, Catering, Photo/Video, Music",
                "button_text": "Estimate Wedding Budget",
                "button_link_type": "budget",
            },
            {
                "title": "Corporate Events",
                "category": "Corporate",
                "badge_text": "Business",
                "badge_type": "secondary",
                "description": "Conferences, product launches, seminars, team offsites & branding setups.",
                "tags": "Stage, AV, Branding, Logistics",
                "button_text": "Request Corporate Quote",
                "button_link_type": "contact",
            },
            {
                "title": "Birthday Parties",
                "category": "Personal",
                "badge_text": "Family",
                "badge_type": "success",
                "description": "Theme décor, cake & sweets, games, entertainers, photo booth & return gifts.",
                "tags": "Theme, Cake, Games, Entertainers",
                "button_text": "Estimate Birthday Budget",
                "button_link_type": "budget",
            },
            {
                "title": "Engagement & Reception",
                "category": "Personal",
                "badge_text": "Premium",
                "badge_type": "warning",
                "description": "Elegant stage décor, lights, flowers, catering, entry concepts & music.",
                "tags": "Stage, Lighting, Flowers, Catering",
                "button_text": "Book Consultation",
                "button_link_type": "contact",
            },
            {
                "title": "College/School Events",
                "category": "Large Scale",
                "badge_text": "Large",
                "badge_type": "info",
                "description": "Annual days, culturals, freshers, stage programs, sound & lighting.",
                "tags": "Stage, Sound, Lighting, Crowd Mgmt",
                "button_text": "Get School/College Quote",
                "button_link_type": "contact",
            },
            {
                "title": "Concerts & Shows",
                "category": "Large Scale",
                "badge_text": "Stage",
                "badge_type": "dark",
                "description": "Stage production, lighting rigs, sound systems, security & audience flow.",
                "tags": "Stage, AV, Security, Backstage",
                "button_text": "Talk to Production Team",
                "button_link_type": "contact",
            },
            {
                "title": "Baby Shower",
                "category": "Personal",
                "badge_text": "Theme",
                "badge_type": "secondary",
                "description": "Theme décor, photos, games, customized gifts, catering & stage setup.",
                "tags": "Theme, Props, Games, Catering",
                "button_text": "Estimate Baby Shower Budget",
                "button_link_type": "budget",
            },
            {
                "title": "Exhibitions & Stalls",
                "category": "Corporate",
                "badge_text": "Expo",
                "badge_type": "secondary",
                "description": "Stall design, vendor setup, banners, lighting, registrations & coordination.",
                "tags": "Stalls, Branding, Lighting, Registration",
                "button_text": "Get Exhibition Quote",
                "button_link_type": "contact",
            },
            {
                "title": "Private Parties",
                "category": "Personal",
                "badge_text": "Custom",
                "badge_type": "secondary",
                "description": "House parties, surprise events, anniversaries—tailored packages & themes.",
                "tags": "Decor, Food, Music, Photos",
                "button_text": "Create Custom Package",
                "button_link_type": "contact",
            },
        ]

        created_count = 0
        for data in services_data:
            obj, created = Service.objects.get_or_create(
                title=data["title"],
                defaults=data
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Seed completed. New services added: {created_count}"))
