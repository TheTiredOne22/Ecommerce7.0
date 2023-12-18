from django import forms
from .models import Coupon


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount_type', 'value', 'valid_to', 'valid_from', 'max_usage',
                  'active']


class CouponUpdateForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount_type', 'value', 'valid_to', 'valid_from', 'max_usage',
                  'active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Populate the select field with choices from the model
        self.fields['discount_type'].widget = forms.Select(
            choices=Coupon.DISCOUNT_TYPES,
            attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 '
                         'focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 '
                         'dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 '
                         'dark:focus:border-primary-500 '
            }
        )
