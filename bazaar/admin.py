from django.contrib import admin
from django.utils.html import format_html
from .models import Market, Category, Shop, Product, Offer, Wishlist, FavoriteShop

@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'state', 'opening_time', 'closing_time', 'image_preview']
    search_fields = ['name', 'city', 'state', 'description']
    list_filter = ['city', 'state']
    list_per_page = 15

    def image_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" style="width: 60px; height: 40px; border-radius: 4px; object-fit: cover;" />', obj.cover_image.url)
        return "No Image"
    image_preview.short_description = 'Cover Preview'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon_preview']
    search_fields = ['name']
    
    def icon_preview(self, obj):
        return format_html('<i class="fas {}" style="font-size: 18px; color: #8B5E3C;"></i> &nbsp; {}', obj.icon, obj.icon)
    icon_preview.short_description = 'Icon Symbol'


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'market', 'category', 'verified_shop', 'image_preview']
    list_filter = ['verified_shop', 'market', 'category']
    search_fields = ['name', 'owner__username', 'market__name', 'description']
    actions = ['verify_shops', 'unverify_shops']
    list_per_page = 20

    def image_preview(self, obj):
        if obj.shop_image:
            return format_html('<img src="{}" style="width: 50px; height: 40px; border-radius: 4px; object-fit: cover;" />', obj.shop_image.url)
        return "No Image"
    image_preview.short_description = 'Shop Photo'

    def verify_shops(self, request, queryset):
        queryset.update(verified_shop=True)
    verify_shops.short_description = "Verify selected shops"

    def unverify_shops(self, request, queryset):
        queryset.update(verified_shop=False)
    unverify_shops.short_description = "Revoke verification"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'shop', 'price', 'discount', 'discounted_price', 'stock', 'available', 'image_preview']
    list_filter = ['available', 'shop__market', 'shop']
    search_fields = ['name', 'shop__name', 'description']
    list_editable = ['price', 'discount', 'stock', 'available']
    list_per_page = 25

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 40px; border-radius: 4px; object-fit: cover;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Product Photo'


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['title', 'shop', 'discount_percentage', 'valid_till']
    list_filter = ['valid_till', 'shop']
    search_fields = ['title', 'shop__name', 'description']
    list_per_page = 20


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created_at']
    search_fields = ['user__username', 'product__name']


@admin.register(FavoriteShop)
class FavoriteShopAdmin(admin.ModelAdmin):
    list_display = ['user', 'shop', 'created_at']
    search_fields = ['user__username', 'shop__name']
