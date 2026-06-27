from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    path('add/<int:shop_id>/', views.add_review, name='add_review'),
]
