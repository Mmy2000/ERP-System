
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('products/', include('products.urls')),
    path('customers/', include('customers.urls')),
    path('orders/', include('orders.urls')),
    path('movements/', include('movements.urls')),
]
