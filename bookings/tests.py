from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from listings.models import Listing
from bookings.models import Booking
from datetime import date, timedelta

User = get_user_model()


class BookingTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(email='testuser@example.com', password='testpass123', name='Test User')
        self.owner = User.objects.create_user(email='owner@example.com', password='testpass123', name='Owner User')
        self.listing = Listing.objects.create(
            title='Test Listing',
            description='A nice place to stay.',
            location='Test City',
            price=100.00,
            rooms=2,
            property_type='Apartments',
            owner=self.owner,
        )
        self.booking = Booking.objects.create(
            user=self.user,
            listing=self.listing,
            start_date=date.today(),
            end_date=date.today(),
            price=100.00,
            status='pending',
        )
        self.client.login(email='testuser@example.com', password='testpass123')

    def test_create_booking_view(self):
        response = self.client.get(reverse('create_booking', args=[self.listing.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/create_booking.html')

        data = {
            'start_date': date.today() + timedelta(days=1),
            'end_date': date.today() + timedelta(days=2),
        }
        response = self.client.post(reverse('create_booking', args=[self.listing.id]), data)

        if response.status_code != 302:
            print(response.context['form'].errors)  # Вывод ошибок формы для отладки

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Booking.objects.count(), 2)

    def test_my_bookings_view(self):
        response = self.client.get(reverse('my_bookings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/my_bookings.html')
        self.assertContains(response, self.listing.title)

    def test_cancel_booking_view(self):
        response = self.client.get(reverse('cancel_booking', args=[self.booking.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/cancel_booking.html')

        response = self.client.post(reverse('cancel_booking', args=[self.booking.id]))
        self.assertEqual(response.status_code, 302)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'cancelled')

    def test_manage_bookings_view(self):
        self.client.login(email='owner@example.com', password='testpass123')
        response = self.client.get(reverse('manage_bookings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/manage_bookings.html')
        self.assertContains(response, self.listing.title)

    def test_update_booking_status_view(self):
        self.client.login(email='owner@example.com', password='testpass123')
        response = self.client.get(reverse('update_booking_status', args=[self.booking.id, 'confirmed']))
        self.assertEqual(response.status_code, 302)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'confirmed')



