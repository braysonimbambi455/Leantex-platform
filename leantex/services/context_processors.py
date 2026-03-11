from .models import Category, Service

def services_processor(request):
    return {
        'all_categories': Category.objects.all(),
        'recent_services': Service.objects.filter(is_available=True)[:5],
    }