from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.
from django.urls import reverse
from coupon.forms import CouponForm, CouponUpdateForm
from coupon.models import Coupon
from orders.models import Order
from shop.forms import ProductForm, ProductUpdateForm
from shop.models import Product, Category
from django.shortcuts import redirect
from django.contrib import messages


@login_required
def user_dashboard(request):
    user = request.user

    context = {
        'user': user,
    }

    return render(request, 'admin_panel/dashboard.html', context)


def product(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    form = ProductForm()
    product_count = products.count()

    # pagination logic
    page_number = request.GET.get('page', 1)
    products_per_page = 10

    paginator = Paginator(products, products_per_page)
    try:
        current_page = paginator.page(page_number)
    except PageNotAnInteger:
        current_page = paginator.page(1)
    except EmptyPage:
        current_page = paginator.page(paginator.num_pages)

    start_range = (current_page.number - 1) * products_per_page + 1
    end_range = start_range + len(current_page.object_list) - 1

    context = {
        'products': products,
        'categories': categories,
        'product_count': product_count,
        'start_range': start_range,
        'end_range': end_range,
        'form': form,
    }
    return render(request, 'admin_panel/products.html', context)


def product_search(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(product_name__icontains=query)
    else:
        products = Product.objects.all()

    return render(request, 'admin_panel/partials/products/table-results.html', {'products': products})


def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully.')
            return redirect(reverse('admin_panel:products'))
        else:
            messages.error(request, 'Error Adding Product')
    else:
        form = ProductForm()

    return render(request, 'admin_panel/products.html', {'form': form})


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'admin_panel/partials/products/preview.html', {'product': product})


def product_update(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductUpdateForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully')
            return redirect(reverse('admin_panel:products'))
        else:
            messages.error(request, 'Error updating products')
    else:
        form = ProductUpdateForm(instance=product)

    context = {
        'product': product,
        'form': form
    }
    return render(request, 'admin_panel/partials/products/update.html', context)


def product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully')
        return HttpResponse()
    else:
        messages.error(request, 'Error deleting product')
    return render(request, 'admin_panel/partials/products/delete.html', {'product': product})


def bulk_delete_view(request):
    selected_products_ids = request.POST.getlist('selected_products')
    Product.objects.filter(id__in=selected_products_ids).delete()
    return redirect(reverse('admin_panel:products'))


def coupon(request):
    coupons = Coupon.objects.all()

    context = {
        'coupons': coupons
    }
    return render(request, 'admin_panel/coupons.html', context)


def create_coupon(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully.')
            return redirect(reverse('admin_panel:products'))
        else:
            messages.error(request, 'Error Adding Product')
    else:
        form = CouponForm()

    return render(request, 'admin_panel/coupons.html', {'form': form})


def update_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    if request.method == 'POST':
        form = CouponUpdateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon updated successfully.')
            return redirect(reverse('admin_panel:coupons'))
        else:
            messages.error(request, 'Error updating coupon')
    else:
        form = CouponUpdateForm()
    context = {
        'coupon': coupon,
        'form': form
    }
    return render(request, 'admin_panel/partials/coupons/update-coupon.html', context)


def order(request):
    orders = Order.objects.all()
    return render(request, 'admin_panel/orders.html', {'orders': orders})


def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'admin_panel/partials/orders/preview.html', {'order': order})


def order_search(request):
    query = request.GET.get('q', '')

    if query:
        orders = Order.objects.filter(
            Q(order_number__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
    else:
        orders = Order.objects.all()

    return render(request, 'admin_panel/partials/orders/order-results.html', {'orders': orders})
