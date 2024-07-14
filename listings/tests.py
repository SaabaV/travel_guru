from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Listing

User = get_user_model()

class ListingTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(email='owner@example.com', password='testpass123', name='Owner User')
        self.other_user = User.objects.create_user(email='other@example.com', password='testpass123', name='Other User')
        self.listing = Listing.objects.create(
            title='Test Listing',
            description='A nice place to stay.',
            location='Test City',
            price=100.00,
            rooms=2,
            property_type='Apartments',
            owner=self.user,
        )
        self.client.login(email='owner@example.com', password='testpass123')

    def test_create_listing_view(self):
        # Logout to test redirection for unauthenticated users
        self.client.logout()
        response = self.client.get(reverse('create_listing'))
        self.assertEqual(response.status_code, 302)  # Expect redirection to login

        # Login to test the creation of listing
        self.client.login(email='owner@example.com', password='testpass123')
        response = self.client.get(reverse('create_listing'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'listings/listing_form.html')

        data = {
            'title': 'New Listing',
            'description': 'A new nice place to stay.',
            'location': 'New City',
            'price': 200.00,
            'rooms': 3,
            'property_type': 'Villas',
            'is_active': True,
        }
        response = self.client.post(reverse('create_listing'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        self.assertEqual(Listing.objects.count(), 2)

    def test_edit_listing_view(self):
        # Test unauthenticated access
        self.client.logout()
        response = self.client.get(reverse('edit_listing', args=[self.listing.id]))
        self.assertEqual(response.status_code, 302)  # Expect redirection to login

        # Test unauthorized user access
        self.client.login(email='other@example.com', password='testpass123')
        response = self.client.get(reverse('edit_listing', args=[self.listing.id]))
        self.assertEqual(response.status_code, 403)  # Forbidden access

        # Test authorized user access
        self.client.login(email='owner@example.com', password='testpass123')
        response = self.client.get(reverse('edit_listing', args=[self.listing.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'listings/listing_form.html')

        data = {
            'title': 'Updated Listing',
            'description': 'An updated nice place to stay.',
            'location': 'Updated City',
            'price': 150.00,
            'rooms': 3,
            'property_type': 'Hotels',
            'is_active': True,
        }
        response = self.client.post(reverse('edit_listing', args=[self.listing.id]), data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful edit
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.title, 'Updated Listing')

    def test_delete_listing_view(self):
        self.client.login(email='owner@example.com', password='testpass123')
        response = self.client.get(reverse('delete_listing', args=[self.listing.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'listings/listing_confirm_delete.html')

        response = self.client.post(reverse('delete_listing', args=[self.listing.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Listing.objects.count(), 0)

    def test_toggle_listing_status_view(self):
        self.client.login(email='owner@example.com', password='testpass123')
        response = self.client.get(reverse('toggle_listing_status', args=[self.listing.id]))
        self.assertEqual(response.status_code, 302)
        self.listing.refresh_from_db()
        self.assertFalse(self.listing.is_active)

        response = self.client.get(reverse('toggle_listing_status', args=[self.listing.id]))
        self.assertEqual(response.status_code, 302)
        self.listing.refresh_from_db()
        self.assertTrue(self.listing.is_active)

    def test_listing_detail_view(self):
        response = self.client.get(reverse('listing_detail', args=[self.listing.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'listings/listing_detail.html')
        self.assertContains(response, self.listing.title)

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'listings/home.html')
        self.assertContains(response, self.listing.title)

        response = self.client.get(reverse('home') + '?location=Test City')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.listing.title)

        response = self.client.get(reverse('home') + '?sort_by=price_asc')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.listing.title)











