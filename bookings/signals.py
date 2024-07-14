from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.apps import AppConfig
from .models import Booking


class BookingsConfig(AppConfig):
    name = 'bookings'

    def ready(self):
        from .cron import CompleteBookingsCronJob


@receiver(post_save, sender=Booking)
def send_booking_notification(sender, instance, created, **kwargs):
    if created:
        send_mail(
            'New Booking Request',
            f'You have a new booking request for {instance.listing.title}.',
            'travel@guru.com',
            [instance.listing.owner.email],
            fail_silently=False,
        )
    elif instance.status == 'confirmed':
        send_mail(
            'Booking Confirmed',
            f'Your booking for {instance.listing.title} has been confirmed.',
            'travel@guru.com',
            [instance.user.email],
            fail_silently=False,
        )
    elif instance.status == 'declined':
        send_mail(
            'Booking Declined',
            f'Your booking for {instance.listing.title} has been declined.',
            'travel@guru.com',
            [instance.user.email],
            fail_silently=False,
        )
