from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from bazaar.models import Shop
from .forms import ReviewForm
from .models import Review

@login_required
def add_review(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            # Check if user has already reviewed this shop
            existing_review = Review.objects.filter(user=request.user, shop=shop).first()
            if existing_review:
                # Update existing review
                existing_review.rating = form.cleaned_data['rating']
                existing_review.review = form.cleaned_data['review']
                existing_review.save()
                messages.success(request, f"Your review for {shop.name} has been updated!")
            else:
                # Create new review
                review = form.save(commit=False)
                review.user = request.user
                review.shop = shop
                review.save()
                messages.success(request, f"Your review for {shop.name} has been submitted successfully!")
        else:
            messages.error(request, "Invalid review form. Rating must be 1 to 5.")
    return redirect('bazaar:shop_detail', pk=shop_id)
