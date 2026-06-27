/*
   BAAZAARNAMA - DESI MARKET, GONE DIGITAL
   Interactive AI Bazaar Maps JS Engine
*/

class BazaarMapEngine {
    constructor(marketId, mapDataUrl, directionsUrl) {
        this.marketId = marketId;
        this.mapDataUrl = mapDataUrl;
        this.directionsUrl = directionsUrl;
        
        this.marketData = null;
        this.shops = [];
        this.activeStartShop = 'entrance';
        this.activeEndShop = null;
        this.geoMap = null;
        this.geoMarkers = [];

        // Grid Constants (matching 10x10 virtual layout)
        this.gridSize = 10;
        this.cellSize = 50; // pixels
        this.padding = 10;  // SVG bounds padding
    }

    init() {
        this.loadMapData();
        this.setupEventHandlers();
    }

    loadMapData() {
        fetch(this.mapDataUrl)
            .then(res => res.json())
            .then(data => {
                this.marketData = data.market;
                this.shops = data.shops;
                
                // Render both views
                this.renderVirtualMap();
                this.initGeographicMap();
                this.populateShopSelects();
                this.findNearestShopsGeolocation();
            })
            .catch(err => console.error("Error loading map coordinates:", err));
    }

    renderVirtualMap() {
        const svg = document.getElementById('virtual-bazaar-svg');
        if (!svg) return;

        // Clear previous grid elements (except definitions)
        const pathLine = document.getElementById('route-path-line');
        svg.innerHTML = '';
        if (pathLine) svg.appendChild(pathLine); // Keep path line container

        const width = this.gridSize * this.cellSize;
        const height = this.gridSize * this.cellSize;
        svg.setAttribute('width', width);
        svg.setAttribute('height', height);

        // 1. Draw grid floor background cells
        for (let x = 1; x <= this.gridSize; x++) {
            for (let y = 1; y <= this.gridSize; y++) {
                const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
                rect.setAttribute('x', (x - 1) * this.cellSize);
                rect.setAttribute('y', (y - 1) * this.cellSize);
                rect.setAttribute('width', this.cellSize);
                rect.setAttribute('height', this.cellSize);
                
                // Color walkways beige, stalls light beige-gray
                if (x === 3 || x === 7 || y === 3 || y === 7) {
                    rect.setAttribute('fill', '#eedfc8'); // Walkway
                    rect.setAttribute('stroke', '#e4d0b2');
                } else {
                    rect.setAttribute('fill', '#Faf8f5'); // Stall area
                    rect.setAttribute('stroke', '#f3edd8');
                }
                rect.setAttribute('stroke-width', '0.5');
                svg.appendChild(rect);
            }
        }

        // 2. Draw Entry banner at the bottom (x=5, y=10)
        const entryText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        entryText.setAttribute('x', 4.5 * this.cellSize);
        entryText.setAttribute('y', 9.8 * this.cellSize);
        entryText.setAttribute('fill', '#8B5E3C');
        entryText.setAttribute('font-size', '10px');
        entryText.setAttribute('font-weight', 'bold');
        entryText.textContent = "▲ ENTRANCE";
        svg.appendChild(entryText);

        // 3. Draw Shop Stalls
        this.shops.forEach(shop => {
            const stallG = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            stallG.setAttribute('class', 'map-stall');
            stallG.setAttribute('id', `stall-${shop.id}`);
            stallG.setAttribute('data-id', shop.id);
            stallG.setAttribute('data-category', shop.category);
            stallG.setAttribute('data-name', shop.name.toLowerCase());

            const px = (shop.x - 1) * this.cellSize + 4;
            const py = (shop.y - 1) * this.cellSize + 4;
            const size = this.cellSize - 8;

            // Rectangle stall box
            const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            rect.setAttribute('x', px);
            rect.setAttribute('y', py);
            rect.setAttribute('width', size);
            rect.setAttribute('height', size);
            rect.setAttribute('rx', '8');
            rect.setAttribute('fill', shop.verified ? '#F5F0EA' : '#fff');
            rect.setAttribute('stroke', shop.verified ? '#8B5E3C' : '#D8C3A5');
            rect.setAttribute('stroke-width', '1.5');
            stallG.appendChild(rect);

            // Icon symbol representation
            const textIcon = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            textIcon.setAttribute('x', px + size / 2);
            textIcon.setAttribute('y', py + size / 2 + 5);
            textIcon.setAttribute('text-anchor', 'middle');
            textIcon.setAttribute('font-size', '12px');
            textIcon.setAttribute('fill', '#3B2F2F');
            textIcon.setAttribute('font-weight', 'bold');
            
            // Abbreviate shop name for display
            textIcon.textContent = shop.name.substring(0, 3).toUpperCase();
            stallG.appendChild(textIcon);

            // Click listener for details popup
            stallG.addEventListener('click', () => {
                this.selectShop(shop);
            });

            svg.appendChild(stallG);
        });

        // 4. Create paths lines overlays
        const pathGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        pathGroup.setAttribute('id', 'route-path-overlay');
        svg.appendChild(pathGroup);
    }

