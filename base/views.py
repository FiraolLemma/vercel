# project/base/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages as django_messages

from poultrys.models import ChickenSeller, Consultant, EggSeller, Item

from conversation.models import Conversation 
from .forms import MessageForm
from .models import Message
from dairys.models import DairyProduct, DairyService
from datetime import datetime
from django.db.models import Q
from poultrys.models import Item as PoultryItem

def base(request):
    User = get_user_model()
    users_count = User.objects.count()
    active_users_count = User.objects.filter(is_active=True).count()
    poultry_item_count = Item.objects.count()
    items_count = poultry_item_count
    conversations_count = Conversation.objects.count()
    dairy_product_count = DairyProduct.objects.filter(
        quantity_available__gt=0
    ).count()
    dairy_service_count = DairyService.objects.filter(is_available=True).count()
    egg_seller_count = EggSeller.objects.filter(is_active=True).count()
    chicken_seller_count = ChickenSeller.objects.filter(is_active=True).count()
    consultant_count = Consultant.objects.filter(is_available=True).count()
    featured_poultry = Item.objects.filter(is_featured=True)\
        .select_related('category')\
        .prefetch_related('sub_images')\
        .order_by('-created_at')[:12]
    featured_dairy = DairyProduct.objects.filter(is_featured=True)\
        .select_related('category', 'created_by')\
        .order_by('-created_at')[:12]
    
    for poultry in featured_poultry:
        poultry.product_type = 'poultry'

    for dairy_product in featured_dairy:
        dairy_product.product_type = 'dairy'
    
    all_featured = list(featured_poultry) + list(featured_dairy)
    
    def safe_sort_key(obj):
        """
        Safe sorting that handles both datetime and integer fallbacks
        """
        try:
            created = obj.created_at
        except AttributeError:
            
            created = getattr(obj, 'date_added', None)
        
        if isinstance(created, datetime):
            return created.timestamp()
        else:
            return float(getattr(obj, 'pk', 0))
    all_featured.sort(key=safe_sort_key, reverse=True)
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            Message.objects.create(
                phone=form.cleaned_data['phone'],
                message=form.cleaned_data['message']
            )
            django_messages.success(request, 'Message sent successfully!')
            return redirect('base:index')
    else:
        form = MessageForm()

    context = {
        'users_count': users_count,
        'active_users_count': active_users_count,
        'items_count': items_count,
        'conversations_count': conversations_count,
        'form': form,
        'all_featured': all_featured,
        'dairy_product_count': dairy_product_count,
        'dairy_service_count': dairy_service_count,
        'dairy_count': dairy_product_count + dairy_service_count,
        'poultry_item_count': poultry_item_count,
        'egg_seller_count': egg_seller_count,
        'chicken_seller_count': chicken_seller_count,
        'consultant_count': consultant_count,
        'poultry_count': (
            poultry_item_count
            + egg_seller_count
            + chicken_seller_count
            + consultant_count
        ),
    }

    return render(request, 'base/index.html', context)

def message_list(request):
    all_messages = Message.objects.all().order_by('-created_at')
    return render(request, 'base/messages.html', {'messages': all_messages})

def about_us(request):
    return render(request, 'base/about_us.html')

def admin_links(request):
    return render(request, 'base/admin_links.html')

def terms(request):
    return render(request, 'base/terms.html')

# search
def search_results(request):
    query = request.GET.get('q', '').strip()
    
    if not query:
        return render(request, 'base/search_results.html', {
            'query': '',
            'results': [],
            'no_query': True
        })
    
    results = []
    
    # Search Poultry
    poultry = PoultryItem.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query)
    ).select_related('created_by').prefetch_related('sub_images')[:10]
    
    for item in poultry:
        results.append({
            'type': 'poultry',
            'object': item,
            'title': item.name,
            'description': item.description,
            'price': item.price,
            'url': item.get_absolute_url()
        })

    dairy_products = DairyProduct.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(location__icontains=query) |
        Q(category__name__icontains=query)
    ).select_related('category', 'created_by')[:10]

    for product in dairy_products:
        results.append({
            'type': 'dairy',
            'object': product,
            'title': product.name,
            'description': product.description,
            'price': product.price,
            'url': product.get_absolute_url()
        })

    dairy_services = DairyService.objects.filter(
        is_available=True
    ).filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(location__icontains=query) |
        Q(service_type__icontains=query)
    ).select_related('provider')[:10]

    for service in dairy_services:
        results.append({
            'type': 'dairy_service',
            'object': service,
            'title': service.name,
            'description': service.description,
            'price': service.price,
            'url': service.get_absolute_url()
        })
    
    context = {
        'query': query,
        'results': results,
        'results_count': len(results),
        'poultry_count': len([r for r in results if r['type'] == 'poultry']),
        'dairy_count': len([r for r in results if r['type'] == 'dairy']),
        'dairy_service_count': len([r for r in results if r['type'] == 'dairy_service']),
    }
    
    return render(request, 'base/search_results.html', context)
