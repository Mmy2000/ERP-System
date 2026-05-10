from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404
from django.core.exceptions import ValidationError

from core.mixins import SalesOrAdminMixin
from .models import SalesOrder
from .forms import SalesOrderForm, OrderItemFormSet, OrderSearchForm
from .services import OrderService


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