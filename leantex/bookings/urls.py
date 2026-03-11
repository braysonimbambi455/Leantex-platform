from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('create/', views.booking_create, name='create'),
    path('create/<int:service_id>/', views.booking_create, name='create_with_service'),
    path('list/', views.booking_list, name='list'),
    path('<int:booking_id>/', views.booking_detail, name='detail'),
    path('<int:booking_id>/cancel/', views.booking_cancel, name='cancel'),
]