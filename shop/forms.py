from django import forms
from .models import Category, Product


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'category', 'brand', 'product_image', 'description', 'price', 'quantity',
                  'is_available']

    # You can customize form widgets and add validation if needed
    widgets = {
        'description': forms.Textarea(attrs={'cols': 80, 'rows': 5}),
    }

    def clean_price(self):
        """
        Custom validation for the price field.
        """
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise forms.ValidationError("Price must be greater than zero.")
        return price

    def clean_quantity(self):
        """
        Custom validation for the quantity field.
        """
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and quantity <= 0:
            raise forms.ValidationError("Quantity must be a positive integer.")
        return quantity


class ProductUpdateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'category', 'brand', 'product_image', 'description', 'price', 'quantity',
                  'is_available']
