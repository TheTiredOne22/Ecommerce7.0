from django.db.models import Sum
from django.shortcuts import render, get_object_or_404
from shop.models import Product
from .models import Cart, CartItem
from django.contrib import messages
from django.http.response import HttpResponse


def get_cart(request):
    """
    Get or create a user's shopping cart using sessions.

    If the session has a cart ID, retrieve the cart.
    If not, create a new cart and store its ID in the session.

    Args:
        request: The HTTP request object.

    Returns:
        The user's shopping cart.
    """

    cart_id = request.session.get('cart_id')

    if not cart_id:
        # Create a new cart for the session
        cart = Cart.objects.create()
        request.session['cart_id'] = cart.id
    else:
        # Retrieve the existing cart for the session
        cart = Cart.objects.filter(id=cart_id).first()

    return cart


def cart_view(request):
    """
    Display the shopping cart and its contents.

    Retrieves the user's cart, cart items, total price, and discounts.

    Args:
        request: The HTTP request object.

    Returns:
        Rendered cart view with context data.
    """
    # Retrieve cart and cart items
    cart = get_cart(request)
    cart_items = cart.items.all()

    # Calculate total price, cart item count, and discounts
    total_price = cart.calculate_total()
    cart_item_count = count_cart_items(request)
    discount = cart.calculate_discount_string()
    subtotal = cart.calculate_subtotal()
    tax_amount = cart.calculate_tax()

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'cart_item_count': cart_item_count,
        'coupon': cart.coupon,
        'discount': discount,
        'subtotal': subtotal,
        'tax_amount': tax_amount
    }

    return render(request, 'cart/detail.html', context)


def count_cart_items(request):
    """
    Count the total quantity of items in the shopping cart.

    Args:
        request: The HTTP request object.

    Returns:
        The total quantity of items in the cart or 0 if the cart is empty.
    """
    # Retrieve cart and calculate total quantity of cart items
    cart = get_cart(request)
    total_quantity = CartItem.objects.filter(cart=cart).aggregate(Sum('quantity'))['quantity__sum']
    return total_quantity or 0


# Add a product to the cart or update its quantity
def add_to_cart(request, product_id):
    """
    Add a product to the shopping cart or update its quantity.

    Args:
        request: The HTTP request object.
        product_id: The ID of the product to add.

    Returns:
        Rendered cart menu.
    """
    # Retrieve the product and cart
    product = get_object_or_404(Product, id=product_id)
    cart = get_cart(request)

    # Extract the quantity from the request
    quantity = int(request.POST.get('quantity', 1))

    # Get or create a cart item for the product
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if created:
        # If the cart item is created, set its quantity and display a success message
        cart_item.quantity = quantity
        messages.success(request, f'{product.product_name} has been added to your cart.')
    elif cart_item.quantity < product.quantity:
        # If the product is already in the cart and available quantity allows, increment the quantity
        cart_item.quantity += quantity
        messages.success(request, f'{product.product_name} quantity has been updated in your cart.')

    cart_item.save()

    return render(request, 'cart/partials/cart_menu.html')


# Remove a cart item
def remove_from_cart(request, cart_item_id):
    """
    Remove an item from the shopping cart.

    Args:
        request: The HTTP request object.
        cart_item_id: The ID of the cart item to remove.

    Returns:
        An HTTP response with an update-cart trigger.
    """
    # Get the cart item with the specified ID
    cart_item = get_object_or_404(CartItem, id=cart_item_id)

    # Delete the cart item
    cart_item.delete()

    # Create an HTTP response and set an update-cart trigger
    response = HttpResponse()
    response['HX-Trigger'] = 'update-cart'
    return response


# Increase the quantity of a cart item
def increase_cart_item_quantity(request, cart_item_id):
    """
    Increase the quantity of a cart item in the shopping cart.

    Args:
        request: The HTTP request object.
        cart_item_id: The ID of the cart item to increase.

    Returns:
        An HTTP response with an update-cart trigger.
    """
    # Get the cart item with the specified ID
    cart_item = get_object_or_404(CartItem, id=cart_item_id)

    # Check if increasing the quantity doesn't exceed the product's available quantity
    if cart_item.quantity < cart_item.product.quantity:
        # Increment the cart item's quantity
        cart_item.quantity += 1
        cart_item.save()

    # Create an HTTP response with a status of 204 (success) and set an update-cart trigger
    response = HttpResponse(status=204)
    response['HX-Trigger'] = 'update-cart'
    return response


# Reduce the quantity of a cart item
def reduce_cart_item_quantity(request, cart_item_id):
    """
    Reduce the quantity of a cart item in the shopping cart.

    Args:
        request: The HTTP request object.
        cart_item_id: The ID of the cart item to reduce.

    Returns:
        An HTTP response with an update-cart trigger.
    """
    # Get the cart item with the specified ID
    cart_item = get_object_or_404(CartItem, id=cart_item_id)

    # Check if reducing the quantity to at least 1
    if cart_item.quantity > 1:
        # Decrement the cart item's quantity
        cart_item.quantity -= 1
        cart_item.save()

    # Create an HTTP response with a status of 204 (success) and set an update-cart trigger
    response = HttpResponse(status=204)
    response['HX-Trigger'] = 'update-cart'
    return response


# Render cart total
def hx_cart_total(request):
    return render(request, 'cart/partials/cart_total.html')


# Render cart subtotal
def hx_cart_subtotal(request):
    return render(request, 'cart/partials/cart_subtotal.html')


# Render cart tax rate
def hx_cart_tax(request):
    return render(request, 'cart/partials/cart_tax.html')


# Render cart menu
def hx_cart_menu(request):
    return render(request, 'cart/partials/cart_menu.html')


# Render empty cart message
def hx_empty_cart(request):
    return render(request, 'cart/partials/empty_cart.html')


# Render cart price update
def hx_cart_price(request):
    return render(request, 'cart/partials/update_price.html')
