from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

from core.mixins import AdminRequiredMixin, SalesOrAdminMixin
from .models import Customer
from .forms import CustomerForm, CustomerSearchForm
from .services import CustomerService


class CustomerListView(SalesOrAdminMixin, ListView):
    model = Customer
    template_name = 'customers/customer_list.html'
    context_object_name = 'customers'
    paginate_by = 15

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        return CustomerService.search(query=query or None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = CustomerSearchForm(self.request.GET)
        return context


class CustomerDetailView(SalesOrAdminMixin, DetailView):
    model = Customer
    template_name = 'customers/customer_detail.html'
    context_object_name = 'customer'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = self.object.salesorder_set.order_by('-created_at')[:10]
        return context


class CustomerCreateView(SalesOrAdminMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customers/customer_form.html'
    success_url = reverse_lazy('customer_list')

    def form_valid(self, form):
        try:
            data = {k: v for k, v in form.cleaned_data.items() if v != '' and v is not None}
            CustomerService.create(data)
            messages.success(self.request, 'Customer created successfully.')
            return redirect(self.success_url)
        except Exception as e:
            messages.error(self.request, f'Error creating customer: {e}')
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Customer'
        context['action'] = 'Create'
        return context


class CustomerUpdateView(SalesOrAdminMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customers/customer_form.html'
    success_url = reverse_lazy('customer_list')

    def form_valid(self, form):
        try:
            CustomerService.update(self.object, form.cleaned_data)
            messages.success(self.request, 'Customer updated successfully.')
            return redirect(self.success_url)
        except Exception as e:
            messages.error(self.request, f'Error updating customer: {e}')
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit: {self.object.name}'
        context['action'] = 'Update'
        return context


class CustomerDeleteView(AdminRequiredMixin, DeleteView):
    """Only admins can delete customers."""
    model = Customer
    template_name = 'customers/customer_confirm_delete.html'
    success_url = reverse_lazy('customer_list')

    def form_valid(self, form):
        CustomerService.delete(self.object)
        messages.success(self.request, f'Customer "{self.object.name}" deleted.')
        return redirect(self.success_url)