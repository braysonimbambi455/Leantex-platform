from django import forms
from django.utils import timezone
from .models import Booking
from services.models import Service

class DateInput(forms.DateInput):
    input_type = 'date'

class TimeInput(forms.TimeInput):
    input_type = 'time'

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['service', 'date', 'time', 'notes']
        widgets = {
            'date': DateInput(attrs={'class': 'form-control', 'min': timezone.now().date()}),
            'time': TimeInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['service'].widget.attrs.update({'class': 'form-control'})
        self.fields['service'].queryset = Service.objects.filter(is_available=True)
        
    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date < timezone.now().date():
            raise forms.ValidationError("Booking date cannot be in the past.")
        return date

class GuestBookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['service', 'customer_name', 'customer_email', 'customer_phone', 
                  'customer_address', 'date', 'time', 'notes']
        widgets = {
            'date': DateInput(attrs={'class': 'form-control', 'min': timezone.now().date()}),
            'time': TimeInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['service'].widget.attrs.update({'class': 'form-control'})
        self.fields['service'].queryset = Service.objects.filter(is_available=True)
    
    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date < timezone.now().date():
            raise forms.ValidationError("Booking date cannot be in the past.")
        return date