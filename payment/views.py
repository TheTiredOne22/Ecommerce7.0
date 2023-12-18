import json
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseServerError, JsonResponse
from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.utils.crypto import constant_time_compare
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

import environ
import requests

# from order.models import Order
# from order.tasks import order_created

# Initialize environment variables
from orders.models import Order

env = environ.Env()
environ.Env.read_env()

# Initialize the logger
logger = logging.getLogger('webhook-logger')
logger.setLevel(logging.INFO)


def process_payment(request):
    """
    Process a payment request.

    Retrieves the order and relevant information, then sends a payment request to a third-party service.

    Args:
        request: The HTTP request object.

    Returns:
        An HttpResponseRedirect or HttpResponse object.
    """
    # Retrieve the order and relevant information
    order_id = request.session.get('order_id', None)
    order = get_object_or_404(Order, id=order_id)

    amount_in_kobo = int(order.total)
    order_number = order.order_number
    email = order.email
    user = request.user
    user_id = user.id
    name = f'{order.first_name} {order.last_name}'
    success_url = 'http://localhost:8000/payment/completed'

    # Set up authentication and headers
    auth_token = env('SECRET_KEY')
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }

    # Prepare data for the payment request
    data = {
        "id": order.id,
        "tx_ref": order_number,  # Unique transaction reference
        "amount": amount_in_kobo,  # Total order amount in kobo
        "currency": "USD",  # Replace with your desired currency code
        "redirect_url": success_url,
        "payment_options": "card",
        "customer": {
            "email": email,
            "name": name
        },
        "meta": {
            "consumer_id": user_id,  # Add any additional meta information
        },
        "customizations": {
            "title": "Your Order Payment",
            "logo": "your_logo_url_here",  # Add a URL to your logo
            "description": "Payment for your order",
        }
    }

    try:
        # Make the payment request
        response = requests.post('https://api.flutterwave.com/v3/payments', json=data, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        link = response_data['data']['link']
        return HttpResponseRedirect(link)
    except requests.exceptions.RequestException as e:
        # Handle request-related errors, and log the error for debugging
        logger.error(f"Request Error: {str(e)}")
        return HttpResponse(f"Request Error: {str(e)}", status=500)
    except ValueError as e:
        # Handle JSON parsing errors, and log the error for debugging
        logger.error(f"JSON Parsing Error: {str(e)}")
        return HttpResponse(f"JSON Parsing Error: {str(e)}", status=500)


def payment_completed(request):
    """
    Render the payment completed page.

    Args:
        request: The HTTP request object.

    Returns:
        A rendered HTML page.
    """
    return render(request, 'payment/completed.html')


def payment_cancelled(request):
    """
    Render the payment cancelled page.

    Args:
        request: The HTTP request object.

    Returns:
        A rendered HTML page.
    """
    return render(request, 'payment/cancelled.html')


@csrf_exempt
@require_POST
def webhook(request):
    """
    Handle incoming webhooks.

    Verify the webhook signature and process events.

    Args:
        request: The HTTP request object.

    Returns:
        An HTTP response indicating success or failure.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        # Return a JSON response for invalid JSON payload
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

        # Retrieve the secret hash from environment variables
    secret_hash = env('SECRET_HASH')  # Replace with your secret key retrieval

    # Retrieve the signature from the request headers
    signature = request.META.get('HTTP_VERIF-HASH')

    # Verify the request's signature with the secret hash
    if not signature or not constant_time_compare(signature, secret_hash):
        # Return an unauthorized response
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    # Extract event type and status from the payload
    event_type = data.get('event')
    status = data.get('data', {}).get('status')

    # Check if the event is 'charge.completed' and the status is 'successful'
    if event_type == 'charge.completed' and status == 'successful':
        order_number = data.get('tx_ref')  # Unique transaction reference

        try:
            # Find the order based on the order number (assuming it's unique)
            order = Order.objects.get(order_number=order_number)

            # Check if the amount in the payload matches the order amount
            if order.amount == data.get('data', {}).get('amount'):
                # Mark the order as paid
                order.paid = True
                order.save()

                # Asynchronously trigger the 'payment_completed' task with the order number
                payment_completed.delay(order_number)

                # Return a success response
                return HttpResponse({'message': 'Payment processed successfully'})
            else:
                logger.error('Amount mismatch for order %s', order.id)
                # Return a response for amount mismatch
                return HttpResponse({'error': 'Amount mismatch'}, status=400)
        except Order.DoesNotExist:
            # Return a response for order not found
            return HttpResponse({'error': 'Order not found'}, status=400)

    # Return a response for a received and processed webhook
    return HttpResponse({'message': 'Webhook received and processed'}, status=200)
