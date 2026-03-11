from django.db import models
from django.contrib.auth.models import User
from bookings.models import Booking

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('stripe', 'Stripe'),
        ('pesapal', 'PesaPal'),
        ('cash', 'Cash'),
        ('mpesa', 'M-Pesa'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='stripe')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    
    # Payment details
    payment_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    # Additional data
    payment_data = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"Payment {self.transaction_id or self.id} - {self.amount}"

class Invoice(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='invoice')
    invoice_number = models.CharField(max_length=50, unique=True)
    pdf_file = models.FileField(upload_to='invoices/', null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Invoice {self.invoice_number}"