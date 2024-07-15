from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from bookings.models import Booking
from listings.models import Listing
from Travel_guru import settings

User = get_user_model()


class BookingModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(email='testuser@example.com', password='12345')
        self.listing = Listing.objects.create(
            title='Test Listing',
            description='Test Description',
            location='Test Location',
            price=100.00,
            rooms=2,
            property_type='Apartments',
            owner=self.user
        )
        self.booking = Booking.objects.create(
            user=self.user,
            listing=self.listing,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=1),
            status='confirmed',
            price=100.00
        )

    def test_booking_creation(self):
        self.assertEqual(self.booking.user, self.user)
        self.assertEqual(self.booking.listing, self.listing)
        self.assertEqual(self.booking.status, 'confirmed')

    def test_booking_total_price(self):
        self.assertEqual(self.booking.total_price, 100.00)

    def test_unavailable_dates(self):
        unavailable_dates = Booking.get_unavailable_dates(self.listing)
        expected_dates = [date.today().strftime('%Y-%m-%d'), (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')]
        self.assertEqual(unavailable_dates, expected_dates)

class BookingViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='testuser@example.com', password='12345')
        self.listing = Listing.objects.create(
            title='Test Listing',
            description='Test Description',
            location='Test Location',
            price=100.00,
            rooms=2,
            property_type='Apartments',
            owner=self.user
        )

    def test_create_booking_unauthenticated(self):
        response = self.client.get(reverse('create_booking', args=[self.listing.id]))
        login_url = reverse(settings.LOGIN_URL)  # Использование пути из настроек
        self.assertRedirects(response, f'{login_url}?next=/bookings/create/{self.listing.id}/')

    def test_create_booking_authenticated(self):
        self.client.login(email='testuser@example.com', password='12345')
        response = self.client.post(reverse('create_booking', args=[self.listing.id]), {
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=1)
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('my_bookings'))

    def test_manage_bookings_view(self):
        self.client.login(email='testuser@example.com', password='12345')
        response = self.client.get(reverse('manage_bookings'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Manage Bookings')

    def test_cancel_booking(self):
        booking = Booking.objects.create(
            user=self.user,
            listing=self.listing,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=1),
            status='confirmed',
            price=100.00
        )
        self.client.login(email='testuser@example.com', password='12345')
        response = self.client.post(reverse('cancel_booking', args=[booking.id]))
        self.assertRedirects(response, reverse('my_bookings'))
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'cancelled')








