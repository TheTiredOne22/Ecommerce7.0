from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [

    path('top-selling-products/', views.top_selling_products, name='top_selling_products'),
    path('top-selling-products/<str:time_frame>/', views.top_selling_products,
         name='top_selling_products_timeframed'),

]
