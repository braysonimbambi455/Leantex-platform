import stripe
from django.conf import settings
from django.core.mail import send_mail
from twilio.rest import Client
import sendgrid
from sendgrid.helpers.mail import Mail

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_payment_intent(amount, currency='kes'):
    """Create a Stripe payment intent"""
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert to cents/smallest unit
            currency=currency.lower(),
            metadata={'integration_check': 'accept_a_payment'},
        )
        return intent
    except Exception as e:
        print(f"Error creating payment intent: {e}")
        return None

def send_email_notification(recipient_email, subject, html_content):
    """Send email using SendGrid"""
    try:
        sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = recipient_email
        
        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )
        
        response = sg.send(message)
        return response.status_code == 202
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_sms_notification(to_phone, message):
    """Send SMS using Twilio"""
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        message = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to_phone
        )
        
        return message.sid is not None
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return False

def send_booking_confirmation(booking):
    """Send booking confirmation email and SMS"""
    # Email content
    subject = f"Booking Confirmation - {booking.booking_number}"
    html_content = f"""
    <h2>Booking Confirmed!</h2>
    <p>Dear {booking.customer_name},</p>
    <p>Your booking has been confirmed. Here are the details:</p>
    <ul>
        <li><strong>Booking Number:</strong> {booking.booking_number}</li>
        <li><strong>Service:</strong> {booking.service.name}</li>
        <li><strong>Date:</strong> {booking.date}</li>
        <li><strong>Time:</strong> {booking.time}</li>
        <li><strong>Status:</strong> {booking.status}</li>
    </ul>
    <p>Thank you for choosing Leantex!</p>
    """
    
    # Send email
    email_sent = send_email_notification(booking.customer_email, subject, html_content)
    
    # Send SMS
    sms_message = f"Leantex: Booking {booking.booking_number} confirmed for {booking.date} at {booking.time}. Thank you!"
    sms_sent = send_sms_notification(booking.customer_phone, sms_message)
    
    # Update booking
    booking.email_sent = email_sent
    booking.sms_sent = sms_sent
    booking.save()
    
    return email_sent and sms_sent