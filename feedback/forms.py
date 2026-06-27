from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(
        min_value=1, 
        max_value=5, 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Rate 1 to 5 stars'})
    )
    review = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write your shopping experience...'})
    )

    class Meta:
        model = Review
        fields = ['rating', 'review']
