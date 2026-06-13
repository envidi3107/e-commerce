from django.db import models


class Category(models.Model):
    CATEGORY_CHOICES = [
        ('books',        'Books'),
        ('electronics',  'Electronics'),
        ('fashion',      'Fashion'),
        ('home_living',  'Home & Living'),
        ('sports',       'Sports'),
        ('beauty',       'Beauty & Personal Care'),
        ('toys',         'Toys & Games'),
        ('automotive',   'Automotive'),
        ('food',         'Food & Beverage'),
        ('health',       'Health & Wellness'),
    ]

    name        = models.CharField(max_length=100, unique=True)
    slug        = models.SlugField(max_length=100, unique=True)
    code        = models.CharField(max_length=30, choices=CATEGORY_CHOICES, unique=True)
    description = models.TextField(blank=True)
    image       = models.URLField(blank=True)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table  = 'categories'
        ordering  = ['name']
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    STATUS_CHOICES = [
        ('active',   'Active'),
        ('inactive', 'Inactive'),
        ('draft',    'Draft'),
    ]

    category    = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    name        = models.CharField(max_length=255)
    slug        = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    price       = models.DecimalField(max_digits=12, decimal_places=2)
    compare_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    sku         = models.CharField(max_length=100, unique=True)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    thumbnail   = models.URLField(blank=True)
    # Domain-specific attributes stored as JSON
    attributes  = models.JSONField(default=dict, blank=True)
    # e.g. for books: {"author":"...", "isbn":"...", "publisher":"...", "pages":300}
    # for electronics: {"brand":"...", "warranty_months":12, "model":"..."}
    # for fashion: {"sizes":["S","M","L"], "colors":["red","blue"], "material":"..."}
    rating_avg  = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    rating_count = models.PositiveIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product    = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image_url  = models.URLField()
    alt_text   = models.CharField(max_length=255, blank=True)
    order      = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_images'
        ordering = ['order']


class Inventory(models.Model):
    product        = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='inventory')
    quantity       = models.PositiveIntegerField(default=0)
    reserved       = models.PositiveIntegerField(default=0)  # reserved in active orders
    low_stock_threshold = models.PositiveIntegerField(default=10)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventory'
        verbose_name_plural = 'inventories'

    @property
    def available(self):
        return max(self.quantity - self.reserved, 0)

    @property
    def is_low_stock(self):
        return self.available <= self.low_stock_threshold

    def __str__(self):
        return f"{self.product.name} – qty:{self.quantity}"
