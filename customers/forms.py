from django import forms
from .models import Customer


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['customer_code', 'name', 'phone', 'address', 'email', 'opening_balance']
        widgets = {
            'customer_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Auto-generated if empty'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Customer full name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 234 567 8900'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Full address'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'opening_balance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer_code'].required = False
        self.fields['opening_balance'].required = False


class CustomerSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, code, or email...'
        })
    )