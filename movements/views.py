from django.views.generic import ListView
from django import forms

from core.mixins import SalesOrAdminMixin
from .models import StockMovement
from .services import StockMovementService


class StockMovementSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by product or reference...'})
    )
    movement_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types'), ('sale', 'Sale'), ('return', 'Return'), ('adjustment', 'Adjustment'), ('purchase', 'Purchase')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )


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