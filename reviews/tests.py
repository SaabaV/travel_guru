from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from listings.models import Listing
from reviews.models import Review
from reviews.forms import ReviewForm

User = get_user_model()

class ReviewModelTests(TestCase):

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
        self.review = Review.objects.create(
            listing=self.listing,
            user=self.user,
            rating=5,
            comment='Great place!',
            approved=True
        )

    def test_review_creation(self):
        self.assertEqual(self.review.listing, self.listing)
        self.assertEqual(self.review.user, self.user)
        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.comment, 'Great place!')

    def test_approve_review(self):
        self.review.approve()
        self.assertTrue(self.review.approved)

class ReviewFormTests(TestCase):

    def test_review_form_valid(self):
        form_data = {
            'rating': 5,
            'comment': 'Great place!'
        }
        form = ReviewForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_review_form_invalid(self):
        form_data = {
            'rating': '',
            'comment': 'Great place!'
        }
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())

class ReviewViewTests(TestCase):

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
        self.review = Review.objects.create(
            listing=self.listing,
            user=self.user,
            rating=5,
            comment='Great place!',
            approved=True
        )

    def test_add_review_authenticated(self):
        self.client.login(email='testuser@example.com', password='12345')
        response = self.client.post(reverse('add_review', args=[self.listing.pk]), {
            'rating': 5,
            'comment': 'Amazing experience!'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation

    def test_add_review_unauthenticated(self):
        response = self.client.post(reverse('add_review', args=[self.listing.pk]), {
            'rating': 5,
            'comment': 'Amazing experience!'
        })
        self.assertRedirects(response, f'/users/login/?next=/reviews/listings/{self.listing.pk}/add_review/')

    def test_review_list_view(self):
        response = self.client.get(reverse('review_list', args=[self.listing.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.review.comment)

    def test_approve_review_view(self):
        self.client.login(email='testuser@example.com', password='12345')
        response = self.client.post(reverse('approve_review', args=[self.review.pk]))
        self.assertEqual(response.status_code, 302)
        self.review.refresh_from_db()
        self.assertTrue(self.review.approved)

    def test_delete_review_view(self):
        self.client.login(email='testuser@example.com', password='12345')
        response = self.client.post(reverse('delete_review', args=[self.review.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Review.objects.filter(pk=self.review.pk).exists())

