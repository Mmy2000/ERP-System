from django.views.generic import ListView
from core.mixins import SalesOrAdminMixin
from .forms import StockMovementSearchForm
from .models import StockMovement
from .services import StockMovementService

class StockMovementListView(SalesOrAdminMixin, ListView):
    model = StockMovement
    template_name = 'stock/movement_list.html'
    context_object_name = 'movements'
    paginate_by = 20

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        movement_type = self.request.GET.get('movement_type', '')
        return StockMovementService.search(
            query=query or None,
            movement_type=movement_type or None
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = StockMovementSearchForm(self.request.GET)
        return context