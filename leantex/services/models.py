from django.db import models
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class", default="fa-service")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Service(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField(help_text="Duration in minutes")
    image = models.ImageField(upload_to='services/', null=True, blank=True)
    is_available = models.BooleanField(default=True)
    features = models.TextField(help_text="List features separated by commas", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('services:detail', args=[str(self.id)])

    def get_features_list(self):
        if self.features:
            return [f.strip() for f in self.features.split(',')]
        return []

class Testimonial(models.Model):
    customer_name = models.CharField(max_length=100)
    customer_role = models.CharField(max_length=100, blank=True)
    content = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    image = models.ImageField(upload_to='testimonials/', null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} - {self.rating} stars"