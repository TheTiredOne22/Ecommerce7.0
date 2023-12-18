from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from shop.models import Product, Category


def product_list(request, category_slug=None):
    products = Product.objects.all()
    categories = Category.objects.all()

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    sort_option = request.GET.get('sort_by')
    if sort_option == 'lowest':
        products = products.order_by('price')
    elif sort_option == 'highest':
        products = products.order_by('-price')

    paginator = Paginator(products, 8)
    page = request.GET.get('page')

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'shop/list.html', {'products': products, 'categories': categories})


def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, is_available=True)
    return render(request, 'shop/detail.html', {'product': product})


def product_search(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(product_name__icontains=query)
    else:
        products = Product.objects.all()

    return render(request, 'shop/partials/search_results.html', {'products': products})
