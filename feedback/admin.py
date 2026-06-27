from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'shop', 'rating', 'created_date']
    list_filter = ['rating', 'created_date']
    search_fields = ['user__username', 'shop__name', 'review']
    list_per_page = 20
