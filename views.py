import json
from typing import Dict

from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from . import services
from .algorithm import PackingError, Recommendation
from .models import Order


class BadRequest(Exception):
    pass


# --------------------------------------------------------------------- parsing


def _parse_json(request) -> dict:
    try:
        data = json.loads(request.body or b"")
    except ValueError:  # JSONDecodeError and UnicodeDecodeError both subclass ValueError
        raise BadRequest("Request body must be valid JSON.")
    if not isinstance(data, dict):
        raise BadRequest("JSON body must be an object.")
    return data


def _parse_items(data: dict) -> Dict[str, int]:
    """Validate 'items' and merge repeated SKUs: {sku: total_quantity}."""
    items = data.get("items")
    if not isinstance(items, list) or not items:
        raise BadRequest("'items' must be a non-empty list.")
    merged: Dict[str, int] = {}
    for index, entry in enumerate(items):
        if not isinstance(entry, dict):
            raise BadRequest(f"items[{index}] must be an object.")
        sku = entry.get("sku")
        quantity = entry.get("quantity", 1)
        if not isinstance(sku, str) or not sku.strip():
            raise BadRequest(f"items[{index}].sku must be a non-empty string.")
        # bool is a subclass of int in Python, so reject it explicitly.
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 1:
            raise BadRequest(f"items[{index}].quantity must be a positive integer.")
        sku = sku.strip()
        merged[sku] = merged.get(sku, 0) + quantity
    return merged


# ----------------------------------------------------------------- serializing


def _box_dict(box) -> dict:
    return {
        "id": box.id,
        "name": box.name,
        "cost": str(box.cost),
        "max_weight_kg": str(box.max_weight),
        "inner_dimensions_cm": {
            "length": str(box.length),
            "width": str(box.width),
            "height": str(box.height),
        },
    }


def _recommendation_dict(rec: Recommendation) -> dict:
    best = rec.best
    return {
        "recommended_box": _box_dict(best.box) if best else None,
        "message": None if best else services.NO_BOX_MESSAGE,
        "total_weight_kg": str(rec.total_weight),
        "unit_count": rec.unit_count,
        "utilization_percent": str(best.utilization_percent) if best else None,
        "placements": [
            {
                "sku": p.sku,
                "position": {"x": str(p.x), "y": str(p.y), "z": str(p.z)},
                "size": {"x": str(p.dx), "y": str(p.dy), "z": str(p.dz)},
            }
            for p in (best.placements if best else ())
        ],
        "evaluated_boxes": [
            {"box": r.box.name, "fits": r.fits, "reason": r.reason} for r in rec.evaluated
        ],
    }


def _order_dict(order: Order) -> dict:
    box = order.recommended_box
    return {
        "id": order.id,
        "reference": order.reference,
        "status": order.status,
        "note": order.note,
        "created_at": order.created_at.isoformat(),
        "items": [
            {"sku": i.product.sku, "quantity": i.quantity}
            for i in sorted(order.items.all(), key=lambda i: i.product.sku)
        ],
        "recommended_box": (
            {"id": box.id, "name": box.name, "cost": str(box.cost)} if box else None
        ),
    }


def _error(message: str, status: int, **extra) -> JsonResponse:
    return JsonResponse({"error": message, **extra}, status=status)


# ----------------------------------------------------------------------- views


@csrf_exempt  # token-less JSON API for this exercise; add real auth before production
@require_POST
def recommend_box_view(request):
    """POST /api/recommend-box/  {"items": [{"sku": "MUG", "quantity": 2}]}
    Pure query: nothing is saved."""
    try:
        requested = _parse_items(_parse_json(request))
        rec = services.recommend(requested)
    except BadRequest as exc:
        return _error(str(exc), 400)
    except services.UnknownSkuError as exc:
        return _error("Unknown SKU(s).", 400, unknown_skus=exc.skus)
    except PackingError as exc:
        return _error(str(exc), 400)
    return JsonResponse(_recommendation_dict(rec))


@csrf_exempt
@require_POST
def create_order_view(request):
    """POST /api/orders/  {"reference": "ORD-1", "items": [...]}
    Saves the order and the box recommended for it."""
    try:
        data = _parse_json(request)
        reference = data.get("reference")
        if not isinstance(reference, str) or not reference.strip() or len(reference.strip()) > 64:
            raise BadRequest("'reference' must be a non-empty string of at most 64 characters.")
        reference = reference.strip()
        requested = _parse_items(data)
        if Order.objects.filter(reference=reference).exists():
            return _error(f"Order '{reference}' already exists.", 409)
        with transaction.atomic():
            rec = services.recommend(requested)
            order = services.create_order(reference, requested, rec)
    except BadRequest as exc:
        return _error(str(exc), 400)
    except services.UnknownSkuError as exc:
        return _error("Unknown SKU(s).", 400, unknown_skus=exc.skus)
    except PackingError as exc:
        return _error(str(exc), 400)
    except IntegrityError:  # lost a race on the unique reference
        return _error(f"Order '{reference}' already exists.", 409)
    order = Order.objects.select_related("recommended_box").prefetch_related("items__product").get(pk=order.pk)
    return JsonResponse({"order": _order_dict(order), "recommendation": _recommendation_dict(rec)}, status=201)


@require_GET
def order_detail_view(request, order_id: int):
    """GET /api/orders/<id>/"""
    try:
        order = (
            Order.objects.select_related("recommended_box")
            .prefetch_related("items__product")
            .get(pk=order_id)
        )
    except Order.DoesNotExist:
        return _error("Order not found.", 404)
    return JsonResponse(_order_dict(order))
