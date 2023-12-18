from django.shortcuts import get_object_or_404, render
from .models import CartItem


def calculate_total_price(cart_items):
    total_price = 0
    for item in cart_items:
        total_price += item.item_price()
    return total_price


# def count_cart_items(request):
#     cart, _ = get_cart(request)
#     cart_items = CartItem.objects.filter(cart=cart)
#     total_quantity = sum(cart_item.quantity for cart_item in cart_items)
#     return total_quantity


def get_cart_item_quantity(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)

    return render(request, 'cart/partials/cart_item_quantity.html', {'item': cart_item})


def update_item_price(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item_price = item.item_price

    return render(request, 'cart/partials/update_price.html', {'item_price': item_price})
