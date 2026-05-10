from django import forms
from django.forms import formset_factory, BaseFormSet

from .models import SalesOrder
from customers.models import Customer
from products.models import Product


class SalesOrderForm(forms.ModelForm):
    class Meta:
        model = SalesOrder
        fields = ['customer', 'order_date', 'notes']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'order_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional notes...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer'].queryset = Customer.objects.filter(is_active=True)
        self.fields['notes'].required = False


class OrderItemForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select product-select'}),
        empty_label='Select product...'
    )
    qty = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'placeholder': 'Qty'})
    )
    price = forms.DecimalField(
        max_digits=12, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Unit price'})
    )


class BaseOrderItemFormSet(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return
        products = []
        has_valid = False
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                product = form.cleaned_data.get('product')
                if product:
                    if product in products:
                        raise forms.ValidationError('Each product can only appear once per order.')
                    products.append(product)
                    has_valid = True
        if not has_valid:
            raise forms.ValidationError('At least one item is required.')


OrderItemFormSet = formset_factory(
    OrderItemForm,
    formset=BaseOrderItemFormSet,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


class OrderSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by order # or customer...'})
    )
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Status'), ('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )