from django.contrib import admin
from .models import Listing, ListingImage


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1


class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'location', 'price', 'rooms', 'property_type', 'is_active', 'owner']
    list_filter = ['location', 'property_type', 'is_active']
    search_fields = ['title', 'description', 'location']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ListingImageInline]

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'location', 'price', 'rooms', 'property_type', 'owner', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


admin.site.register(Listing, ListingAdmin)

