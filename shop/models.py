from django.core.validators import MinValueValidator
from django.db import models
from autoslug import AutoSlugField
from django.urls import reverse


# Create your models here.
class Category(models.Model):
    """
    Model to represent product categories.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = AutoSlugField(populate_from='name')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse('shop:product_list_by_category',
                       args=[self.slug])


class Product(models.Model):
    """
    Model to represent individual products.
    """
    product_name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.CharField(max_length=100, blank=True)
    product_image = models.ImageField(upload_to='products/%Y/%m/%d', null=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=1, blank=False,
                                validators=[MinValueValidator(0.01)])
    quantity = models.PositiveIntegerField(blank=False)
    slug = AutoSlugField(populate_from='product_name', unique=True)
    is_available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']
        verbose_name_plural = 'products'

    def __str__(self):
        return self.product_name

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.id, self.slug])
