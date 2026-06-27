from django.urls import path
from . import views

app_name = 'ai_maps'

urlpatterns = [
    path('<int:market_id>/', views.market_map, name='market_map'),
    path('<int:market_id>/data/', views.market_map_data, name='market_map_data'),
    path('<int:market_id>/directions/', views.walking_directions, name='walking_directions'),
]
