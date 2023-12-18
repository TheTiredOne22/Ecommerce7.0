from django.urls import path
from . import views

app_name = 'coupon'

urlpatterns = [
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('delete-coupon/', views.remove_coupon, name='remove_coupon')
]
