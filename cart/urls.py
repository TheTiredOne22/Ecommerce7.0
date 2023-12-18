from django.urls import path
from . import views
from . import utils

app_name = 'cart'

urlpatterns = [
    path('', views.cart_view, name='cart'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('increase-cart-item-quantity/<int:cart_item_id>/', views.increase_cart_item_quantity,
         name='increase_cart_quantity'),
    path('reduce-cart-item-quantity/<int:cart_item_id>/', views.reduce_cart_item_quantity,
         name='reduce_cart_quantity'),
    path('get-cart-item-quantity/<int:cart_item_id>/', utils.get_cart_item_quantity, name='get_cart_item_quantity'),
    path('update-item-price/<int:item_id>/', utils.update_item_price, name='update_item_price'),
    path('hx_cart_total', views.hx_cart_total, name='hx_cart_total'),
    path('hx_cart_tax', views.hx_cart_tax, name='hx_cart_tax'),
    path('hx_cart_subtotal', views.hx_cart_subtotal, name='hx_cart_subtotal'),
    path('hx_cart_menu', views.hx_cart_menu, name='hx_cart_menu'),
    path('hx_empty_cart', views.hx_empty_cart, name='hx_empty_cart'),
    path('hx_update_price', views.hx_cart_price, name='hx_cart_price'),

]
