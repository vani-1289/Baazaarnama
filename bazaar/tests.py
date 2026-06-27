from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import time, date
from .models import Market, Category, Shop, Product, Offer

class BazaarTestCase(TestCase):
    def setUp(self):
        # Setup Client
        self.client = Client()
        
        # Seed test categories
        self.category = Category.objects.create(name="Spices", icon="fa-pepper-hot")
        
        # Seed test market
        self.market = Market.objects.create(
            name="Chandni Chowk",
            city="Delhi",
            state="Delhi",
            description="Historic market in Delhi.",
            opening_time=time(9, 0),
            closing_time=time(20, 0)
        )
        
        # Seed test user
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        
        # Seed test shop
        self.shop = Shop.objects.create(
            name="Gupta Spices",
            owner=self.user,
            market=self.market,
            category=self.category,
            description="Premium Spices.",
            opening_time=time(9, 0),
            closing_time=time(19, 0),
            verified_shop=True
        )
        
        # Seed product
        self.product = Product.objects.create(
            shop=self.shop,
            name="Kashmiri Turmeric",
            description="Curcumin rich spice.",
            price=Decimal('150.00'),
            discount=10,
            stock=50,
            available=True
        )

    def test_home_view(self):
        """Verify the homepage load contains trending markets and statistics."""
        response = self.client.get(reverse('bazaar:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Chandni Chowk")
        self.assertContains(response, "Gupta Spices")

    def test_search_view(self):
        """Verify searching by shop, city, or product names returns correct matches."""
        # 1. Search for Spices
        response = self.client.get(reverse('bazaar:search') + "?q=Spices")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Gupta Spices")

        # 2. Search for non-existent keyword
        response = self.client.get(reverse('bazaar:search') + "?q=nonexistent")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Gupta Spices")

    def test_market_detail_view(self):
        """Verify market detail loads information and lists active stalls."""
        response = self.client.get(reverse('bazaar:market_detail', args=[self.market.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Chandni Chowk")
        self.assertContains(response, "Gupta Spices")

    def test_product_detail_view(self):
        """Verify product detail load and discount price computation."""
        response = self.client.get(reverse('bazaar:product_detail', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kashmiri Turmeric")
        # Assert discounted price is correctly calculated (150 * 0.9 = 135)
        self.assertEqual(self.product.discounted_price, Decimal('135.00'))
