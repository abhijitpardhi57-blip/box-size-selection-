from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

# Validators run in full_clean() / the admin. The algorithm layer re-validates
# everything anyway, so bad rows written around the validators cannot cause a wrong box.
_POSITIVE_CM = [MinValueValidator(Decimal("0.01"))]
_POSITIVE_KG = [MinValueValidator(Decimal("0.001"))]


class Product(models.Model):
    """Something we sell. Dimensions in cm, weight in kg."""

    sku = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=200)
    length_cm = models.DecimalField(max_digits=8, decimal_places=2, validators=_POSITIVE_CM)
    width_cm = models.DecimalField(max_digits=8, decimal_places=2, validators=_POSITIVE_CM)
    height_cm = models.DecimalField(max_digits=8, decimal_places=2, validators=_POSITIVE_CM)
    weight_kg = models.DecimalField(max_digits=8, decimal_places=3, validators=_POSITIVE_KG)

    class Meta:
        ordering = ["sku"]

    def __str__(self):
        return f"{self.sku} - {self.name}"


class Box(models.Model):
    """A shipping box. Dimensions are INTERNAL (usable space), in cm."""

    name = models.CharField(max_length=100, unique=True)
    inner_length_cm = models.DecimalField(max_digits=8, decimal_places=2, validators=_POSITIVE_CM)
    inner_width_cm = models.DecimalField(max_digits=8, decimal_places=2, validators=_POSITIVE_CM)
    inner_height_cm = models.DecimalField(max_digits=8, decimal_places=2, validators=_POSITIVE_CM)
    max_weight_kg = models.DecimalField(max_digits=8, decimal_places=3, validators=_POSITIVE_KG)
    cost = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal("0"))]
    )
    is_active = models.BooleanField(default=True, help_text="Inactive boxes are never recommended.")

    class Meta:
        ordering = ["cost", "name"]
        verbose_name_plural = "boxes"

    def __str__(self):
        return self.name


class Order(models.Model):
    class Status(models.TextChoices):
        BOXED = "boxed", "Boxed"
        NEEDS_REVIEW = "needs_review", "Needs manual review"

    reference = models.CharField(max_length=64, unique=True)
    status = models.CharField(max_length=20, choices=Status.choices)
    recommended_box = models.ForeignKey(
        Box, null=True, blank=True, on_delete=models.SET_NULL, related_name="orders"
    )
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return self.reference


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["order", "product"], name="unique_product_per_order")
        ]

    def __str__(self):
        return f"{self.quantity} x {self.product.sku}"
