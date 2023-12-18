# from django.db import models
# from django.db.models import Sum
# from datetime import datetime, timedelta
# from orders.models import Order
# from django.utils import timezone
#
#
# # Create your models here.
#
#
# def get_sales_data(time_range):
#     now = timezone.now
#
#     if time_range == 'today':
#         start_date = datetime.combine(now.date(), datetime.min.time())
#     elif time_range == 'yesterday':
#         start_date = now - timedelta(days=1)
#     elif time_range == 'last_7_days':
#         start_date = now - timedelta(days=7)
#     elif time_range == 'last_30_days':
#         start_date = now - timedelta(days=30)
#     elif time_range == 'last_60_days':
#         start_date = now - timedelta(days=60)
#     else:
#         return None
#
#     sales_data = Order.objects.filter(
#         paid=True,
#         created__gte=start_date,
#         created__lte=now
#     ).aggregate(total_sales=Sum('total'))
#
#     return sales_data['total_sales'] if sales_data['total_sales'] else 0.00
