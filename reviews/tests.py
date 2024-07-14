from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from listings.models import Listing
from bookings.models import Booking
from reviews.models import Review
from datetime import date

User = get_user_model()

class ReviewTests(TestCase):

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
            status='confirmed',
        )
        self.review = Review.objects.create(
            listing=self.listing,
            user=self.user,
            rating=5,
            comment='Great place!',
            approved=False
        )
        self.client.login(email='testuser@example.com', password='testpass123')

    def test_add_review_view(self):
        response = self.client.get(reverse('add_review', args=[self.listing.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reviews/add_review.html')

        data = {
            'rating': 5,
            'comment': 'Amazing stay!'
        }
        response = self.client.post(reverse('add_review', args=[self.listing.pk]), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.filter(listing=self.listing).count(), 2)

    def test_review_list_view(self):
        self.review.approved = True  # Убедитесь, что отзыв одобрен
        self.review.save()
        response = self.client.get(reverse('review_list', args=[self.listing.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reviews/review_list.html')
        self.assertContains(response, self.review.comment)

    def test_review_approval(self):
        self.client.logout()
        self.client.login(email='owner@example.com', password='testpass123')
        response = self.client.post(reverse('approve_review', args=[self.review.pk]))
        self.assertEqual(response.status_code, 302)
        self.review.refresh_from_db()
        self.assertTrue(self.review.approved)

    def test_review_deletion(self):
        self.client.logout()
        self.client.login(email='owner@example.com', password='testpass123')
        response = self.client.post(reverse('delete_review', args=[self.review.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.filter(listing=self.listing).count(), 0)

