from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'listing', 'start_date', 'end_date', 'status', 'price')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('user__email', 'listing__title')

