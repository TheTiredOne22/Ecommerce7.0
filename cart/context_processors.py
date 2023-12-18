from .models import CartItem
from .views import get_cart, count_cart_items


def cart_context(request):
    cart = get_cart(request)
    if cart is not None:
        cart_items = CartItem.objects.filter(cart=cart)
        total_price = cart.calculate_total()
        cart_item_count = count_cart_items(request)
        coupon = cart.coupon
        tax_amount = cart.calculate_tax()
        discount = cart.calculate_discount_string()
        subtotal = cart.calculate_subtotal()
    else:
        # Handle the case where 'cart' is None, e.g., by setting default values or raising an error.
        cart_items = []
        total_price = 0
        cart_item_count = 0

    return {
        'cart_items': cart_items,
        'total_price': total_price,
        'cart_item_count': cart_item_count,
        'tax_amount': tax_amount,
        'coupon': coupon,
        'discount': discount,
        'subtotal': subtotal

    }
