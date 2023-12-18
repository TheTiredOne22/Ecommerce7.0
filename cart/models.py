from django.db import models
from decimal import Decimal
from coupon.models import Coupon
from shop.models import Product


class Cart(models.Model):
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)

    def calculate_subtotal(self):
        return sum(item.item_price() for item in self.items.all())

    def calculate_discount_value(self, total_price):
        if self.coupon:
            if self.coupon.discount_type == 'Percentage':
                return (Decimal(self.coupon.value) / 100) * total_price
            elif self.coupon.discount_type == 'Fixed':
                return Decimal(self.coupon.value)
        return Decimal(0.00)

    def calculate_tax(self):
        total_price = self.calculate_subtotal()
        tax_percentage = Decimal('0.15')  # 15% tax rate
        tax_amount = total_price * tax_percentage
        return tax_amount

    def calculate_discount_string(self):
        if self.coupon:
            discount = self.calculate_discount_value(self.calculate_subtotal())
            discount_string = f"- ${discount:.2f}"
            return discount_string
        return None

    def calculate_total(self):
        total_price = self.calculate_subtotal()
        discount = self.calculate_discount_value(total_price)
        return total_price - discount + self.calculate_tax()

    def apply_discount(self):
        if self.coupon:
            discount = self.calculate_discount_value(self.calculate_total())
            current_total = self.calculate_total()
            new_total = current_total - discount
            return new_total
        return self.calculate_total()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} of {self.product.product_name}'

    def item_price(self):
        return self.quantity * self.product.price

    def update_quantity(self, new_quantity):
        self.quantity = new_quantity
        self.save()
