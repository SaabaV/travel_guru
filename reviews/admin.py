from django.contrib import admin
from .models import Review


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('listing', 'user', 'rating', 'approved', 'created_at')
    list_filter = ('approved', 'created_at')
    search_fields = ('user__username', 'listing__title', 'comment')
    actions = ['approve_reviews', 'disapprove_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(approved=True)

    def disapprove_reviews(self, request, queryset):
        queryset.update(approved=False)


admin.site.register(Review, ReviewAdmin)
