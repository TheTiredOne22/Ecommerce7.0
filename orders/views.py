from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.template.loader import render_to_string, get_template

from .forms import OrderCreationForm
from .models import Order, OrderItem
from cart.views import get_cart
from .tasks import order_created
import weasyprint


# from order.tasks import order_created

def create_order(request):
    """
    Create a new order based on the user's cart contents.

    Args:
        request: The HTTP request object.

    Returns:
        A rendered HTML page with the order creation form.
    """
    user_cart = get_cart(request)

    if request.method == 'POST':
        form = OrderCreationForm(request.POST)

        if form.is_valid():
            # Retrieve the total from the cart model
            total_amount = user_cart.calculate_total()

            # Create a new order
            new_order = form.save(commit=False)
            new_order.total = total_amount
            new_order.save()

            # Create order items based on cart items
            cart_items = user_cart.items.all()
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=new_order,
                    product=cart_item.product,
                    price=cart_item.product.price,
                    quantity=cart_item.quantity,
                )

            cart_items.delete()
            request.session['order_id'] = new_order.id
            order_created.delay(new_order.id)

            return redirect(reverse('payment:process_payment'))
    else:
        form = OrderCreationForm()

    return render(request, 'order/create.html', {'user_cart': user_cart, 'form': form})


@staff_member_required
def admin_order_detail(request, order_id):
    """
    Render the order detail page for administrators.

    Args:
        request: The HTTP request object.
        order_id (int): The ID of the order to display.

    Returns:
        A rendered HTML page displaying order details.
    """
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'admin/orders/order/detail.html', {'order': order})

# @staff_member_required
# def admin_order_pdf(request, order_id):
#     # Get the data to be displayed in the PDF
#     order = get_object_or_404(Order, id=order_id)
#     html = render_to_string('orders/pdf.html', {'order': order})
#     response = HttpResponse(content_type='application/pdf')
#     response['content_disposition'] = f'filename=order_{order.id}.pdf'
#     weasyprint.HTML(string=html).write_pdf(response, stylesheets=[weasyprint.CSS])
