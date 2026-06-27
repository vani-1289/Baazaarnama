/*
   BAAZAARNAMA - DESI MARKET, GONE DIGITAL
   Core Main JS Interactions
*/

document.addEventListener('DOMContentLoaded', function() {
    // 1. Scroll-aware sticky transparent navbar transitions
    const navbar = document.querySelector('.navbar-custom');
    if (navbar && navbar.classList.contains('navbar-transparent')) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.remove('navbar-transparent');
            } else {
                navbar.classList.add('navbar-transparent');
            }
        });
    }

    // 2. Automatically fade out Django message alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            // Bootstrap fade class helper
            alert.classList.add('fade');
            setTimeout(function() {
                alert.remove();
            }, 500);
        }, 5000);
    });

    // 3. AJAX Wishlist Toggling
    const wishlistButtons = document.querySelectorAll('.btn-wishlist-toggle');
    wishlistButtons.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const url = this.getAttribute('href') || this.getAttribute('data-url');
            if (!url) return;

            const icon = this.querySelector('i');
            const textSpan = this.querySelector('.btn-text');

            fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.added) {
                    icon.classList.remove('far');
                    icon.classList.add('fas');
                    icon.style.color = '#C62828'; // Red filled heart
                    if (textSpan) textSpan.innerText = 'Wishlisted';
                    showToast('Product added to Wishlist!', 'success');
                } else {
                    icon.classList.remove('fas');
                    icon.classList.add('far');
                    icon.style.color = ''; // standard color
                    if (textSpan) textSpan.innerText = 'Add to Wishlist';
                    showToast('Product removed from Wishlist.', 'info');
                }
            })
            .catch(error => {
                console.error('Error toggling wishlist:', error);
                // Fallback to standard redirect if user is not logged in or error occurs
                window.location.href = url;
            });
        });
    });

    // 4. AJAX Favorite Shop Toggling
    const favoriteButtons = document.querySelectorAll('.btn-favorite-toggle');
    favoriteButtons.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const url = this.getAttribute('href') || this.getAttribute('data-url');
            if (!url) return;

            const icon = this.querySelector('i');
            const textSpan = this.querySelector('.btn-text');

            fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.added) {
                    icon.classList.remove('far');
                    icon.classList.add('fas');
                    icon.style.color = '#F39C12'; // Amber filled star
                    if (textSpan) textSpan.innerText = 'Favourited';
                    showToast('Shop added to Favorites!', 'success');
                } else {
                    icon.classList.remove('fas');
                    icon.classList.add('far');
                    icon.style.color = '';
                    if (textSpan) textSpan.innerText = 'Add to Favourites';
                    showToast('Shop removed from Favorites.', 'info');
                }
            })
            .catch(error => {
                console.error('Error toggling favorites:', error);
                window.location.href = url;
            });
        });
    });

    // Helper functions
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function showToast(message, type = 'info') {
        // Create toast notification dynamically if none exists
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.style.position = 'fixed';
            container.style.bottom = '20px';
            container.style.right = '20px';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : 'dark'} border-0 show m-2`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-info-circle'} me-2"></i> ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;

        container.appendChild(toast);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3500);
    }
});
