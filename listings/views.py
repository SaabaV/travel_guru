from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from django.contrib import messages
from datetime import timedelta
from bookings.forms import BookingForm
from bookings.models import Booking
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from rest_framework import viewsets
from .forms import ListingForm, ListingImageFormSet
from .models import Listing, ListingImage
from .utils import get_listing_context
from .models import Listing
from .serializers import ListingSerializer


class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer


def home(request):
    listings = Listing.objects.filter(is_active=True)

    location = request.GET.get('location', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    property_type = request.GET.get('property_type', '')
    min_rooms = request.GET.get('min_rooms', '')
    max_rooms = request.GET.get('max_rooms', '')
    search_query = request.GET.get('q', '')
    sort_by = request.GET.get('sort_by', '')

    if location:
        listings = listings.filter(location__icontains=location)
    if min_price:
        listings = listings.filter(price__gte=min_price)
    if max_price:
        listings = listings.filter(price__lte=max_price)
    if property_type:
        listings = listings.filter(property_type=property_type)
    if min_rooms:
        listings = listings.filter(rooms__gte=min_rooms)
    if max_rooms:
        listings = listings.filter(rooms__lte=max_rooms)
    if search_query:
        listings = listings.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )

    # Сортировка
    if sort_by == 'price_asc':
        listings = listings.order_by('price')
    elif sort_by == 'price_desc':
        listings = listings.order_by('-price')
    elif sort_by == 'date_asc':
        listings = listings.order_by('created_at')
    elif sort_by == 'date_desc':
        listings = listings.order_by('-created_at')
    elif sort_by == 'rating_asc':
        listings = listings.annotate(avg_rating=Avg('reviews__rating')).order_by('avg_rating')
    elif sort_by == 'rating_desc':
        listings = listings.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
    else:
        listings = listings.annotate(avg_rating=Avg('reviews__rating'))

    listings = listings.annotate(avg_rating=Avg('reviews__rating'))

    # Пагинация
    paginator = Paginator(listings, 10)  # 10 объявлений на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'location': location,
        'min_price': min_price,
        'max_price': max_price,
        'property_type': property_type,
        'min_rooms': min_rooms,
        'max_rooms': max_rooms,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    return render(request, 'listings/home.html', context)


@login_required
def create_listing(request):
    if not request.user.is_landlord:
        return redirect('home')
    if request.method == 'POST':
        form = ListingForm(request.POST)
        formset = ListingImageFormSet(request.POST, request.FILES, queryset=ListingImage.objects.none())
        if form.is_valid() and formset.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.save()
            for form in formset:
                if form.cleaned_data:
                    image = form.save(commit=False)
                    image.listing = listing
                    image.save()
            return redirect('home')
    else:
        form = ListingForm()
        formset = ListingImageFormSet(queryset=ListingImage.objects.none())
    return render(request, 'listings/listing_form.html', {'form': form, 'formset': formset})


@login_required
def edit_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    if request.user != listing.owner:
        return redirect('home')
    if request.method == 'POST':
        form = ListingForm(request.POST, instance=listing)
        formset = ListingImageFormSet(request.POST, request.FILES, queryset=ListingImage.objects.filter(listing=listing))
        if form.is_valid() and formset.is_valid():
            form.save()
            for form in formset:
                if form.cleaned_data:
                    image = form.save(commit=False)
                    image.listing = listing
                    image.save()
            return redirect('home')
    else:
        form = ListingForm(instance=listing)
        formset = ListingImageFormSet(queryset=ListingImage.objects.filter(listing=listing))
    return render(request, 'listings/listing_form.html', {'form': form, 'formset': formset})


@login_required
def delete_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    if request.user != listing.owner:
        return HttpResponseForbidden("You can only delete your own listings.")
    if request.method == 'POST':
        listing.delete()
        return redirect('home')
    return render(request, 'listings/listing_confirm_delete.html', {'listing': listing})


@login_required
def listing_detail(request, pk):
    context = get_listing_context(request, pk)
    if isinstance(context, dict):
        return render(request, 'listings/listing_detail.html', context)
    return context


@login_required
def toggle_listing_status(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    if request.user != listing.owner:
        return HttpResponseForbidden("You can only change the status of your own listings.")
    listing.is_active = not listing.is_active
    listing.save()
    return redirect('home')


@login_required
def update_booking_status(request, booking_id, status):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.user == booking.listing.owner:
        booking.status = status
        booking.save()

        try:
            send_mail(
                'Booking status updated',
                f'Your booking status has been updated to {status}.',
                'Travel@guru',
                [booking.user.email],
                fail_silently=False,
            )
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
        except ConnectionRefusedError:
            messages.error(request, 'Email server connection refused. Please check your email server settings.')
        except Exception as e:
            messages.error(request, f'An error occurred: {e}')

        messages.success(request, f'Booking status has been updated to {status}.')
        return redirect('home')
    else:
        messages.error(request, 'You are not authorized to update this booking.')
        return redirect('home')