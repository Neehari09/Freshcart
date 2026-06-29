from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    icon = models.CharField(
        max_length=10, default='🛒',
        help_text='Emoji used as a lightweight icon (e.g. 🍎, 🥦, 🥛).'
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:product_list') + f'?category={self.slug}'


class Product(models.Model):
    UNIT_CHOICES = [
        ('kg', 'kg'),
        ('dozen', 'dozen'),
        ('ltr', 'ltr'),
        ('pack', 'pack'),
        ('pc', 'pc'),
    ]

    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=160, unique=True)
    emoji = models.CharField(
        max_length=10, default='🛒',
        help_text='Emoji shown as the product image placeholder.'
    )
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='kg')
    description = models.TextField(blank=True)
    stock = models.PositiveIntegerField(default=100)
    is_featured = models.BooleanField(default=False, help_text='Show on Best Selling Products (home page).')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.slug])

    @property
    def in_stock(self):
        return self.stock > 0


class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} <{self.email}>'
