from django import forms
from .models import Shop, Product, Offer

class ShopForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = [
            'name', 'market', 'category', 'description', 'phone', 
            'email', 'address', 'opening_time', 'closing_time', 
            'google_map_link', 'shop_image', 'map_x', 'map_y'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'address': forms.Textarea(attrs={'rows': 2}),
            'opening_time': forms.TimeInput(attrs={'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'type': 'time'}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'discount', 'image', 'stock', 'available']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ['title', 'description', 'discount_percentage', 'valid_till']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'valid_till': forms.DateInput(attrs={'type': 'date'}),
        }
