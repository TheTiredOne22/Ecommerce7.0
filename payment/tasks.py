from io import BytesIO
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from celery import shared_task
from orders.models import Order
import weasyprint


@shared_task
def payment_completed(order_id):
    """
    Task to send an e-mail notification with an attached PDF invoice
    when an order is successfully paid.

    Args:
        order_id (int): The ID of the order to process.

    Raises:
        Order.DoesNotExist: If the specified order does not exist.
    """
    try:
        # Retrieve the order
        order = Order.objects.get(id=order_id)

        # Create an invoice e-mail
        subject = f'My Shop - Invoice no. {order.id}'
        message = 'Please find attached the invoice for your recent purchase.'
        email = send_mail(subject, message, 'admin@myshop.com', [order.email])

        # Generate the invoice PDF
        html = render_to_string('order/pdf.html', {'order': order})
        out = BytesIO()
        stylesheets = [weasyprint.CSS(settings.STATIC_ROOT / 'css/pdf.css')]
        weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)

        # Attach the PDF file
        email.attach(f'order_{order.order_number}.pdf', out.getvalue(), 'application/pdf')

        # Send the e-mail
        email.send()
    except Order.DoesNotExist:
        # Handle the case where the order does not exist
        raise Order.DoesNotExist(f"Order with ID {order_id} does not exist.")
