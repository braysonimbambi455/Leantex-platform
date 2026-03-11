from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from bookings.models import Booking
from services.models import Service, Testimonial
from accounts.models import User
from payments.models import Payment
from datetime import timedelta



@login_required
def dashboard_home(request):
    user = request.user
    
    if user.profile.role == 'admin':
        return redirect('dashboard:admin')
    elif user.profile.role == 'technician':
        return redirect('dashboard:technician')
    else:
        return redirect('dashboard:customer')

@login_required
def customer_dashboard(request):
    user = request.user
    
    # Get user's bookings
    upcoming_bookings = Booking.objects.filter(
        customer=user,
        date__gte=timezone.now().date(),
        status__in=['confirmed', 'assigned', 'in_progress']
    ).order_by('date', 'time')[:5]
    
    past_bookings = Booking.objects.filter(
        customer=user,
        status='completed'
    ).order_by('-date', '-time')[:5]
    
    # Statistics
    total_bookings = Booking.objects.filter(customer=user).count()
    completed_bookings = Booking.objects.filter(customer=user, status='completed').count()
    pending_payments = Payment.objects.filter(customer=user, status='pending').count()
    
    context = {
        'upcoming_bookings': upcoming_bookings,
        'past_bookings': past_bookings,
        'total_bookings': total_bookings,
        'completed_bookings': completed_bookings,
        'pending_payments': pending_payments,
    }
    return render(request, 'dashboard/customer_dashboard.html', context)

@login_required
def technician_dashboard(request):
    if request.user.profile.role != 'technician':
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    # Get assigned bookings
    today = timezone.now().date()
    
    today_bookings = Booking.objects.filter(
        technician=request.user,
        date=today
    ).order_by('time')
    
    upcoming_bookings = Booking.objects.filter(
        technician=request.user,
        date__gt=today,
        status__in=['assigned', 'confirmed']
    ).order_by('date', 'time')
    
    completed_today = Booking.objects.filter(
        technician=request.user,
        date=today,
        status='completed'
    ).count()
    
    context = {
        'today_bookings': today_bookings,
        'upcoming_bookings': upcoming_bookings,
        'completed_today': completed_today,
    }
    return render(request, 'dashboard/technician_dashboard.html', context)

@login_required
@staff_member_required
def admin_dashboard(request):
    # Statistics
    total_customers = User.objects.filter(profile__role='customer').count()
    total_technicians = User.objects.filter(profile__role='technician').count()
    total_bookings = Booking.objects.count()
    total_revenue = Payment.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Recent bookings
    recent_bookings = Booking.objects.all().order_by('-created_at')[:10]
    
    # Bookings by status
    status_counts = Booking.objects.values('status').annotate(count=Count('status'))
    
    # Revenue by month (last 6 months)
    six_months_ago = timezone.now() - timedelta(days=180)
    monthly_revenue = Payment.objects.filter(
        status='completed',
        payment_date__gte=six_months_ago
    ).extra({'month': "EXTRACT(month FROM payment_date)"}).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')
    
    # Popular services
    popular_services = Service.objects.annotate(
        booking_count=Count('bookings')
    ).order_by('-booking_count')[:5]
    
    context = {
        'total_customers': total_customers,
        'total_technicians': total_technicians,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'recent_bookings': recent_bookings,
        'status_counts': status_counts,
        'monthly_revenue': monthly_revenue,
        'popular_services': popular_services,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)

@login_required
@staff_member_required
def manage_bookings(request):
    bookings = Booking.objects.all().order_by('-date', '-time')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        bookings = bookings.filter(status=status)
    
    # Filter by date
    date_from = request.GET.get('date_from')
    if date_from:
        bookings = bookings.filter(date__gte=date_from)
    
    context = {
        'bookings': bookings,
    }
    return render(request, 'dashboard/manage_bookings.html', context)

