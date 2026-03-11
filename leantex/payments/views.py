from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .models import Payment
from bookings.models import Booking
from .utils import create_payment_intent, send_booking_confirmation

@login_required
def checkout(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    
    # Check if payment already exists
    if hasattr(booking, 'payment'):
        messages.info(request, 'Payment already processed for this booking.')
        return redirect('bookings:detail', booking_id=booking.id)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'stripe')
        
        # Create payment intent
        intent = create_payment_intent(float(booking.service.price))
        
        if intent:
            # Create payment record
            payment = Payment.objects.create(
                booking=booking,
                customer=request.user,
                amount=booking.service.price,
                payment_method=payment_method,
                transaction_id=intent.id,
                payment_data={'intent_client_secret': intent.client_secret}
            )
            
            # Update booking status
            booking.payment_status = 'paid'
            booking.status = 'confirmed'
            booking.save()
            
            # Send confirmation notifications
            send_booking_confirmation(booking)
            
            messages.success(request, 'Payment successful! Booking confirmed.')
            return redirect('payments:success', payment_id=payment.id)
        else:
            messages.error(request, 'Payment failed. Please try again.')
            return redirect('payments:checkout', booking_id=booking.id)
    
    context = {
        'booking': booking,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'payments/checkout.html', context)

@login_required
def payment_success(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, customer=request.user)
    
    context = {
        'payment': payment,
        'booking': payment.booking,
    }
    return render(request, 'payments/success.html', context)

@login_required
def payment_history(request):
    payments = Payment.objects.filter(customer=request.user).order_by('-payment_date')
    
    context = {
        'payments': payments,
    }
    return render(request, 'dashboard/payment_history.html', context)