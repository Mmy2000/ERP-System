from django.urls import path
from .views import (
    OrderListView, OrderDetailView, OrderCreateView,
    OrderConfirmView, OrderCancelView, OrderExportView
)


urlpatterns = [
    path('', OrderListView.as_view(), name='order_list'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('create/', OrderCreateView.as_view(), name='order_create'),
    path('<int:pk>/confirm/', OrderConfirmView.as_view(), name='order_confirm'),
    path('<int:pk>/cancel/', OrderCancelView.as_view(), name='order_cancel'),
    path('export/', OrderExportView.as_view(), name='order_export'),
]