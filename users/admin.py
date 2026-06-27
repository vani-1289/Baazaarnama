from django.contrib import admin
from django.utils.html import format_html
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'is_seller', 'image_preview']
    list_filter = ['is_seller']
    search_fields = ['user__username', 'user__email', 'phone', 'address']
    list_per_page = 20

    def image_preview(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;" />', obj.profile_image.url)
        return "No Image"
    image_preview.short_description = 'Avatar Preview'