from django.db import models
from django.conf import settings
from listings.models import Listing
from datetime import timedelta


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'In review'),
        ('confirmed', 'Confirmed'),
        ('declined', 'Rejected'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Booking {self.id} by {self.user} for {self.listing}'

    @staticmethod
    def get_unavailable_dates(listing):
        bookings = Booking.objects.filter(listing=listing, status='confirmed')
        dates = []
        for booking in bookings:
            current_date = booking.start_date
            while current_date <= booking.end_date:
                dates.append(current_date.strftime('%Y-%m-%d'))
                current_date += timedelta(days=1)
        return dates

    @property
    def total_price(self):
        days = (self.end_date - self.start_date).days
        return days * self.listing.price


class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    stripe_payment_intent_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for {self.booking} - {self.amount} - {self.status}"