from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('new/', views.create_listing, name='create_listing'),
    path('<int:pk>/edit/', views.edit_listing, name='edit_listing'),
    path('<int:pk>/delete/', views.delete_listing, name='delete_listing'),
    path('<int:pk>/toggle/', views.toggle_listing_status, name='toggle_listing_status'),
    path('<int:pk>/', views.listing_detail, name='listing_detail'),
]