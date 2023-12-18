from django.shortcuts import render
from django.db.models import Sum, F
from datetime import datetime, timedelta
from shop.models import Product
from orders.models import Order, OrderItem


def top_selling_products(request, days=7):
    # Calculate the start and end dates for the time frame
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)

    # Get the top-selling products for the time frame
    top_products = OrderItem.objects.filter(order__created__range=(start_date, end_date)) \
                       .values('product__product_name', 'product__product_image') \
                       .annotate(total_sales=Sum('price')) \
                       .order_by('-total_sales')[:10]

    # Calculate the percentage increase vs the last period
    last_period_end_date = start_date - timedelta(days=1)
    last_period_start_date = last_period_end_date - timedelta(days=days)
    last_period_sales = OrderItem.objects.filter(order__created__range=(last_period_start_date, last_period_end_date)) \
                            .aggregate(total_sales=Sum('price'))['total_sales'] or 0
    for product in top_products:
        product['percentage_increase'] = (product[
                                              'total_sales'] - last_period_sales) / last_period_sales * 100 if last_period_sales else 0

    # Render the template with the top-selling products
    context = {'top_products': top_products}
    return render(request, 'admin_panel/partials/analytics/top-products.html', context)
