from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal

from .forms import CouponForm
from .models import Coupon  # Adjust this import to your actual Coupon model
from cart.views import get_cart  # You need to implement or import get_cart


def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')

        # Initialize coupon as None by default.
        coupon = None

        try:
            coupon = Coupon.objects.get(
                code=coupon_code,
                active=True,
                valid_from__lte=timezone.now(),
                valid_to__gte=timezone.now()
            )
        except Coupon.DoesNotExist:
            messages.error(request, 'Invalid coupon code.')

        cart = get_cart(request)

        # Check if the coupon is not found (coupon is None).
        if coupon is None:
            messages.error(request, 'Coupon not found.')
        else:
            if cart.coupon == coupon:
                messages.error(request, 'This coupon has already been applied to your cart.')
            elif coupon.max_usage is not None and coupon.used_count >= coupon.max_usage:
                messages.error(request, "This coupon has reached its maximum usage limit.")
            else:
                cart.coupon = coupon
                cart.save()
                messages.success(request, 'Coupon applied successfully')

    return redirect('cart:cart')


def remove_coupon(request):
    if request.method == 'POST':
        cart = get_cart(request)
        cart.coupon = None
        cart.save()
        messages.success(request, 'Coupon removed')
    return redirect('cart:cart')
