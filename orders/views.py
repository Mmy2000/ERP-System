from django.views.generic import ListView, DetailView, CreateView, View
from django.contrib import messages
from django.urls import  reverse
from django.shortcuts import redirect, get_object_or_404
from django.core.exceptions import ValidationError

from core.mixins import SalesOrAdminMixin
from .models import SalesOrder
from .forms import SalesOrderForm, OrderItemFormSet, OrderSearchForm
from .services import OrderService

from django.utils import timezone
from core.exports import build_workbook, workbook_response
from django.views import View

class OrderListView(SalesOrAdminMixin, ListView):
    model = SalesOrder
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 15

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        status = self.request.GET.get('status', '')
        return OrderService.search(query=query or None, status=status or None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = OrderSearchForm(self.request.GET)
        return context


class OrderDetailView(SalesOrAdminMixin, DetailView):
    model = SalesOrder
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'

    def get_object(self):
        return OrderService.get_by_id(self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        order = self.object
        user = self.request.user

        context['can_user_cancel'] = (
            (
                order.created_by == user
                or user.is_staff
                or user.is_superuser
            )
            and order.status != 'cancelled'
        )

        return context


class OrderCreateView(SalesOrAdminMixin, CreateView):
    model = SalesOrder
    form_class = SalesOrderForm
    template_name = 'orders/order_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['item_formset'] = OrderItemFormSet(self.request.POST, prefix='items')
        else:
            context['item_formset'] = OrderItemFormSet(prefix='items')
        context['title'] = 'Create Sales Order'
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        item_formset = context['item_formset']

        if not item_formset.is_valid():
            return self.form_invalid(form)

        items_data = []
        for item_form in item_formset:
            if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE', False):
                items_data.append({
                    'product': item_form.cleaned_data['product'],
                    'qty': item_form.cleaned_data['qty'],
                    'price': item_form.cleaned_data['price'],
                })

        try:
            order = OrderService.create_order(
                customer=form.cleaned_data['customer'],
                items_data=items_data,
                user=self.request.user,
                notes=form.cleaned_data.get('notes', ''),
            )
            messages.success(self.request, f'Order {order.order_number} created successfully.')
            return redirect(reverse('order_detail', kwargs={'pk': order.pk}))
        except (ValidationError, Exception) as e:
            messages.error(self.request, f'Error creating order: {e}')
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        messages.error(self.request, 'Please fix the errors below.')
        return super().form_invalid(form)


class OrderConfirmView(SalesOrAdminMixin, View):
    """Confirm an order — reduces stock."""

    def post(self, request, pk):
        order = get_object_or_404(SalesOrder, pk=pk)
        try:
            OrderService.confirm_order(order, user=request.user)
            messages.success(request, f'Order {order.order_number} confirmed. Stock updated.')
        except ValidationError as e:
            messages.error(request, str(e))
        return redirect(reverse('order_detail', kwargs={'pk': pk}))


class OrderCancelView(SalesOrAdminMixin, View):
    """Cancel an order — restores stock if was confirmed."""

    def post(self, request, pk):
        order = get_object_or_404(SalesOrder, pk=pk)
        try:
            OrderService.cancel_order(order, user=request.user)
            messages.success(request, f'Order {order.order_number} cancelled.')
        except ValidationError as e:
            messages.error(request, str(e))
        return redirect(reverse('order_detail', kwargs={'pk': pk}))
    


class OrderExportView(SalesOrAdminMixin, View):
    def get(self, request):
        orders = OrderService.get_all().prefetch_related('items__product').order_by('-created_at')

        order_rows = [
            [
                o.order_number,
                o.customer.name,
                o.customer.customer_code,
                o.order_date.strftime('%Y-%m-%d'),
                o.get_status_display(),
                float(o.total_amount),
                o.created_by.get_full_name() or o.created_by.username,
                o.created_at.strftime('%Y-%m-%d %H:%M'),
                o.notes,
            ]
            for o in orders
        ]

        orders_sheet = {
            'title': 'Orders',
            'headers': [
                'Order #', 'Customer', 'Customer Code', 'Order Date',
                'Status', 'Total Amount ($)', 'Created By', 'Created At', 'Notes',
            ],
            'rows': order_rows,
            'col_widths': [22, 28, 16, 14, 12, 18, 22, 20, 35],
            'number_formats': {6: '#,##0.00'},
        }

        item_rows = []
        for o in orders:
            for item in o.items.all():
                item_rows.append([
                    o.order_number,
                    o.customer.name,
                    o.order_date.strftime('%Y-%m-%d'),
                    o.get_status_display(),
                    item.product.sku,
                    item.product.name,
                    item.qty,
                    float(item.price),
                    float(item.total),
                ])

        items_sheet = {
            'title': 'Order Items',
            'headers': [
                'Order #', 'Customer', 'Order Date', 'Status',
                'SKU', 'Product', 'Qty', 'Unit Price ($)', 'Line Total ($)',
            ],
            'rows': item_rows,
            'col_widths': [22, 28, 14, 12, 15, 30, 8, 16, 16],
            'number_formats': {8: '#,##0.00', 9: '#,##0.00'},
        }

        wb = build_workbook([orders_sheet, items_sheet])
        filename = f'orders_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        return workbook_response(wb, filename)