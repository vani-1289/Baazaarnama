from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse

from .models import Market, Category, Shop, Product, Offer, Wishlist, FavoriteShop
from .forms import ShopForm, ProductForm, OfferForm
from feedback.forms import ReviewForm

def home(request):
    markets = Market.objects.all().order_by('-created_date')[:6]
    categories = Category.objects.all()[:8]
    featured_shops = Shop.objects.filter(verified_shop=True).select_related('market', 'category')[:6]
    
    # If no verified shops, grab any 6 shops
    if not featured_shops.exists():
        featured_shops = Shop.objects.all().select_related('market', 'category')[:6]
        
    latest_offers = Offer.objects.all().select_related('shop')[:4]
    
    # Calculate some dashboard stats for landing page
    stats = {
        'markets_count': Market.objects.count(),
        'shops_count': Shop.objects.count(),
        'products_count': Product.objects.count(),
        'happy_customers': 1500 + Wishlist.objects.count() * 7,
    }
    
    context = {
        'markets': markets,
        'categories': categories,
        'featured_shops': featured_shops,
        'offers': latest_offers,
        'stats': stats,
    }
    return render(request, 'bazaar/home.html', context)


def search(request):
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')
    city = request.GET.get('city', '')
    
    markets = Market.objects.all()
    shops = Shop.objects.all().select_related('market', 'category')
    products = Product.objects.all().select_related('shop')
    
    if query:
        markets = markets.filter(Q(name__icontains=query) | Q(city__icontains=query) | Q(state__icontains=query))
        shops = shops.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(address__icontains=query))
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
        
    if category_id:
        shops = shops.filter(category_id=category_id)
        
    if city:
        markets = markets.filter(city__icontains=city)
        shops = shops.filter(market__city__icontains=city)
        
    # Get all cities for the filter dropdown
    all_cities = Market.objects.values_list('city', flat=True).distinct()
    categories = Category.objects.all()

    context = {
        'query': query,
        'selected_category': category_id,
        'selected_city': city,
        'cities': all_cities,
        'categories': categories,
        'markets': markets[:12],
        'shops': shops[:12],
        'products': products[:12],
    }
    return render(request, 'bazaar/search_results.html', context)


def market_list(request):
    markets = Market.objects.all().order_by('name')
    cities = Market.objects.values_list('city', flat=True).distinct()
    
    selected_city = request.GET.get('city', '')
    if selected_city:
        markets = markets.filter(city=selected_city)
        
    context = {
        'markets': markets,
        'cities': cities,
        'selected_city': selected_city,
    }
    return render(request, 'bazaar/market_list.html', context)


def market_detail(request, pk):
    market = get_object_or_404(Market, pk=pk)
    shops = market.shops.all().select_related('category', 'owner')
    categories = Category.objects.all()
    
    # Filter by category if selected
    selected_cat = request.GET.get('category', '')
    if selected_cat:
        shops = shops.filter(category_id=selected_cat)
        
    # Search within market shops
    shop_query = request.GET.get('shop_q', '')
    if shop_query:
        shops = shops.filter(name__icontains=shop_query)

    context = {
        'market': market,
        'shops': shops,
        'categories': categories,
        'selected_category': selected_cat,
        'shop_query': shop_query,
    }
    return render(request, 'bazaar/market_detail.html', context)


def shop_list(request):
    shops = Shop.objects.all().select_related('market', 'category')
    categories = Category.objects.all()
    
    selected_cat = request.GET.get('category', '')
    if selected_cat:
        shops = shops.filter(category_id=selected_cat)
        
    context = {
        'shops': shops,
        'categories': categories,
        'selected_category': selected_cat,
    }
    return render(request, 'bazaar/shop_list.html', context)


