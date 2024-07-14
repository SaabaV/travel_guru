from django import forms
from .models import Listing, ListingImage


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'location', 'price', 'rooms', 'property_type', 'is_active']


class ListingImageForm(forms.ModelForm):
    class Meta:
        model = ListingImage
        fields = ['image']


ListingImageFormSet = forms.inlineformset_factory(Listing, ListingImage, form=ListingImageForm, extra=10, max_num=10)

