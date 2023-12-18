from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('products/', views.product, name='products'),
    path('product/create/', views.create_product, name='create_product'),
    path('product/detail/', views.product_detail, name='product_detail'),
    path('product/update/<int:product_id>/', views.product_update, name='update_product'),
    path('product/delete/<int:product_id>/', views.product_delete, name='delete_product'),
    path('product/search/', views.product_search, name='search'),
    path('product/bulk-delete', views.bulk_delete_view, name='bulk_delete'),

    # coupons
    path('coupons/', views.coupon, name='coupons'),

    # orders
    path('orders/', views.order, name='orders'),
    path('orders/detail/<int:order_id>', views.order_detail, name='order_detail'),
    path('orders/search/', views.order_search, name='order_search'),

]
