from django.urls import path
from .views import StockMovementListView


urlpatterns = [
    path('', StockMovementListView.as_view(), name='movement_list'),
]