from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('process/', views.process_payment, name='process_payment'),
    path('completed/', views.payment_completed, name='completed'),
    path('cancelled/', views.payment_cancelled, name='canceled'),
    path('webhook/', views.webhook, name='webhook')
]
