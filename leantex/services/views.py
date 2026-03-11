from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Service, Category, Testimonial

def service_list(request):
    services = Service.objects.filter(is_available=True)
    categories = Category.objects.all()
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        services = services.filter(category_id=category_id)
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        services = services.filter(name__icontains=query) | services.filter(description__icontains=query)
    
    # Pagination
    paginator = Paginator(services, 9)  # 9 services per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': int(category_id) if category_id else None,
        'query': query,
    }
    return render(request, 'services.html', context)

def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk)
    related_services = Service.objects.filter(category=service.category, is_available=True).exclude(pk=pk)[:3]
    
    context = {
        'service': service,
        'related_services': related_services
    }
    return render(request, 'service_detail.html', context)

def home_view(request):
    featured_services = Service.objects.filter(is_available=True)[:6]
    testimonials = Testimonial.objects.filter(is_approved=True)[:5]
    categories = Category.objects.all()
    
    context = {
        'featured_services': featured_services,
        'testimonials': testimonials,
        'categories': categories,
    }
    return render(request, 'index.html', context)