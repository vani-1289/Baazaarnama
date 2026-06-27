from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required

from bazaar.models import Market, Shop, Product, Wishlist, FavoriteShop
from feedback.models import Review
from .forms import RegisterForm, UserUpdateForm, ProfileUpdateForm

def register(request):
    if request.user.is_authenticated:
        return redirect('bazaar:home')
        
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Welcome to Baazaarnama, {user.username}! Your profile has been created.")
            login(request, user)
            return redirect('users:dashboard')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    return render(request, 'users/profile.html')


@login_required
def profile_edit(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('users:profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
        
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/profile_edit.html', context)


@login_required
def dashboard(request):
    # Route according to roles: Admin (staff), Seller, Customer
    if request.user.is_staff:
        return redirect('users:dashboard_admin')
    elif request.user.profile.is_seller:
        return redirect('users:dashboard_seller')
    else:
        return redirect('users:dashboard_customer')


@login_required
def dashboard_customer(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product', 'product__shop')
    favorite_shops = FavoriteShop.objects.filter(user=request.user).select_related('shop', 'shop__market')
    my_reviews = Review.objects.filter(user=request.user).select_related('shop')
    
    context = {
        'wishlist': wishlist_items,
        'favorite_shops': favorite_shops,
        'reviews': my_reviews
    }
    return render(request, 'users/dashboard_customer.html', context)


@login_required
def dashboard_seller(request):
    if not request.user.profile.is_seller:
        messages.warning(request, "Please enable Seller mode in your Profile to access the Vendor dashboard.")
        return redirect('users:profile_edit')
        
    my_shops = Shop.objects.filter(owner=request.user).select_related('market', 'category')
    
    # Simple aggregates
    shop_ids = my_shops.values_list('id', flat=True)
    products_count = Product.objects.filter(shop_id__in=shop_ids).count()
    reviews_count = Review.objects.filter(shop_id__in=shop_ids).count()
    
    context = {
        'shops': my_shops,
        'products_count': products_count,
        'reviews_count': reviews_count
    }
    return render(request, 'users/dashboard_seller.html', context)


@staff_member_required
def dashboard_admin(request):
    # Overall statistics
    total_users = UserUpdateForm.Meta.model.objects.count()
    total_markets = Market.objects.count()
    total_shops = Shop.objects.count()
    total_products = Product.objects.count()
    total_reviews = Review.objects.count()
    
    recent_shops = Shop.objects.select_related('market', 'owner').order_by('-id')[:5]
    recent_reviews = Review.objects.select_related('shop', 'user').order_by('-id')[:5]
    
    context = {
        'total_users': total_users,
        'total_markets': total_markets,
        'total_shops': total_shops,
        'total_products': total_products,
        'total_reviews': total_reviews,
        'recent_shops': recent_shops,
        'recent_reviews': recent_reviews
    }
    return render(request, 'users/dashboard_admin.html', context)