from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Coupon(models.Model):
    DISCOUNT_TYPES = (
        ('Percentage', 'Percentage'),
        ('Fixed', 'Fixed'),
    )

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPES)
    value = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='The discount value, either a percentage or a fixed amount.'
    )
    valid_from = models.DateField()
    valid_to = models.DateField()
    max_usage = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Maximum number of times this coupon can be used.'
    )
    used_count = models.PositiveIntegerField(
        default=0,
        editable=False,
        help_text='Number of times this coupon has been used.'
    )
    active = models.BooleanField(
        help_text='Indicates whether the coupon is currently active or not.'
    )

    def __str__(self):
        return self.code
