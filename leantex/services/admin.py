from django.contrib import admin
from .models import Category, Service, Testimonial

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'duration', 'is_available', 'created_at']
    list_filter = ['category', 'is_available']
    search_fields = ['name', 'description']
    list_editable = ['is_available']

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'rating', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'rating']
    list_editable = ['is_approved']