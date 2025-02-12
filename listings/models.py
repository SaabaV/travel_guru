from django.db import models
from django.conf import settings
from django.db.models import Avg
from datetime import timedelta


class Listing(models.Model):
    PROPERTY_TYPE_CHOICES = [
        ('Apartments', 'Apartments'),
        ('Vacation apartments', 'Vacation apartments'),
        ('Vacation homes', 'Vacation homes'),
        ('Hotels', 'Hotels'),
        ('Villas', 'Villas'),
        ('Motels', 'Motels'),
        ('Hostels', 'Hostels'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rooms = models.IntegerField()
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    average_rating = models.FloatField(default=0, blank=True)
    reviews_count = models.IntegerField(default=0)
    blocked_dates = models.JSONField(default=list, blank=True)

    def block_dates(self, start_date, end_date):
        new_blocked_dates = set(self.blocked_dates)
        current_date = start_date
        while current_date <= end_date:
            new_blocked_dates.add(current_date.isoformat())
            current_date += timedelta(days=1)
        self.blocked_dates = list(new_blocked_dates)
        self.save()

    def update_avg_rating(self):
        reviews = self.reviews.filter(approved=True)
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        self.average_rating = avg_rating
        self.save()

    def update_reviews_count(self):
        self.reviews_count = self.reviews.count()
        self.save()

    def __str__(self):
        return self.title


class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='listings_photos/')

    def __str__(self):
        return f"Image for {self.listing.title}"
