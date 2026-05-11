from django import forms


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