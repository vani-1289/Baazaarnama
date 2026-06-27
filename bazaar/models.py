from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg

class Market(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='markets/', default='markets/default.jpg')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}, {self.city}"

    @property
    def average_rating(self):
        # Calculate avg rating from reviews of all shops in this market
        ratings = []
        for shop in self.shops.all():
            avg = shop.average_rating
            if avg > 0:
                ratings.append(avg)
        return round(sum(ratings) / len(ratings), 1) if ratings else 0.0


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    icon = models.CharField(max_length=50, default='fa-shopping-basket', help_text="FontAwesome class name, e.g., 'fa-utensils'")

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Shop(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shops')
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='shops')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='shops')
    description = models.TextField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    google_map_link = models.URLField(max_length=500, blank=True)
    shop_image = models.ImageField(upload_to='shops/', default='shops/default.jpg')
    verified_shop = models.BooleanField(default=False)
    
    # Grid coordinates for simulated interactive SVG bazaar map
    map_x = models.IntegerField(default=1, help_text="Virtual map horizontal coordinate (1-10)")
    map_y = models.IntegerField(default=1, help_text="Virtual map vertical coordinate (1-10)")

    def __str__(self):
        return f"{self.name} ({self.market.name})"

    @property
    def average_rating(self):
        # Calculate rating dynamically from associated feedback reviews
        reviews = self.reviews.all()
        if reviews.exists():
            return round(reviews.aggregate(Avg('rating'))['rating__avg'], 1)
        return 0.0


class Product(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.IntegerField(default=0, help_text="Discount percentage (0-100)")
    image = models.ImageField(upload_to='products/', default='products/default.jpg')
    stock = models.IntegerField(default=0)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @property
    def discounted_price(self):
        if self.discount > 0:
            from decimal import Decimal
            price_dec = Decimal(str(self.price))
            return round(price_dec * Decimal(100 - self.discount) / Decimal(100), 2)
        return self.price


class Offer(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='offers')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    discount_percentage = models.IntegerField(default=0)
    valid_till = models.DateField()

    def __str__(self):
        return f"{self.title} - {self.shop.name}"


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class FavoriteShop(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_shops')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'shop')

    def __str__(self):
        return f"{self.user.username} - {self.shop.name}"