def shop_detail(request, pk):
    shop = get_object_or_404(Shop, pk=pk)
    products = shop.products.filter(available=True)
    offers = shop.offers.all()
    reviews = shop.reviews.all().select_related('user', 'user__profile').order_by('-created_date')
    review_form = ReviewForm()
    
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = FavoriteShop.objects.filter(user=request.user, shop=shop).exists()
        
    context = {
        'shop': shop,
        'products': products,
        'offers': offers,
        'reviews': reviews,
        'review_form': review_form,
        'is_favorite': is_favorite,
    }
    return render(request, 'bazaar/shop_detail.html', context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    related_products = Product.objects.filter(shop=product.shop).exclude(pk=pk)[:4]
    
    is_wishlisted = False
    if request.user.is_authenticated:
        is_wishlisted = Wishlist.objects.filter(user=request.user, product=product).exists()
        
    context = {
        'product': product,
        'related_products': related_products,
        'is_wishlisted': is_wishlisted,
    }
    return render(request, 'bazaar/product_detail.html', context)


@login_required
def wishlist_toggle(request, pk):
    product = get_object_or_404(Product, pk=pk)
    wishlist_item = Wishlist.objects.filter(user=request.user, product=product)
    
    if wishlist_item.exists():
        wishlist_item.delete()
        added = False
        msg = f"{product.name} removed from your wishlist."
    else:
        Wishlist.objects.create(user=request.user, product=product)
        added = True
        msg = f"{product.name} added to your wishlist."
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'added': added, 'message': msg})
        
    messages.info(request, msg)
    return redirect('bazaar:product_detail', pk=pk)


@login_required
def favorite_toggle(request, pk):
    shop = get_object_or_404(Shop, pk=pk)
    fav = FavoriteShop.objects.filter(user=request.user, shop=shop)
    
    if fav.exists():
        fav.delete()
        added = False
        msg = f"{shop.name} removed from your favorites."
    else:
        FavoriteShop.objects.create(user=request.user, shop=shop)
        added = True
        msg = f"{shop.name} added to your favorites."
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'added': added, 'message': msg})
        
    messages.info(request, msg)
    return redirect('bazaar:shop_detail', pk=pk)


# --- SELLER CRUD VIEWS ---

@login_required
def add_shop(request):
    if not request.user.profile.is_seller:
        messages.warning(request, "Access restricted. Please register as a seller first.")
        return redirect('users:dashboard')
        
    if request.method == 'POST':
        form = ShopForm(request.POST, request.FILES)
        if form.is_valid():
            shop = form.save(commit=False)
            shop.owner = request.user
            shop.save()
            messages.success(request, f"Shop '{shop.name}' created successfully!")
            return redirect('users:dashboard_seller')
    else:
        form = ShopForm()
    return render(request, 'bazaar/add_shop.html', {'form': form, 'title': 'Register New Shop'})


@login_required
def edit_shop(request, pk):
    shop = get_object_or_404(Shop, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        form = ShopForm(request.POST, request.FILES, instance=shop)
        if form.is_valid():
            form.save()
            messages.success(request, "Shop details updated successfully!")
            return redirect('users:dashboard_seller')
    else:
        form = ShopForm(instance=shop)
    return render(request, 'bazaar/add_shop.html', {'form': form, 'title': 'Edit Shop Details', 'shop': shop})


@login_required
def add_product(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id, owner=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.shop = shop
            product.save()
            messages.success(request, f"Product '{product.name}' added successfully!")
            return redirect('users:dashboard_seller')
    else:
        form = ProductForm()
    return render(request, 'bazaar/add_product.html', {'form': form, 'shop': shop, 'title': 'Add New Product'})


@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk, shop__owner=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect('users:dashboard_seller')
    else:
        form = ProductForm(instance=product)
    return render(request, 'bazaar/add_product.html', {'form': form, 'shop': product.shop, 'title': 'Edit Product', 'product': product})


@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk, shop__owner=request.user)
    product.delete()
    messages.success(request, "Product deleted successfully.")
    return redirect('users:dashboard_seller')


@login_required
def add_offer(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id, owner=request.user)
    
    if request.method == 'POST':
        form = OfferForm(request.POST)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.shop = shop
            offer.save()
            messages.success(request, f"Offer '{offer.title}' created successfully!")
            return redirect('users:dashboard_seller')
    else:
        form = OfferForm()
    return render(request, 'bazaar/add_offer.html', {'form': form, 'shop': shop, 'title': 'Create New Offer'})


@login_required
def edit_offer(request, pk):
    offer = get_object_or_404(Offer, pk=pk, shop__owner=request.user)
    
    if request.method == 'POST':
        form = OfferForm(request.POST, instance=offer)
        if form.is_valid():
            form.save()
            messages.success(request, "Offer updated successfully!")
            return redirect('users:dashboard_seller')
    else:
        form = OfferForm(instance=offer)
    return render(request, 'bazaar/add_offer.html', {'form': form, 'shop': offer.shop, 'title': 'Edit Offer', 'offer': offer})


@login_required
def delete_offer(request, pk):
    offer = get_object_or_404(Offer, pk=pk, shop__owner=request.user)
    offer.delete()
    messages.success(request, "Offer deleted successfully.")
    return redirect('users:dashboard_seller')