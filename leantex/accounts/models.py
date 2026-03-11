from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    USER_ROLES = (
        ('customer', 'Customer'),
        ('technician', 'Technician'),
        ('admin', 'Admin'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True)
    role = models.CharField(max_length=20, choices=USER_ROLES, default='customer')
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()