from django.urls import path
from .views import (
    ProductListView, ProductDetailView,
    ProductCreateView, ProductUpdateView, ProductDeleteView
)


urlpatterns = [
    path('', ProductListView.as_view(), name='products_list'),
    path('<int:pk>/', ProductDetailView.as_view(), name='products_detail'),
    path('create/', ProductCreateView.as_view(), name='products_create'),
    path('<int:pk>/edit/', ProductUpdateView.as_view(), name='products_update'),
    path('<int:pk>/delete/', ProductDeleteView.as_view(), name='products_delete'),
]