@login_required
@staff_member_required
def assign_technician(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    technicians = User.objects.filter(profile__role='technician', is_active=True)
    
    if request.method == 'POST':
        technician_id = request.POST.get('technician')
        technician = get_object_or_404(User, id=technician_id)
        
        booking.technician = technician
        booking.status = 'assigned'
        booking.save()
        
        messages.success(request, f'Technician assigned to booking {booking.booking_number}')
        return redirect('dashboard:manage_bookings')
    
    context = {
        'booking': booking,
        'technicians': technicians,
    }
    return render(request, 'dashboard/assign_technician.html', context)
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta, datetime
from bookings.models import Booking
from services.models import Service, Testimonial
from accounts.models import User, Profile
from payments.models import Payment

# Add to existing views or create new ones

def customer_dashboard(request):
    user = request.user
    
    # Get user's bookings
    upcoming_bookings = Booking.objects.filter(
        customer=user,
        date__gte=timezone.now().date(),
        status__in=['pending', 'confirmed', 'assigned', 'in_progress']
    ).order_by('date', 'time')[:5]
    
    past_bookings = Booking.objects.filter(
        customer=user,
        status='completed'
    ).order_by('-date', '-time')[:5]
    
    # Statistics
    total_bookings = Booking.objects.filter(customer=user).count()
    completed_bookings = Booking.objects.filter(customer=user, status='completed').count()
    pending_payments = Booking.objects.filter(
        customer=user, 
        payment_status='pending'
    ).count()
    
    # Add feedback tracking
    for booking in past_bookings:
        booking.feedback_given = hasattr(booking, 'feedback')
    
    context = {
        'upcoming_bookings': upcoming_bookings,
        'past_bookings': past_bookings,
        'total_bookings': total_bookings,
        'completed_bookings': completed_bookings,
        'pending_payments': pending_payments,
        'now': timezone.now(),
    }
    return render(request, 'dashboard/customer_dashboard.html', context)

def technician_dashboard(request):
    if request.user.profile.role != 'technician':
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    today = timezone.now().date()
    
    # Get today's bookings
    today_bookings = Booking.objects.filter(
        technician=request.user,
        date=today
    ).order_by('time')
    
    # Get upcoming bookings
    upcoming_bookings = Booking.objects.filter(
        technician=request.user,
        date__gt=today,
        status__in=['assigned', 'confirmed']
    ).order_by('date', 'time')
    
    # Get completed bookings
    completed_bookings = Booking.objects.filter(
        technician=request.user,
        status='completed'
    ).order_by('-date')[:10]
    
    # Statistics
    completed_today = Booking.objects.filter(
        technician=request.user,
        date=today,
        status='completed'
    ).count()
    
    monthly_completed = Booking.objects.filter(
        technician=request.user,
        status='completed',
        date__month=today.month,
        date__year=today.year
    ).count()
    
    # Weekly stats
    week_start = today - timedelta(days=today.weekday())
    weekly_count = Booking.objects.filter(
        technician=request.user,
        status='completed',
        date__gte=week_start
    ).count()
    weekly_target = 10  # Example target
    
    context = {
        'today_bookings': today_bookings,
        'upcoming_bookings': upcoming_bookings,
        'completed_bookings': completed_bookings,
        'completed_today': completed_today,
        'monthly_completed': monthly_completed,
        'weekly_count': weekly_count,
        'weekly_target': weekly_target,
        'now': timezone.now(),
    }
    return render(request, 'dashboard/technician_dashboard.html', context)

def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    today = timezone.now().date()
    
    # Basic statistics
    total_customers = User.objects.filter(profile__role='customer').count()
    total_technicians = User.objects.filter(profile__role='technician').count()
    total_bookings = Booking.objects.count()
    total_revenue = Payment.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Monthly statistics
    monthly_bookings = Booking.objects.filter(
        date__month=today.month,
        date__year=today.year
    ).count()
    
    new_customers = User.objects.filter(
        date_joined__month=today.month,
        date_joined__year=today.year
    ).count()
    
    # Pending tasks
    pending_bookings = Booking.objects.filter(status='pending').count()
    unassigned_bookings = Booking.objects.filter(technician__isnull=True, status='confirmed').count()
    
    # Status counts for chart
    status_counts = Booking.objects.values('status').annotate(count=Count('status'))
    
    # Recent bookings
    recent_bookings = Booking.objects.select_related('service', 'technician').order_by('-created_at')[:10]
    
    # Popular services
    popular_services = Service.objects.annotate(
        booking_count=Count('bookings')
    ).order_by('-booking_count')[:5]
    
    # Technician performance
    technicians = User.objects.filter(profile__role='technician').annotate(
        completed_jobs=Count('assigned_bookings', filter=Q(assigned_bookings__status='completed')),
        assigned_jobs=Count('assigned_bookings', filter=~Q(assigned_bookings__status='completed')),
        avg_rating=Avg('assigned_bookings__feedback__rating')
    )
    
    for tech in technicians:
        # Calculate current load percentage
        total_capacity = 10  # Example: max jobs per technician
        tech.current_load = (tech.assigned_jobs or 0) * 100 // total_capacity
        tech.on_time_rate = 98  # Example static value
        
    completed_today = Booking.objects.filter(
        status='completed',
        date=today
    ).count()
    
    context = {
        'total_customers': total_customers,
        'total_technicians': total_technicians,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'monthly_bookings': monthly_bookings,
        'new_customers': new_customers,
        'pending_bookings': pending_bookings,
        'unassigned_bookings': unassigned_bookings,
        'status_counts': status_counts,
        'recent_bookings': recent_bookings,
        'popular_services': popular_services,
        'technicians': technicians,
        'completed_today': completed_today,
        'today_date': today,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)

# Add these URL patterns to dashboard/urls.py
"""
path('start-job/<int:booking_id>/', views.start_job, name='start_job'),
path('complete-job/<int:booking_id>/', views.complete_job, name='complete_job'),
path('support/', views.support_request, name='support'),
"""

def start_job(request, booking_id):
    if request.method == 'POST' and request.user.profile.role == 'technician':
        booking = get_object_or_404(Booking, id=booking_id, technician=request.user)
        booking.status = 'in_progress'
        booking.save()
        messages.success(request, 'Job started successfully.')
    return redirect('dashboard:technician')

def complete_job(request, booking_id):
    if request.method == 'POST' and request.user.profile.role == 'technician':
        booking = get_object_or_404(Booking, id=booking_id, technician=request.user)
        booking.status = 'completed'
        booking.save()
        messages.success(request, 'Job marked as completed.')
    return redirect('dashboard:technician')

def support_request(request):
    if request.method == 'POST':
        # Handle support request - send email to admin
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        # Send email logic here
        messages.success(request, 'Support request sent successfully.')
    return redirect('dashboard:customer')