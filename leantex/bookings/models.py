from django.db import models
from django.contrib.auth.models import User
from services.models import Service

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    booking_number = models.CharField(max_length=20, unique=True, editable=False)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='bookings')
    technician = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_bookings')
    
    # Booking details
    date = models.DateField()
    time = models.TimeField()
    duration = models.IntegerField(help_text="Duration in minutes", default=60)
    
    # Customer information (in case customer is not logged in)
    customer_name = models.CharField(max_length=100, blank=True)
    customer_email = models.EmailField(blank=True)
    customer_phone = models.CharField(max_length=15, blank=True)
    customer_address = models.TextField(blank=True)
    
    # Additional notes
    notes = models.TextField(blank=True, help_text="Special instructions or notes")
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Notification tracking
    email_sent = models.BooleanField(default=False)
    sms_sent = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-date', '-time']

    def __str__(self):
        return f"Booking {self.booking_number} - {self.customer_name or self.customer.username}"

    def save(self, *args, **kwargs):
        if not self.booking_number:
            # Generate booking number: LEX-YYYYMMDD-XXXX
            from datetime import datetime
            from django.utils.crypto import get_random_string
            
            date_str = datetime.now().strftime('%Y%m%d')
            random_str = get_random_string(4, allowed_chars='0123456789')
            self.booking_number = f"LEX-{date_str}-{random_str}"
        
        # Set customer details if user is logged in
        if self.customer and not self.customer_name:
            self.customer_name = f"{self.customer.first_name} {self.customer.last_name}"
            self.customer_email = self.customer.email
            if hasattr(self.customer, 'profile'):
                self.customer_phone = self.customer.profile.phone_number
                self.customer_address = self.customer.profile.address
        
        super().save(*args, **kwargs)