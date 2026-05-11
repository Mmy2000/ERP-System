from django.urls import path
from .views import (
    CustomerListView, CustomerDetailView,
    CustomerCreateView, CustomerUpdateView, CustomerDeleteView, CustomerExportView
)

urlpatterns = [
    path('', CustomerListView.as_view(), name='customer_list'),
    path('<int:pk>/', CustomerDetailView.as_view(), name='customer_detail'),
    path('create/', CustomerCreateView.as_view(), name='customer_create'),
    path('<int:pk>/edit/', CustomerUpdateView.as_view(), name='customer_update'),
    path('<int:pk>/delete/', CustomerDeleteView.as_view(), name='customer_delete'),
    path('export/', CustomerExportView.as_view(), name='customer_export'),
]