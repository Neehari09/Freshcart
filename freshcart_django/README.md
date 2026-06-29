# FreshCart — Django Grocery Store

A Django implementation of the FreshCart grocery e-commerce mockup: Home,
Products (with category/price filters + pagination), Product Detail, Cart,
Checkout, About, and Contact pages.

## Stack
- Django 4.2+ (plain Django, no DRF/React needed)
- SQLite (default, zero setup)
- Session-based cart (works without user accounts/login)
- Product "photos" are emoji placeholders by default, but every product also
  has a real `ImageField` you can fill in via the admin if you want real photos.

## Setup

```bash
# 1. Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Apply migrations
python manage.py makemigrations
python manage.py migrate

# 4. Load sample categories & products (Apple, Banana, Milk, Tomato, Potato, etc.)
python manage.py seed_data

# 5. (Optional) create an admin user to manage products from /admin/
python manage.py createsuperuser

# 6. Run the dev server
python manage.py runserver
```

Then visit:
- http://127.0.0.1:8000/ — Home
- http://127.0.0.1:8000/products/ — Products
- http://127.0.0.1:8000/cart/ — Cart
- http://127.0.0.1:8000/about/ — About
- http://127.0.0.1:8000/contact/ — Contact
- http://127.0.0.1:8000/admin/ — Manage categories/products/messages

## Project structure

```
freshcart_django/
├── manage.py
├── requirements.txt
├── freshcart/              # project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── store/                  # the app: models, views, templates, static
    ├── models.py           # Category, Product, ContactMessage
    ├── views.py            # home, product_list, product_detail, cart_*, checkout, about, contact
    ├── cart.py             # session-based Cart helper class
    ├── forms.py            # ContactForm
    ├── urls.py
    ├── admin.py
    ├── management/commands/seed_data.py   # sample product data
    ├── templates/store/    # base.html + one template per page
    └── static/store/       # css/style.css (matches the mockup's green theme)
```

## How the key features work

- **Cart**: stored in the Django session (`store/cart.py`), so it persists
  across requests without requiring login. Add/update/remove all use POST
  requests with CSRF protection.
- **Filtering**: `/products/?category=fruits&min_price=20&max_price=100&sort=price_asc`
  — all handled server-side in `product_list` view.
- **Contact form**: saves every submission to the `ContactMessage` model,
  visible in `/admin/`.
- **Checkout**: a simple demo flow that clears the cart and shows a success
  message — there's no real payment gateway wired up. If you want a real
  payment integration later (Razorpay/Stripe), that would slot into the
  `checkout` view in `store/views.py`.

## Customizing product images

Right now product cards show large emoji as image placeholders so the project
works out of the box with zero asset files. To use real photos: upload an
image to a product's `image` field in `/admin/`, then update
`product_detail.html` / `home.html` / `products.html` to prefer
`product.image.url` over `product.emoji` when an image is present, e.g.:

```html
{% if product.image %}
  <img src="{{ product.image.url }}" alt="{{ product.name }}">
{% else %}
  <div class="thumb">{{ product.emoji }}</div>
{% endif %}
```

## Notes
- `DEBUG = True` and a placeholder `SECRET_KEY` are set for local development
  only — change both before deploying anywhere public.
- No payment gateway, real delivery logic, or user authentication is wired up
  — this is a frontend-matching functional demo, ready to extend.
