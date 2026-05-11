from django.views.generic import TemplateView

class HomeView(TemplateView):
    """Public-facing landing page — no login required."""
    template_name = 'home.html'