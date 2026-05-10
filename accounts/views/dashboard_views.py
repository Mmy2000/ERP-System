from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from accounts.services.dashboard_service import DashboardService

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(DashboardService.get_stats())
        return context