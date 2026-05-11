from django.utils import timezone
from core.exports import build_workbook, workbook_response
from django.views import View
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
    


class StockMovementExportView(SalesOrAdminMixin, View):
    def get(self, request):
        movements = StockMovementService.get_all()

        rows = [
            [
                m.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                m.product.sku,
                m.product.name,
                m.product.category,
                m.get_movement_type_display(),
                m.qty,
                m.reference,
                m.user.username if m.user else 'System',
                m.notes,
            ]
            for m in movements
        ]

        sheet = {
            'title': 'Stock Movements',
            'headers': [
                'Timestamp', 'SKU', 'Product', 'Category',
                'Type', 'Qty Change', 'Reference', 'User', 'Notes',
            ],
            'rows': rows,
            'col_widths': [22, 15, 30, 18, 22, 12, 22, 18, 35],
        }

        wb = build_workbook([sheet])
        filename = f'stock_movements_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        return workbook_response(wb, filename)