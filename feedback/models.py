from django.db import models
from django.contrib.auth.models import User
from bazaar.models import Shop

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(default=5)
    review = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s review on {self.shop.name} ({self.rating} stars)"
