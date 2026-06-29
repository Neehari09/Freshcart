from decimal import Decimal

from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .cart import Cart
from .forms import ContactForm
from .models import Category, Product


def home(request):
    categories = Category.objects.all()
    featured_products = Product.objects.filter(is_featured=True).select_related('category')[:5]
    context = {
        'categories': categories,
        'featured_products': featured_products,
    }
    return render(request, 'store/home.html', context)


def product_list(request):
    categories = Category.objects.all()
    products = Product.objects.select_related('category').all()

    category_slug = request.GET.get('category')
    active_category = None
    if category_slug and category_slug != 'all':
        active_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=active_category)

    query = request.GET.get('q')
    if query:
        products = products.filter(name__icontains=query)

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=Decimal(min_price))
    if max_price:
        products = products.filter(price__lte=Decimal(max_price))

    sort = request.GET.get('sort')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'name':
        products = products.order_by('name')

    paginator = Paginator(products,8)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'categories': categories,
        'active_category': active_category,
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'query': query or '',
        'min_price': min_price or '',
        'max_price': max_price or '',
    }
    return render(request, 'store/products.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(id=product.id)[:4]
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'store/product_detail.html', context)


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'store/cart.html', {'cart': cart})


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product=product, quantity=quantity)
    messages.success(request, f'{product.name} added to your cart.')

    if request.POST.get('buy_now'):
        return redirect('store:checkout')

    next_url = request.POST.get('next') or 'store:product_list'
    if next_url.startswith('/'):
        return redirect(next_url)
    return redirect(next_url)


@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    action = request.POST.get('action')
    current_qty = cart.cart.get(str(product.id), {}).get('quantity', 1)

    if action == 'increase':
        cart.add(product=product, quantity=1)
    elif action == 'decrease':
        new_qty = max(current_qty - 1, 1)
        cart.add(product=product, quantity=new_qty, update_quantity=True)
    return redirect('store:cart_detail')


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.info(request, f'{product.name} removed from your cart.')
    return redirect('store:cart_detail')


def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, 'Your cart is empty. Add some products first!')
        return redirect('store:product_list')

    if request.method == 'POST':
        cart.clear()
        messages.success(request, 'Your order has been placed successfully! Thank you for shopping with FreshCart.')
        return redirect('store:home')

    return render(request, 'store/checkout.html', {'cart': cart})


def about(request):
    return render(request, 'store/about.html')


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thanks for reaching out! We'll get back to you soon.")
            return redirect('store:home')
    else:
        form = ContactForm()
    return render(request, 'store/contact.html', {'form': form})
