# BAAZAARNAMA — Desi Market, Gone Digital

BAAZAARNAMA is a premium, production-quality Django web application that brings India's traditional local markets to people's fingertips. The application promotes offline shopping and digitally empowers local vendors by providing online stall catalogs, active deal flyers, and interactive walk-path mapping tools.

## Key Features

1. **User Authentication & Profiles**:
   - Secure customer/seller registration, login, logout, password change, and password reset flows.
   - Dynamic profile edits (avatar uploads, address entries, contact phone) supported by automatic profile generation via Django signals.
2. **Core Marketplace Directory**:
   - Advanced multi-criteria search by Market name, city, shop name, categories, or items.
   - Browse trending bazaars, featured shops, active promotion deals, and popular categories.
   - Dynamic dynamic price computing with support for percentage discounts.
3. **Walkthrough AI Maps Module**:
   - Dual Map interface: 
     - **Virtual Bazaar Layout**: Styled SVG grid layout representing vendor stalls. Walkways are marked beige, and shops act as grid blocks.
     - **Geographic View**: Free OpenStreetMap layers powered by Leaflet.js centered on the market center, displaying custom pins for shops.
   - Clickable shop stalls with popups displaying reviews, category, and online shop link.
   - Walking directions: computes paths avoiding stalls along walkways using Python-side routing (BFS algorithm) and renders animated path guidelines on the SVG grid.
   - Nearest Stall Finder: locates the user's relative distance to stalls using HTML5 Geolocation.
4. **Reviews & Rating Engine**:
   - Authentic review logging, allowing customers to post comments and 1-5 star ratings (updating their feedback on repeat submissions).
   - Dynamic average ratings calculated on shop cards and market summary headers.
5. **Customer & Seller Consoles**:
   - Customer panel displaying wishlists, favorite stores, and review history logs.
   - Seller workspace supporting shops registration, product additions, discount offer creations, and inventory updates.
   - Fully customized Django Admin dashboard displaying thumbnails, list filtering, and bulk admin verify actions.

---

## Technical Stack
- **Backend**: Django 5+, Python 3.13+, SQLite.
- **Frontend**: HTML5, Vanilla CSS3 (custom variables, glassmorphism, responsive grids), Bootstrap 5, Javascript, FontAwesome 6, AOS (Animate on Scroll).
- **Libraries**: Leaflet.js (GIS mapping), Pillow (Image manipulation).

---

## Installation & Setup

1. **Clone/Navigate to Project Directory**:
   ```powershell
   cd d:\Baazaarnama
   ```

2. **Verify Dependencies Installation**:
   Ensure Pillow and Django are installed in the local virtual environment.
   ```powershell
   env\Scripts\python.exe -m pip install -r requirements.txt
   ```

3. **Database Schema & Migrations**:
   Run migration commands to build SQLite tables.
   ```powershell
   env\Scripts\python.exe manage.py migrate
   ```

4. **Seed Database Mock Data**:
   Populate categories, markets, shop coordinates, and products along with test profile accounts.
   ```powershell
   env\Scripts\python.exe seed_db.py
   ```

5. **Start Dev Server**:
   Launch the Django server.
   ```powershell
   env\Scripts\python.exe manage.py runserver
   ```
   Access the marketplace at `http://127.0.0.1:8000/`.

---

## Seed Accounts (Credentials)

- **Staff Administrator**: `admin` / `admin123`
- **Seller/Vendor**: `seller` / `seller123`
- **Customer**: `customer` / `customer123`

---

## Verification & Automated Tests
To run the automated test suite checking views, routing, search operations, and model calculations:
```powershell
env\Scripts\python.exe manage.py test
```
