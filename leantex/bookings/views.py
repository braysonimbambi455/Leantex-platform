from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Booking
from .forms import BookingForm, GuestBookingForm
from services.models import Service
from payments.utils import create_payment_intent

def booking_create(request, service_id=None):
    service = None
    if service_id:
        service = get_object_or_404(Service, id=service_id, is_available=True)
    
    if request.user.is_authenticated:
        form_class = BookingForm
        initial_data = {'service': service} if service else {}
    else:
        form_class = GuestBookingForm
        initial_data = {'service': service} if service else {}
    
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            
            if request.user.is_authenticated:
                booking.customer = request.user
                booking.customer_name = f"{request.user.first_name} {request.user.last_name}"
                booking.customer_email = request.user.email
                if hasattr(request.user, 'profile'):
                    booking.customer_phone = request.user.profile.phone_number
                    booking.customer_address = request.user.profile.address
            
            booking.save()
            messages.success(request, 'Booking created successfully! Please complete payment.')
            
            # Redirect to payment
            return redirect('payments:checkout', booking_id=booking.id)
    else:
        form = form_class(initial=initial_data)
    
    context = {
        'form': form,
        'service': service,
    }
    return render(request, 'booking_form.html', context)

@login_required
def booking_list(request):
    if request.user.profile.role == 'customer':
        bookings = Booking.objects.filter(customer=request.user)
    elif request.user.profile.role == 'technician':
        bookings = Booking.objects.filter(technician=request.user)
    else:
        bookings = Booking.objects.all()
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        bookings = bookings.filter(status=status)
    
    context = {
        'bookings': bookings.order_by('-date', '-time'),
    }
    return render(request, 'dashboard/bookings_list.html', context)

@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check permissions
    if request.user.profile.role == 'customer' and booking.customer != request.user:
        messages.error(request, 'You do not have permission to view this booking.')
        return redirect('bookings:list')
    
    context = {
        'booking': booking,
    }
    return render(request, 'dashboard/booking_detail.html', context)

@login_required
def booking_cancel(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check permissions
    if request.user.profile.role == 'customer' and booking.customer != request.user:
        messages.error(request, 'You cannot cancel this booking.')
        return redirect('bookings:list')
    
    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Booking cancelled successfully.')
        
        # Send cancellation email
        # send_cancellation_notification(booking)
        
        return redirect('bookings:detail', booking_id=booking.id)
    
    return render(request, 'dashboard/booking_cancel.html', {'booking': booking})