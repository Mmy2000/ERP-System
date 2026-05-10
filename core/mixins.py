from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class AdminRequiredMixin(LoginRequiredMixin):
    """Only allow admin (staff/superuser) users."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not (request.user.is_staff or request.user.is_superuser):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class SalesOrAdminMixin(LoginRequiredMixin):
    """Allow both sales users and admins."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


def is_admin(user):
    return user.is_staff or user.is_superuser


def is_sales(user):
    return user.is_authenticated and not (user.is_staff or user.is_superuser)