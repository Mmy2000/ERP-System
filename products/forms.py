from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['sku', 'name', 'category', 'cost_price', 'selling_price', 'stock_qty', 'image']
        widgets = {
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. PROD-001'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product name'}),
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Electronics'}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock_qty': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        cost = cleaned_data.get('cost_price')
        selling = cleaned_data.get('selling_price')
        if cost and selling and selling < cost:
            self.add_error('selling_price', 'Selling price must be greater than or equal to cost price.')
        return cleaned_data


class ProductSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by name or SKU...'})
    )
    category = forms.CharField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, categories=None, **kwargs):
        super().__init__(*args, **kwargs)
        if categories:
            choices = [('', 'All Categories')] + [(c, c) for c in categories]
            self.fields['category'].widget.choices = choices