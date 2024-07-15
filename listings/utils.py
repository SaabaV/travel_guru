from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Avg
from datetime import timedelta
from bookings.models import Listing, Booking
from reviews.forms import Review, ReviewForm
from bookings.forms import BookingForm


def get_listing_context(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')

        form = BookingForm(request.POST)
        review_form = ReviewForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.listing = listing
            if Booking.objects.filter(listing=listing, start_date__lte=booking.end_date, end_date__gte=booking.start_date).exists():
                messages.error(request, 'The selected dates are not available for booking.')
            else:
                booking.price = listing.price * (booking.end_date - booking.start_date).days
                booking.save()
                messages.success(request, 'Your booking request has been submitted.')
                return redirect('listing_detail', pk=listing.pk)
        elif review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user
            review.listing = listing
            existing_review = Review.objects.filter(listing=listing, user=request.user).exists()
            if existing_review:
                messages.error(request, 'You have already submitted a review for this listing.')
            else:
                review.save()
                listing.update_avg_rating()
                messages.success(request, 'Your review has been submitted and is pending approval.')
            return redirect('listing_detail', pk=listing.pk)
    else:
        form = BookingForm()
        review_form = ReviewForm()

    booked_dates = Booking.objects.filter(listing=listing, status='confirmed').values_list('start_date', 'end_date')
    unavailable_dates = []
    for start_date, end_date in booked_dates:
        while start_date <= end_date:
            unavailable_dates.append(start_date.strftime('%Y-%m-%d'))
            start_date += timedelta(days=1)

    reviews = listing.reviews.filter(approved=True)
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or "No ratings yet"

    confirmed_bookings = False
    user_can_review = False
    if request.user.is_authenticated:
        confirmed_bookings = Booking.objects.filter(listing=listing, user=request.user, status='confirmed').exists()
        user_can_review = confirmed_bookings and not Review.objects.filter(listing=listing, user=request.user).exists()

    context = {
        'listing': listing,
        'form': form,
        'unavailable_dates': unavailable_dates,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_form': review_form if user_can_review else None,
        'confirmed_bookings': confirmed_bookings,
        'user_can_review': user_can_review,
    }
    return context


def get_unavailable_dates(listing):
    bookings = Booking.objects.filter(listing=listing, status='confirmed')
    dates = []
    for booking in bookings:
        current_date = booking.start_date
        while current_date <= booking.end_date:
            dates.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)
    return dates
