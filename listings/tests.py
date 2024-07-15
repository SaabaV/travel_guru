from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from listings.models import Listing
from reviews.models import Review
from listings.forms import ListingForm

User = get_user_model()

class ListingModelTests(TestCase):

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

    def test_listing_creation(self):
        self.assertEqual(self.listing.title, 'Test Listing')
        self.assertEqual(self.listing.owner, self.user)
        self.assertEqual(self.listing.price, 100.00)

    def test_update_reviews_count(self):
        review = Review.objects.create(
            listing=self.listing,
            user=self.user,
            rating=5,
            comment='Great place!',
            approved=True
        )
        self.listing.update_reviews_count()
        self.assertEqual(self.listing.reviews_count, 1)

    def test_update_avg_rating(self):
        review = Review.objects.create(
            listing=self.listing,
            user=self.user,
            rating=5,
            comment='Great place!',
            approved=True
        )
        self.listing.update_avg_rating()
        self.assertEqual(self.listing.average_rating, 5.0)  # Изменено на average_rating

class ListingFormTests(TestCase):

    def test_listing_form_valid(self):
        form_data = {
            'title': 'Test Listing',
            'description': 'Test Description',
            'location': 'Test Location',
            'price': 100.00,
            'rooms': 2,
            'property_type': 'Apartments',
        }
        form = ListingForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_listing_form_invalid(self):
        form_data = {
            'title': '',
            'description': 'Test Description',
            'location': 'Test Location',
            'price': 100.00,
            'rooms': 2,
            'property_type': 'Apartments',
        }
        form = ListingForm(data=form_data)
        self.assertFalse(form.is_valid())

class ListingViewTests(TestCase):

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

    def test_listing_detail_view(self):
        response = self.client.get(reverse('listing_detail', args=[self.listing.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.listing.title)

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Listing')  # Убедитесь, что заголовок листинга присутствует на домашней странице

    def test_create_listing_view_authenticated(self):
        self.client.login(email='testuser@example.com', password='12345')
        response = self.client.post(reverse('create_listing'), {
            'title': 'New Listing',
            'description': 'New Description',
            'location': 'New Location',
            'price': 150.00,
            'rooms': 3,
            'property_type': 'Villas'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation

    def test_create_listing_view_unauthenticated(self):
        response = self.client.get(reverse('create_listing'))
        self.assertRedirects(response, '/users/login/?next=/listings/new/')  # Обновлено для корректного URL-адреса









