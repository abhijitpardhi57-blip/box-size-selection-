"""Glue between the database and the pure algorithm."""
from typing import Dict, List, Tuple

from .algorithm import BoxSpec, Item, Recommendation, recommend_box
from .models import Box, Order, OrderItem, Product

NO_BOX_MESSAGE = (
    "No single box can hold this order. Split it into several parcels or review it manually."
)


class UnknownSkuError(Exception):
    def __init__(self, skus: List[str]):
        super().__init__(f"Unknown SKU(s): {', '.join(skus)}")
        self.skus = skus


def load_order_lines(requested: Dict[str, int]) -> List[Tuple[Item, int]]:
    """{sku: quantity} -> [(Item, quantity)]. Raises UnknownSkuError for missing SKUs."""
    products = {p.sku: p for p in Product.objects.filter(sku__in=list(requested))}
    missing = sorted(set(requested) - set(products))
    if missing:
        raise UnknownSkuError(missing)
    lines = []
    for sku in sorted(requested):
        p = products[sku]
        item = Item(p.sku, p.length_cm, p.width_cm, p.height_cm, p.weight_kg)
        lines.append((item, requested[sku]))
    return lines


def active_boxes() -> List[BoxSpec]:
    return [
        BoxSpec(
            id=b.id,
            name=b.name,
            length=b.inner_length_cm,
            width=b.inner_width_cm,
            height=b.inner_height_cm,
            max_weight=b.max_weight_kg,
            cost=b.cost,
        )
        for b in Box.objects.filter(is_active=True)
    ]


def recommend(requested: Dict[str, int]) -> Recommendation:
    return recommend_box(active_boxes(), load_order_lines(requested))


def create_order(reference: str, requested: Dict[str, int], recommendation: Recommendation) -> Order:
    """Persist an order together with the recommendation that was made for it."""
    best = recommendation.best
    order = Order.objects.create(
        reference=reference,
        status=Order.Status.BOXED if best else Order.Status.NEEDS_REVIEW,
        recommended_box_id=best.box.id if best else None,
        note="" if best else NO_BOX_MESSAGE,
    )
    products = Product.objects.filter(sku__in=list(requested))
    OrderItem.objects.bulk_create(
        [OrderItem(order=order, product=p, quantity=requested[p.sku]) for p in products]
    )
    return order
