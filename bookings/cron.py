from django_cron import CronJobBase, Schedule
from .models import Booking
from datetime import date


class CompleteBookingsCronJob(CronJobBase):
    RUN_EVERY_MINS = 1440

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'bookings.complete_bookings_cron_job'

    def do(self):
        bookings = Booking.objects.filter(status='confirmed', end_date__lt=date.today())
        for booking in bookings:
            booking.status = 'completed'
            booking.save()

