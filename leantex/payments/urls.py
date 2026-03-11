from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/<int:booking_id>/', views.checkout, name='checkout'),
    path('success/<int:payment_id>/', views.payment_success, name='success'),
    path('history/', views.payment_history, name='history'),
]