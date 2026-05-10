from django.urls import path
from .views import auth_views , dashboard_views

urlpatterns = [
    path('login/', auth_views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.CustomLogoutView.as_view(), name='logout'),
    path('dashboard/', dashboard_views.DashboardView.as_view(), name='dashboard'),
]