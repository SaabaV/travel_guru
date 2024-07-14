from django.urls import path
from .views import add_review, review_list, approve_review, delete_review, listing_detail

urlpatterns = [
    path('listings/<int:pk>/', listing_detail, name='listing_detail'),
    path('listings/<int:listing_id>/add_review/', add_review, name='add_review'),
    path('listings/<int:listing_id>/reviews/', review_list, name='review_list'),
    path('reviews/approve/<int:pk>/', approve_review, name='approve_review'),
    path('reviews/delete/<int:pk>/', delete_review, name='delete_review'),
]