    initGeographicMap() {
        const container = document.getElementById('geo-map-container');
        if (!container) return;

        const lat = this.marketData.latitude || 28.6139;
        const lng = this.marketData.longitude || 77.2090;

        // Initialize Leaflet map
        this.geoMap = L.map('geo-map-container').setView([lat, lng], 16);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.geoMap);

        // Add Market center marker
        const marketIcon = L.divIcon({
            html: '<i class="fas fa-shopping-basket fa-2x" style="color: #8B5E3C;"></i>',
            iconSize: [30, 30],
            className: 'custom-leaflet-icon'
        });
        
        L.marker([lat, lng], {icon: marketIcon})
            .addTo(this.geoMap)
            .bindPopup(`<b>${this.marketData.name}</b><br>Central Landmark`)
            .openPopup();

        // Place markers for all shops inside the market
        this.shops.forEach(shop => {
            // Assign dummy coordinates around market center if blank
            const offsetLat = (Math.random() - 0.5) * 0.003;
            const offsetLng = (Math.random() - 0.5) * 0.003;
            const shopLat = lat + offsetLat;
            const shopLng = lng + offsetLng;

            const shopIcon = L.divIcon({
                html: `<i class="fas fa-store" style="color: ${shop.verified ? '#C49A6C' : '#3B2F2F'}; font-size: 16px;"></i>`,
                iconSize: [20, 20],
                className: 'custom-leaflet-icon'
            });

            const marker = L.marker([shopLat, shopLng], {icon: shopIcon})
                .addTo(this.geoMap)
                .bindPopup(`
                    <div style="font-family: 'Poppins', sans-serif;">
                        <h6 style="margin: 0; font-weight: bold; color: #8B5E3C;">${shop.name}</h6>
                        <small class="text-muted">${shop.category}</small><br>
                        <a href="/shop/${shop.id}/" class="btn btn-sm btn-dark text-white py-0 px-2 mt-1" style="font-size: 10px;">Visit Stall</a>
                    </div>
                `);
            this.geoMarkers.push(marker);
        });
    }

    populateShopSelects() {
        const startSelect = document.getElementById('route-start');
        const endSelect = document.getElementById('route-end');
        if (!startSelect || !endSelect) return;

        startSelect.innerHTML = '<option value="entrance">Market Main Entrance</option>';
        endSelect.innerHTML = '<option value="" disabled selected>Choose shop stall...</option>';

        this.shops.forEach(shop => {
            const opt = document.createElement('option');
            opt.value = shop.id;
            opt.textContent = `${shop.name} (${shop.category})`;
            
            startSelect.appendChild(opt.cloneNode(true));
            endSelect.appendChild(opt);
        });
    }

    selectShop(shop) {
        // Highlight active SVG stall
        document.querySelectorAll('.map-stall').forEach(s => s.classList.remove('active'));
        const activeStall = document.getElementById(`stall-${shop.id}`);
        if (activeStall) activeStall.classList.add('active');

        // Populate side panel details
        const detailsContainer = document.getElementById('shop-info-card');
        if (detailsContainer) {
            detailsContainer.innerHTML = `
                <div class="map-info-popup bg-light p-3 rounded shadow-sm">
                    <img src="${shop.image}" class="img-fluid rounded mb-2" style="width: 100%; height: 120px; object-fit: cover;">
                    <h5 class="mb-1 text-primary">${shop.name}</h5>
                    <p class="text-muted mb-1 small"><i class="fas fa-tag"></i> ${shop.category}</p>
                    <div class="text-warning mb-2">
                        <i class="fas fa-star"></i> <span class="text-dark font-weight-bold">${shop.rating || '0.0'}</span>
                    </div>
                    <div class="d-grid gap-2">
                        <a href="/shop/${shop.id}/" class="btn btn-sm btn-premium text-white">Visit Online Stall</a>
                        <button class="btn btn-sm btn-outline-dark" onclick="window.mapEngine.setRouteDestination(${shop.id})">
                            <i class="fas fa-walking"></i> Directions Here
                        </button>
                    </div>
                </div>
            `;
        }

        // Set route endpoint selector automatically
        const endSelect = document.getElementById('route-end');
        if (endSelect) {
            endSelect.value = shop.id;
            this.activeEndShop = shop.id;
        }
    }

    setRouteDestination(shopId) {
        this.activeEndShop = shopId;
        this.calculateDirections();
    }

    calculateDirections() {
        const start = document.getElementById('route-start')?.value || 'entrance';
        const end = this.activeEndShop;
        if (!end) return;

        const url = `${this.directionsUrl}?start=${start}&end=${end}`;
        
        fetch(url)
            .then(res => res.json())
            .then(data => {
                this.drawPath(data.path);
                this.renderInstructions(data.instructions);
            })
            .catch(err => console.error("Error routing walk path:", err));
    }

    drawPath(path) {
        const svg = document.getElementById('virtual-bazaar-svg');
        const overlay = document.getElementById('route-path-overlay');
        if (!svg || !overlay) return;

        // Clear previous path lines
        overlay.innerHTML = '';

        if (path.length < 2) return;

        // Create the SVG path string
        let pathD = "";
        path.forEach((pt, idx) => {
            const px = (pt[0] - 1) * this.cellSize + this.cellSize / 2;
            const py = (pt[1] - 1) * this.cellSize + this.cellSize / 2;
            
            if (idx === 0) {
                pathD += `M ${px} ${py}`;
            } else {
                pathD += ` L ${px} ${py}`;
            }
        });

        // Draw glowing background route path
        const pathLineGlow = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        pathLineGlow.setAttribute('d', pathD);
        pathLineGlow.setAttribute('fill', 'none');
        pathLineGlow.setAttribute('stroke', 'rgba(139, 94, 60, 0.25)');
        pathLineGlow.setAttribute('stroke-width', '10px');
        pathLineGlow.setAttribute('stroke-linecap', 'round');
        pathLineGlow.setAttribute('stroke-linejoin', 'round');
        overlay.appendChild(pathLineGlow);

        // Draw animated main path line
        const pathLine = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        pathLine.setAttribute('class', 'walking-route-path');
        pathLine.setAttribute('d', pathD);
        pathLine.setAttribute('fill', 'none');
        pathLine.setAttribute('stroke', '#8B5E3C');
        pathLine.setAttribute('stroke-width', '4px');
        pathLine.setAttribute('stroke-linecap', 'round');
        pathLine.setAttribute('stroke-linejoin', 'round');
        overlay.appendChild(pathLine);

        // Draw starting pin
        const startPt = path[0];
        const startCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        startCircle.setAttribute('cx', (startPt[0] - 1) * this.cellSize + this.cellSize / 2);
        startCircle.setAttribute('cy', (startPt[1] - 1) * this.cellSize + this.cellSize / 2);
        startCircle.setAttribute('r', '6');
        startCircle.setAttribute('fill', '#2E7D32'); // green pin for start
        overlay.appendChild(startCircle);

        // Draw end pin
        const endPt = path[path.length - 1];
        const endCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        endCircle.setAttribute('cx', (endPt[0] - 1) * this.cellSize + this.cellSize / 2);
        endCircle.setAttribute('cy', (endPt[1] - 1) * this.cellSize + this.cellSize / 2);
        endCircle.setAttribute('r', '6');
        endCircle.setAttribute('fill', '#C62828'); // red pin for end
        overlay.appendChild(endCircle);
    }

    renderInstructions(instructions) {
        const container = document.getElementById('walk-directions-steps');
        if (!container) return;

        container.innerHTML = '';
        instructions.forEach(step => {
            const li = document.createElement('li');
            li.className = 'list-group-item d-flex align-items-center bg-white border-0 py-2 border-bottom';
            li.innerHTML = `
                <span class="badge bg-secondary me-3" style="background-color: var(--primary) !important;"><i class="fas fa-directions"></i></span>
                <span class="small font-weight-medium text-dark">${step}</span>
            `;
            container.appendChild(li);
        });
    }

    setupEventHandlers() {
        // Shop Search inside Map
        const searchInput = document.getElementById('map-shop-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                const query = e.target.value.toLowerCase().trim();
                const stalls = document.querySelectorAll('.map-stall');

                stalls.forEach(stall => {
                    const shopName = stall.getAttribute('data-name');
                    if (query === '' || shopName.includes(query)) {
                        stall.style.opacity = '1';
                        stall.style.pointerEvents = 'auto';
                    } else {
                        stall.style.opacity = '0.2';
                        stall.style.pointerEvents = 'none';
                    }
                });
            });
        }

        // Category filtering inside Map
        const catSelect = document.getElementById('map-category-filter');
        if (catSelect) {
            catSelect.addEventListener('change', (e) => {
                const selectedCat = e.target.value;
                const stalls = document.querySelectorAll('.map-stall');

                stalls.forEach(stall => {
                    const stallCat = stall.getAttribute('data-category');
                    if (selectedCat === 'all' || stallCat === selectedCat) {
                        stall.style.opacity = '1';
                        stall.style.pointerEvents = 'auto';
                    } else {
                        stall.style.opacity = '0.2';
                        stall.style.pointerEvents = 'none';
                    }
                });
            });
        }

        // Routing selectors trigger paths
        document.getElementById('route-start')?.addEventListener('change', () => this.calculateDirections());
        document.getElementById('route-end')?.addEventListener('change', (e) => {
            this.activeEndShop = e.target.value;
            this.calculateDirections();
            // Highlight selected shop in virtual grid
            const selectedShop = this.shops.find(s => s.id == e.target.value);
            if (selectedShop) {
                this.selectShop(selectedShop);
            }
        });
    }

    findNearestShopsGeolocation() {
        const container = document.getElementById('nearest-shops-output');
        if (!container) return;

        if (!navigator.geolocation) {
            container.innerHTML = '<div class="alert alert-warning py-2 mb-0">Geolocation is not supported by your browser.</div>';
            return;
        }

        // Click handler to run geolocation
        const triggerBtn = document.getElementById('trigger-gps-locator');
        if (triggerBtn) {
            triggerBtn.addEventListener('click', () => {
                container.innerHTML = '<div class="spinner-border spinner-border-sm text-primary" role="status"></div> Reading location...';
                
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        const userLat = position.coords.latitude;
                        const userLng = position.coords.longitude;
                        
                        // Calculate distance to central market landmark, and to each shop
                        const centralDist = this.calculateHaversineDistance(
                            userLat, userLng, 
                            parseFloat(this.marketData.latitude) || 28.6139, 
                            parseFloat(this.marketData.longitude) || 77.2090
                        );
                        
                        // Calculate shop distances
                        const shopsWithDistance = this.shops.map(shop => {
                            // Simulated random offset around market center for demo shops
                            const offsetLat = (Math.random() - 0.5) * 0.003;
                            const offsetLng = (Math.random() - 0.5) * 0.003;
                            const shopLat = (parseFloat(this.marketData.latitude) || 28.6139) + offsetLat;
                            const shopLng = (parseFloat(this.marketData.longitude) || 77.2090) + offsetLng;
                            
                            const dist = this.calculateHaversineDistance(userLat, userLng, shopLat, shopLng);
                            return { ...shop, distance: dist };
                        });

                        // Sort by nearest distance
                        shopsWithDistance.sort((a, b) => a.distance - b.distance);

                        container.innerHTML = `
                            <div class="alert alert-success py-2 mb-3 small">
                                <i class="fas fa-map-marker-alt"></i> Found! You are <b>${(centralDist * 1000).toFixed(0)}m</b> from Market Center.
                            </div>
                            <h6 class="mb-2 font-weight-bold">Nearest Shop Stalls:</h6>
                            <div class="list-group">
                        `;
                        
                        // Show top 3 nearest shops
                        shopsWithDistance.slice(0, 3).forEach(shop => {
                            const btn = document.createElement('button');
                            btn.className = 'list-group-item list-group-item-action border-0 px-2 py-2 d-flex justify-content-between align-items-center border-bottom bg-light';
                            btn.innerHTML = `
                                <div>
                                    <div class="font-weight-bold text-primary text-start" style="font-size:13px;">${shop.name}</div>
                                    <small class="text-muted"><i class="fas fa-tag"></i> ${shop.category}</small>
                                </div>
                                <span class="badge bg-dark rounded-pill" style="font-size: 10px;">${(shop.distance * 1000).toFixed(0)}m away</span>
                            `;
                            btn.addEventListener('click', () => {
                                this.selectShop(shop);
                            });
                            container.appendChild(btn);
                        });
                    },
                    (error) => {
                        container.innerHTML = `<div class="alert alert-danger py-2 mb-0 small">Location Access Denied.</div>`;
                    }
                );
            });
        }
    }

    calculateHaversineDistance(lat1, lon1, lat2, lon2) {
        const R = 6371; // Earth radius in km
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLon = (lon2 - lon1) * Math.PI / 180;
        const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                  Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                  Math.sin(dLon / 2) * Math.sin(dLon / 2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        return R * c; // distance in km
    }
}

// Bind to window to allow instantiating in templates
window.BazaarMapEngine = BazaarMapEngine;
