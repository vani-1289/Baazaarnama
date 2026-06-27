from django.urls import path
from . import views

app_name = 'bazaar'

urlpatterns = [
    # General Browsing
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('markets/', views.market_list, name='market_list'),
    path('market/<int:pk>/', views.market_detail, name='market_detail'),
    path('shops/', views.shop_list, name='shop_list'),
    path('shop/<int:pk>/', views.shop_detail, name='shop_detail'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    
    # Wishlist & Favorites
    path('wishlist-toggle/<int:pk>/', views.wishlist_toggle, name='wishlist_toggle'),
    path('favorite-toggle/<int:pk>/', views.favorite_toggle, name='favorite_toggle'),
    
    # Seller Operations - Shops
    path('shop/add/', views.add_shop, name='add_shop'),
    path('shop/<int:pk>/edit/', views.edit_shop, name='edit_shop'),
    
    # Seller Operations - Products
    path('shop/<int:shop_id>/product/add/', views.add_product, name='add_product'),
    path('product/<int:pk>/edit/', views.edit_product, name='edit_product'),
    path('product/<int:pk>/delete/', views.delete_product, name='delete_product'),
    
    # Seller Operations - Offers
    path('shop/<int:shop_id>/offer/add/', views.add_offer, name='add_offer'),
    path('offer/<int:pk>/edit/', views.edit_offer, name='edit_offer'),
    path('offer/<int:pk>/delete/', views.delete_offer, name='delete_offer'),
]