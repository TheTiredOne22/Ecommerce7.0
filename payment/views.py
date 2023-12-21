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

from orders.models import Order
from payment.tasks import payment_completed

# Initialize environment variables

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

    success_url = request.build_absolute_uri(reverse('payment:completed'))

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


@require_POST
@csrf_exempt
def webhook(request):
    secret_hash = env('SECRET_HASH')
    signature = request.META.get('HTTP_VERIF-HASH')
    if signature is None or (signature != secret_hash):
        # This request isn't from Flutterwave; discard
        return HttpResponse(status=401)
    payload = request.body
    payload_data = json.loads(payload)
    if payload_data.get('event') == 'charge.completed' and payload_data['data']['status'] == 'successful':
        order_id = payload_data['data']['id']
        order = get_object_or_404(Order, id=order_id)

        order.paid = True
        order.save()
        payment_completed.delay(order.id)
    return HttpResponse(status=200)
