from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        import sys
        # Skip during CLI management commands
        if any(cmd in sys.argv for cmd in ['makemigrations', 'migrate', 'dumpdata', 'collectstatic', 'test']):
            return
        try:
            from store.models import Product
            from django.core.management import call_command
            if Product.objects.count() == 0:
                print("Database empty: Loading product fixtures automatically...")
                call_command('loaddata', 'store_fixture.json')
                print("Product fixtures loaded successfully!")
        except Exception as e:
            print("Auto fixture load check skipped:", e)
