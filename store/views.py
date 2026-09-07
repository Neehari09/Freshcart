from decimal import Decimal

from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from .cart import Cart
from .forms import ContactForm
from .models import Category, Product, Order, OrderItem
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
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


@login_required
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, 'Your cart is empty. Add some products first!')
        return redirect('store:product_list')

    total_price = cart.get_total_price()
    
    # Initialize Razorpay Client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    # Create order in Razorpay (Amount in paise)
    razorpay_amount = int(total_price * 100)
    payment_data = {
        "amount": razorpay_amount,
        "currency": "INR",
        "payment_capture": "1"
    }
    
    razorpay_order = client.order.create(data=payment_data)
    razorpay_order_id = razorpay_order['id']

    # We will create the Order in the DB here as 'Pending'
    order = Order.objects.create(
        user=request.user,
        total_price=total_price,
        status='Pending',
        razorpay_order_id=razorpay_order_id
    )
    for item in cart:
        OrderItem.objects.create(
            order=order,
            product=item['product'],
            price=item['price'],
            quantity=item['quantity']
        )
        
    context = {
        'cart': cart,
        'razorpay_order_id': razorpay_order_id,
        'razorpay_merchant_key': settings.RAZORPAY_KEY_ID,
        'razorpay_amount': razorpay_amount,
        'currency': "INR",
        'callback_url': "http://" + request.get_host() + "/payment-callback/",
    }
    return render(request, 'store/checkout.html', context)


@csrf_exempt
def payment_callback(request):
    if request.method == "POST":
        payment_id = request.POST.get('razorpay_payment_id', '')
        provider_order_id = request.POST.get('razorpay_order_id', '')
        signature_id = request.POST.get('razorpay_signature', '')

        try:
            order = Order.objects.get(razorpay_order_id=provider_order_id)
        except Order.DoesNotExist:
            return HttpResponseBadRequest("Order not found")

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        # Verify Signature
        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': provider_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature_id
            })
            
            # If successful, mark order as Processing/Completed
            order.razorpay_payment_id = payment_id
            order.razorpay_signature = signature_id
            order.status = 'Processing'
            order.save()
            
            # Since the cross-site POST drops the session cookie, we manually log the user back in
            # using the user associated with the verified order
            login(request, order.user, backend='django.contrib.auth.backends.ModelBackend')
            
            # Clear the session cart
            cart = Cart(request)
            cart.clear()
            
            messages.success(request, 'Your payment was successful and your order has been placed!')
            return redirect('store:my_orders')

        except razorpay.errors.SignatureVerificationError:
            order.status = 'Cancelled'
            order.save()
            messages.error(request, 'Payment failed or signature mismatch.')
            return redirect('store:checkout')
            
    return HttpResponseBadRequest("Invalid request")


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'store/my_orders.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_detail.html', {'order': order})


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

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account successfully created')
            return redirect('store:login')
    else:
        form = UserCreationForm()
    return render(request, 'store/signup.html', {'form': form})
