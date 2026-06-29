from django.core.management.base import BaseCommand
from django.utils.text import slugify
from store.models import Category, Product


CATEGORIES = [
    ('Fruits', '🍎', 1),
    ('Vegetables', '🥦', 2),
    ('Dairy', '🥛', 3),
    ('Beverages', '🧃', 4),
    ('Snacks', '🍪', 5),
    ('Personal Care', '🧴', 6),
]

PRODUCTS = [
    # name, category, emoji, price, unit, featured, description
    ('Apple', 'Fruits', '🍎', 120, 'kg', True, 'Fresh and natural apples. Rich in nutrients and goodness. Perfect for a healthy diet.'),
    ('Banana', 'Fruits', '🍌', 60, 'dozen', True, 'Sweet, ripe bananas packed with potassium and natural energy.'),
    ('Orange', 'Fruits', '🍊', 90, 'kg', False, 'Juicy oranges loaded with vitamin C.'),
    ('Grapes', 'Fruits', '🍇', 110, 'kg', False, 'Seedless green grapes, fresh and crisp.'),
    ('Tomato', 'Vegetables', '🍅', 40, 'kg', True, 'Farm-fresh, ripe red tomatoes ideal for cooking and salads.'),
    ('Potato', 'Vegetables', '🥔', 30, 'kg', True, 'Versatile, fresh potatoes for everyday cooking.'),
    ('Onion', 'Vegetables', '🧅', 25, 'kg', False, 'Fresh onions, a kitchen essential.'),
    ('Broccoli', 'Vegetables', '🥦', 80, 'kg', False, 'Crisp, nutrient-rich broccoli florets.'),
    ('Milk', 'Dairy', '🥛', 60, 'ltr', True, 'Pure, pasteurized full-cream milk delivered fresh.'),
    ('Cheese', 'Dairy', '🧀', 150, 'pack', False, 'Creamy, delicious cheese block.'),
    ('Butter', 'Dairy', '🧈', 95, 'pack', False, 'Rich and creamy table butter.'),
    ('Rice', 'Dairy', '🍚', 80, 'kg', False, 'Premium long-grain rice.'),
    ('Cooking Oil', 'Beverages', '🛢️', 180, 'ltr', False, 'Refined cooking oil, light and healthy.'),
    ('Orange Juice', 'Beverages', '🧃', 70, 'ltr', False, 'Freshly squeezed orange juice, no added sugar.'),
    ('Mineral Water', 'Beverages', '💧', 20, 'ltr', False, 'Clean, safe packaged drinking water.'),
    ('Potato Chips', 'Snacks', '🥔', 30, 'pack', False, 'Crispy, crunchy potato chips, lightly salted.'),
    ('Cookies', 'Snacks', '🍪', 50, 'pack', False, 'Crunchy butter cookies, great with tea.'),
    ('Hand Wash', 'Personal Care', '🧼', 90, 'pc', False, 'Gentle, moisturizing hand wash.'),
    ('Shampoo', 'Personal Care', '🧴', 140, 'pc', False, 'Nourishing shampoo for everyday use.'),
]


class Command(BaseCommand):
    help = 'Seed the database with sample FreshCart categories and products.'

    def handle(self, *args, **options):
        category_objs = {}
        for name, icon, order in CATEGORIES:
            cat, created = Category.objects.get_or_create(
                slug=slugify(name),
                defaults={'name': name, 'icon': icon, 'order': order},
            )
            category_objs[name] = cat
            self.stdout.write(self.style.SUCCESS(f'Category ready: {cat.name}'))

        for name, cat_name, emoji, price, unit, featured, description in PRODUCTS:
            product, created = Product.objects.get_or_create(
                slug=slugify(name),
                defaults={
                    'name': name,
                    'category': category_objs[cat_name],
                    'emoji': emoji,
                    'price': price,
                    'unit': unit,
                    'is_featured': featured,
                    'description': description,
                    'stock': 100,
                },
            )
            status = 'Created' if created else 'Already exists'
            self.stdout.write(self.style.SUCCESS(f'{status}: {product.name}'))

        self.stdout.write(self.style.SUCCESS('Seeding complete!'))
