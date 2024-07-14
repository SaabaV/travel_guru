from django.urls import path
from . import views

urlpatterns = [
    path('create/<int:listing_id>/', views.create_booking, name='create_booking'),
    path('my_bookings/', views.my_bookings, name='my_bookings'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('manage/', views.manage_bookings, name='manage_bookings'),
    path('update/<int:booking_id>/<str:status>/', views.update_booking_status, name='update_booking_status'),
    path('start_payment/<int:booking_id>/', views.stripe_payment, name='start_payment'),
    path('confirm_payment/<int:booking_id>/', views.confirm_payment, name='confirm_payment'),
    path('payment_success/', views.payment_success, name='payment_success'),
    path('payment_cancel/', views.payment_cancel, name='payment_cancel'),
]
