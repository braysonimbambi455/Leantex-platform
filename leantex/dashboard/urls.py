from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('customer/', views.customer_dashboard, name='customer'),
    path('technician/', views.technician_dashboard, name='technician'),
    path('admin/', views.admin_dashboard, name='admin'),
    path('admin/bookings/', views.manage_bookings, name='manage_bookings'),
    path('admin/assign/<int:booking_id>/', views.assign_technician, name='assign_technician'),
]