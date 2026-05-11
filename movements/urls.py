from django.urls import path
from .views import StockMovementListView,StockMovementExportView


urlpatterns = [
    path('', StockMovementListView.as_view(), name='movement_list'),
    path('export/', StockMovementExportView.as_view(), name='movement_export'),
]