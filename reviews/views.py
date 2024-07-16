from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from listings.models import Listing
from listings.utils import get_listing_context
from bookings.models import Booking
from rest_framework import viewsets
from .models import Review
from .serializers import ReviewSerializer
from .models import Review
from .forms import ReviewForm


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


def listing_detail(request, pk):
    context = get_listing_context(request, pk)
    if isinstance(context, dict):
        return render(request, 'listings/listing_detail.html', context)
    return context


@login_required
def add_review(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)

    confirmed_bookings = Booking.objects.filter(listing=listing, user=request.user, status='confirmed').exists()

    if not confirmed_bookings:
        messages.error(request, 'You can only leave a review after booking this listing.')
        return redirect('listing_detail', pk=listing_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.listing = listing
            review.save()
            messages.success(request, 'Your review has been submitted and is pending approval.')
            return redirect('listing_detail', pk=listing_id)
    else:
        form = ReviewForm()
    return render(request, 'reviews/add_review.html', {'form': form, 'listing': listing})


def review_list(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    reviews = listing.reviews.filter(approved=True)
    context = {
        'listing': listing,
        'reviews': reviews,
    }
    return render(request, 'reviews/review_list.html', context)


@login_required
def approve_review(request, pk):
    review = get_object_or_404(Review, pk=pk, listing__owner=request.user)
    review.approved = True
    review.save()
    messages.success(request, 'Review approved.')
    return redirect('review_list', listing_id=review.listing.id)


@login_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk, listing__owner=request.user)
    review.delete()
    messages.success(request, 'Review deleted.')
    return redirect('review_list', listing_id=review.listing.id)



