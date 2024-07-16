from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import stripe
from django.urls import reverse
from django.conf import settings
from listings.models import Listing
from django.views.decorators.http import require_POST
from rest_framework import viewsets
from .models import Booking, Payment
from .forms import BookingForm
from .models import Booking
from .serializers import BookingSerializer


stripe.api_key = settings.STRIPE_SECRET_KEY


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer


@login_required
def stripe_payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.status != 'confirmed':
        messages.error(request, 'Booking is not confirmed yet.')
        return redirect('my_bookings')

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': booking.listing.title,
                },
                'unit_amount': int(booking.price * 100),
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri(reverse('payment_success')) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri(reverse('payment_cancel')),
    )

    return render(request, 'bookings/start_payment.html', {
        'session_id': session.id,
        'stripe_public_key': settings.STRIPE_PUBLISHABLE_KEY
    })


@login_required
def payment_success(request):
    session_id = request.GET.get('session_id')
    session = stripe.checkout.Session.retrieve(session_id)

    booking = get_object_or_404(Booking, id=session.client_reference_id)
    booking.status = 'completed'
    booking.save()

    messages.success(request, 'Payment successful! Your booking is complete.')
    return redirect('my_bookings')


@login_required
def payment_cancel(request):
    messages.error(request, 'Payment was cancelled.')
    return redirect('my_bookings')


@require_POST
def confirm_payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    payment = get_object_or_404(Payment, booking=booking)

    payment_intent_id = request.POST.get('payment_intent_id')

    if payment.stripe_payment_intent_id == payment_intent_id:
        payment.status = 'paid'
        payment.save()

        booking.status = 'completed'
        booking.save()

        messages.success(request, 'Your payment has been successful.')
        return redirect('my_bookings')

    messages.error(request, 'There was an error with your payment.')
    return redirect('start_payment', booking_id=booking_id)


@login_required
def create_booking(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.listing = listing
            booking.price = listing.price * (booking.end_date - booking.start_date).days
            booking.save()
            messages.success(request, 'Your booking request has been submitted.')
            return redirect('my_bookings')
        else:
            print(form.errors)
    else:
        form = BookingForm()

    unavailable_dates = Booking.get_unavailable_dates(listing)
    context = {
        'form': form,
        'listing': listing,
        'unavailable_dates': unavailable_dates,
    }
    return render(request, 'bookings/create_booking.html', context)


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'bookings/my_bookings.html', {'bookings': bookings})


@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Your booking has been cancelled.')
        return redirect('my_bookings')
    return render(request, 'bookings/cancel_booking.html', {'booking': booking})


@login_required
def manage_bookings(request):
    user_listings = Listing.objects.filter(owner=request.user)
    bookings = Booking.objects.filter(listing__owner=request.user).select_related('user', 'listing')

    return render(request, 'bookings/manage_bookings.html', {
        'bookings': bookings,
        'listings': user_listings,
    })


@login_required
def update_booking_status(request, booking_id, status):
    booking = get_object_or_404(Booking, id=booking_id, listing__owner=request.user)
    if status not in dict(Booking.STATUS_CHOICES):
        messages.error(request, 'Invalid status.')
    else:
        booking.status = status
        booking.save()
        messages.success(request, f'Booking status updated to {booking.get_status_display()}')
    return redirect('manage_bookings')



