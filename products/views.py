from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect

from core.mixins import AdminRequiredMixin, SalesOrAdminMixin
from .models import Product
from .forms import ProductForm, ProductSearchForm
from .services import ProductService


class ProductListView(SalesOrAdminMixin, ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        form = ProductSearchForm(
            self.request.GET,
            categories=ProductService.get_categories()
        )
        query = self.request.GET.get('q', '')
        category = self.request.GET.get('category', '')
        return ProductService.search(query=query or None, category=category or None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ProductSearchForm(
            self.request.GET,
            categories=ProductService.get_categories()
        )
        return context


class ProductDetailView(SalesOrAdminMixin, DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'


class ProductCreateView(AdminRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('products:list')

    def form_valid(self, form):
        try:
            ProductService.create(form.cleaned_data)
            messages.success(self.request, 'Product created successfully.')
            return redirect(self.success_url)
        except Exception as e:
            messages.error(self.request, f'Error creating product: {e}')
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Product'
        context['action'] = 'Create'
        return context


class ProductUpdateView(AdminRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('products:list')

    def form_valid(self, form):
        try:
            ProductService.update(self.object, form.cleaned_data)
            messages.success(self.request, 'Product updated successfully.')
            return redirect(self.success_url)
        except Exception as e:
            messages.error(self.request, f'Error updating product: {e}')
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit: {self.object.name}'
        context['action'] = 'Update'
        return context


class ProductDeleteView(AdminRequiredMixin, DeleteView):
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('products:list')

    def form_valid(self, form):
        ProductService.delete(self.object)
        messages.success(self.request, f'Product "{self.object.name}" deleted.')
        return redirect(self.success_url)