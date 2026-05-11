from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect

from core.mixins import AdminRequiredMixin, SalesOrAdminMixin
from .models import Product
from .forms import ProductForm, ProductSearchForm
from .services import ProductService
from django.utils import timezone
from core.exports import build_workbook, workbook_response
from django.views import View


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
    success_url = reverse_lazy('products_list')

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
    success_url = reverse_lazy('products_list')

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
    success_url = reverse_lazy('products_list')

    def form_valid(self, form):
        ProductService.delete(self.object)
        messages.success(self.request, f'Product "{self.object.name}" deleted.')
        return redirect(self.success_url)
    


class ProductExportView(AdminRequiredMixin, View):
    def get(self, request):
        products = ProductService.get_all_active().order_by('category', 'name')

        rows = [
            [
                p.sku,
                p.name,
                p.category,
                float(p.cost_price),
                float(p.selling_price),
                float(p.selling_price - p.cost_price),
                round(float(p.profit_margin), 2),
                p.stock_qty,
                'Yes' if p.is_active else 'No',
                p.created_at.strftime('%Y-%m-%d'),
            ]
            for p in products
        ]

        sheet = {
            'title': 'Products',
            'headers': [
                'SKU', 'Name', 'Category', 'Cost Price ($)', 'Selling Price ($)',
                'Gross Profit ($)', 'Margin (%)', 'Stock Qty', 'Active', 'Created',
            ],
            'rows': rows,
            'col_widths': [15, 30, 18, 16, 17, 16, 13, 12, 8, 14],
            'number_formats': {4: '#,##0.00', 5: '#,##0.00', 6: '#,##0.00', 7: '0.00"%"'},
        }

        wb = build_workbook([sheet])
        filename = f'products_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        return workbook_response(wb, filename)