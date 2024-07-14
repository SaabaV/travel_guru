from django import forms
from bootstrap_datepicker_plus.widgets import DatePickerInput
from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['start_date', 'end_date']
        widgets = {
            'start_date': forms.TextInput(attrs={
                'placeholder': 'Select start date',
                'class': 'datepicker'
            }),
            'end_date': forms.TextInput(attrs={
                'placeholder': 'Select end date',
                'class': 'datepicker'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError('End date must be after start date.')

        return cleaned_data

