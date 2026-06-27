import os
import sys
import django
from datetime import datetime, time, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baazaarnama.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import Profile
from bazaar.models import Market, Category, Shop, Product, Offer, Wishlist, FavoriteShop
from feedback.models import Review

# Generate mock images using PIL
try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

def create_placeholder_image(path, text, color):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if HAS_PIL:
        # Create a simple banner image
        img = Image.new('RGB', (600, 400), color=color)
        d = ImageDraw.Draw(img)
        # Draw some text simple way (without custom font file to prevent path errors)
        d.text((20, 20), text, fill=(255, 255, 255))
        d.rectangle([(10, 10), (590, 390)], outline=(255, 255, 255), width=2)
        img.save(path)
        print(f"Generated image: {path}")
    else:
        # Create empty file as fallback
        with open(path, 'wb') as f:
            f.write(b'')
        print(f"PIL not installed. Created empty file: {path}")

def main():
    print("Starting database seeding...")
    
    # 1. Create default media folders and placeholder images
    create_placeholder_image('media/profiles/default.jpg', 'Avatar Placeholder', '#8B5E3C')
    create_placeholder_image('media/markets/default.jpg', 'Market Placeholder', '#3B2F2F')
    create_placeholder_image('media/shops/default.jpg', 'Shop Stall Placeholder', '#C49A6C')
    create_placeholder_image('media/products/default.jpg', 'Product Placeholder', '#D8C3A5')
    
    # Specific images for our seeded objects
    create_placeholder_image('media/markets/chandni.jpg', 'CHANDNI CHOWK BAZAAR', '#7D3C1B')
    create_placeholder_image('media/markets/colaba.jpg', 'COLABA CAUSEWAY', '#2C3E50')
    create_placeholder_image('media/markets/johari.jpg', 'JOHARI BAZAAR JAIPUR', '#C0392B')
    
    create_placeholder_image('media/shops/gupta_spices.jpg', 'Gupta Spices', '#D35400')
    create_placeholder_image('media/shops/heritage_textiles.jpg', 'Heritage Textiles', '#8E44AD')
    create_placeholder_image('media/shops/royal_jewels.jpg', 'Royal Jaipur Jewels', '#F1C40F')
    create_placeholder_image('media/shops/delhi_chaat.jpg', 'Delhi Chaat Bhandar', '#27AE60')

    create_placeholder_image('media/products/turmeric.jpg', 'Pure Turmeric Powder', '#F39C12')
    create_placeholder_image('media/products/silk_saree.jpg', 'Banarasi Silk Saree', '#9B59B6')
    create_placeholder_image('media/products/silver_ring.jpg', 'Silver Kundan Ring', '#BDC3C7')
    create_placeholder_image('media/products/samosa.jpg', 'Crispy Potato Samosa', '#D35400')

    # 2. Create Users (Admins, Sellers, Customers)
    # Admin
    admin_user, created = User.objects.get_or_create(username='admin', email='admin@baazaarnama.com')
    if created:
        admin_user.set_password('admin123')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        print("Created admin user: admin / admin123")

    # Seller
    seller_user, created = User.objects.get_or_create(username='seller', email='seller@baazaarnama.com')
    if created:
        seller_user.set_password('seller123')
        seller_user.save()
        profile = seller_user.profile
        profile.phone = '+919988776655'
        profile.is_seller = True
        profile.address = 'Shop 12, Chandni Chowk, Delhi'
        profile.save()
        print("Created seller user: seller / seller123")

    # Customer
    customer_user, created = User.objects.get_or_create(username='customer', email='customer@baazaarnama.com')
    if created:
        customer_user.set_password('customer123')
        customer_user.save()
        profile = customer_user.profile
        profile.phone = '+918877665544'
        profile.address = '42-B, Green Avenue, New Delhi'
        profile.save()
        print("Created customer user: customer / customer123")

    # 3. Create Categories
    categories_data = [
        ('Apparel & Textiles', 'fa-tshirt'),
        ('Spices & Groceries', 'fa-pepper-hot'),
        ('Handicrafts & Jewels', 'fa-gem'),
        ('Local Street Food', 'fa-utensils'),
    ]
    categories = {}
    for name, icon in categories_data:
        cat, _ = Category.objects.get_or_create(name=name, defaults={'icon': icon})
        categories[name] = cat
    print("Seeded Categories.")

    # 4. Create Markets
    markets_data = [
        {
            'name': 'Chandni Chowk',
            'city': 'Delhi',
            'state': 'Delhi',
            'description': 'One of the oldest and busiest markets in Old Delhi, India, famous for spices, clothes, and mouth-watering street food stalls.',
            'cover_image': 'markets/chandni.jpg',
            'latitude': 28.6610,
            'longitude': 77.2281,
            'opening_time': time(9, 0),
            'closing_time': time(21, 30),
        },
        {
            'name': 'Colaba Causeway',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'description': 'A lively commercial street in South Mumbai, renowned for handicrafts, brass items, books, and vintage designer clothes.',
            'cover_image': 'markets/colaba.jpg',
            'latitude': 18.9218,
            'longitude': 72.8315,
            'opening_time': time(10, 0),
            'closing_time': time(22, 0),
        },
        {
            'name': 'Johari Bazaar',
            'city': 'Jaipur',
            'state': 'Rajasthan',
            'description': 'The historical gold jewelry capital of Rajasthan, showcasing rich heritage Kundan designs and handcrafted ornaments.',
            'cover_image': 'markets/johari.jpg',
            'latitude': 26.9196,
            'longitude': 75.8291,
            'opening_time': time(11, 0),
            'closing_time': time(20, 0),
        }
    ]
    markets = {}
    for m_data in markets_data:
        market, _ = Market.objects.get_or_create(name=m_data['name'], defaults=m_data)
        markets[market.name] = market
    print("Seeded Markets.")

    # 5. Create Shops (Chandni Chowk Stalls with custom map positions)
    shops_data = [
        {
            'name': 'Gupta Spice House',
            'owner': seller_user,
            'market': markets['Chandni Chowk'],
            'category': categories['Spices & Groceries'],
            'description': 'Authentic traditional Indian spices, hand-ground masalas, and saffron imported straight from Kashmir valley.',
            'phone': '+919876500123',
            'email': 'guptaspices@example.com',
            'address': 'Stall 4, Spice Lane, Chandni Chowk, Delhi',
            'opening_time': time(9, 0),
            'closing_time': time(20, 0),
            'shop_image': 'shops/gupta_spices.jpg',
            'verified_shop': True,
            'map_x': 2,
            'map_y': 2,
        },
        {
            'name': 'Heritage Banarasi Textiles',
            'owner': seller_user,
            'market': markets['Chandni Chowk'],
            'category': categories['Apparel & Textiles'],
            'description': 'Exquisite collection of premium Banarasi silk sarees, designer lehengas, and hand-woven brocades.',
            'phone': '+919876500124',
            'email': 'heritagetextiles@example.com',
            'address': 'Stall 8, Textile Galleria, Chandni Chowk, Delhi',
            'opening_time': time(10, 0),
            'closing_time': time(21, 0),
            'shop_image': 'shops/heritage_textiles.jpg',
            'verified_shop': True,
            'map_x': 6,
            'map_y': 4,
        },
        {
            'name': 'Royal Jaipur Jewels',
            'owner': seller_user,
            'market': markets['Johari Bazaar'],
            'category': categories['Handicrafts & Jewels'],
            'description': 'Traditional Rajasthani Kundan and Meenakari jewelry, silver ornaments, and customized birthstones.',
            'phone': '+919876500125',
            'email': 'royaljewels@example.com',
            'address': 'Shop 105, Johari Road, Jaipur',
            'opening_time': time(11, 0),
            'closing_time': time(20, 0),
            'shop_image': 'shops/royal_jewels.jpg',
            'verified_shop': True,
            'map_x': 4,
            'map_y': 8,
        },
        {
            'name': 'Delhi Old Chaat Bhandar',
            'owner': seller_user,
            'market': markets['Chandni Chowk'],
            'category': categories['Local Street Food'],
            'description': 'Serving lip-smacking street food like Golgappe, Dahi Bhalle, and hot Kachoris since 1950.',
            'phone': '+919876500126',
            'email': 'olddelhichaat@example.com',
            'address': 'Food Lane, Chandni Chowk, Delhi',
            'opening_time': time(12, 0),
            'closing_time': time(22, 0),
            'shop_image': 'shops/delhi_chaat.jpg',
            'verified_shop': False,
            'map_x': 9,
            'map_y': 6,
        }
    ]
    shops = {}
    for s_data in shops_data:
        shop, _ = Shop.objects.get_or_create(name=s_data['name'], defaults=s_data)
        shops[shop.name] = shop
    print("Seeded Shop Stalls.")

    # 6. Create Products
    products_data = [
        {
            'shop': shops['Gupta Spice House'],
            'name': 'Pure Kashmiri Turmeric',
            'description': '100% natural, hand-ground organic turmeric powder with high curcumin content.',
            'price': 250.00,
            'discount': 10,
            'image': 'products/turmeric.jpg',
            'stock': 120,
            'available': True,
        },
        {
            'shop': shops['Heritage Banarasi Textiles'],
            'name': 'Banarasi Silk Saree',
            'description': 'Pure silk handloom saree with rich golden zari borders and classic motifs. Includes blouse piece.',
            'price': 8500.00,
            'discount': 15,
            'image': 'products/silk_saree.jpg',
            'stock': 15,
            'available': True,
        },
        {
            'shop': shops['Royal Jaipur Jewels'],
            'name': 'Silver Kundan Ring',
            'description': 'Handcrafted sterling silver ring embedded with royal Kundan stones.',
            'price': 1800.00,
            'discount': 5,
            'image': 'products/silver_ring.jpg',
            'stock': 40,
            'available': True,
        },
        {
            'shop': shops['Delhi Old Chaat Bhandar'],
            'name': 'Special Dahi Bhalla plate',
            'description': 'Soft lentil dumplings soaked in sweet yogurt, topped with spicy mint and sweet tamarind chutneys.',
            'price': 80.00,
            'discount': 0,
            'image': 'products/samosa.jpg',
            'stock': 200,
            'available': True,
        }
    ]
    for p_data in products_data:
        Product.objects.get_or_create(name=p_data['name'], defaults=p_data)
    print("Seeded Products.")

    # 7. Create Offers
    offers_data = [
        {
            'shop': shops['Gupta Spice House'],
            'title': 'Monsoon Spice Fest',
            'description': 'Flat 10% off on all Kashmiri whole spices and saffron bags.',
            'discount_percentage': 10,
            'valid_till': datetime.now().date() + timedelta(days=30),
        },
        {
            'shop': shops['Heritage Banarasi Textiles'],
            'title': 'Wedding Season Special',
            'description': 'Get up to 15% discount on heritage Banarasi bridal sarees.',
            'discount_percentage': 15,
            'valid_till': datetime.now().date() + timedelta(days=60),
        }
    ]
    for o_data in offers_data:
        Offer.objects.get_or_create(title=o_data['title'], defaults=o_data)
    print("Seeded Special Offers.")

    # 8. Create Reviews
    reviews_data = [
        {
            'user': customer_user,
            'shop': shops['Gupta Spice House'],
            'rating': 5,
            'review': 'Best spices in town! The aroma of Kashmir Saffron is incredible. Fully recommended.',
        },
        {
            'user': customer_user,
            'shop': shops['Heritage Banarasi Textiles'],
            'rating': 4,
            'review': 'Beautiful sarees collection! Helpful vendor staff, guided us directly using walking directions.',
        }
    ]
    for r_data in reviews_data:
        Review.objects.get_or_create(user=r_data['user'], shop=r_data['shop'], defaults=r_data)
    print("Seeded Customer Reviews.")

    print("\nDatabase seeding completed successfully!")
    print("Use these test accounts to log in:")
    print("  - Customer: customer / customer123")
    print("  - Seller/Vendor: seller / seller123")
    print("  - Superuser/Admin: admin / admin123")

if __name__ == '__main__':
    main()
