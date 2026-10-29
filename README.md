# Box Selection System

A small Django service that recommends the cheapest shipping box that can actually hold an order.

Given the items in an order (each with dimensions and weight) and the available boxes (each with
internal dimensions, a max weight and a cost), it answers: **which box should the warehouse use?**

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations packing               # first time only; commit the generated files
python manage.py migrate
python manage.py seed_demo                            # demo products + boxes
python manage.py runserver
```

Try it:

```bash
curl -X POST http://127.0.0.1:8000/api/recommend-box/ \
  -H "Content-Type: application/json" \
  -d '{"items": [{"sku": "MUG", "quantity": 2}]}'
```

Manage products and boxes in the admin: `python manage.py createsuperuser`, then `/admin/`.

## API

| Method | URL | Purpose |
|---|---|---|
| POST | `/api/recommend-box/` | Recommend a box. Saves nothing. |
| POST | `/api/orders/` | Save an order and the box recommended for it. |
| GET | `/api/orders/<id>/` | Read a saved order. |

Request body (both POST endpoints; `/api/orders/` also needs `"reference"`, unique per order):

```json
{"reference": "ORD-1001", "items": [{"sku": "MUG", "quantity": 2}, {"sku": "BOOK"}]}
```

`quantity` is optional and defaults to 1. Repeated SKUs are merged.

Response of `/api/recommend-box/`:

```json
{
  "recommended_box": {"id": 2, "name": "Box S", "cost": "25.00", "max_weight_kg": "5.000",
                      "inner_dimensions_cm": {"length": "25.00", "width": "20.00", "height": "15.00"}},
  "message": null,
  "total_weight_kg": "0.700",
  "unit_count": 2,
  "utilization_percent": "32.00",
  "placements": [
    {"sku": "MUG", "position": {"x": "0", "y": "0", "z": "0"}, "size": {"x": "12.00", "y": "10.00", "z": "10.00"}},
    {"sku": "MUG", "position": {"x": "12.00", "y": "0", "z": "0"}, "size": {"x": "12.00", "y": "10.00", "z": "10.00"}}
  ],
  "evaluated_boxes": [{"box": "Mailer XS", "fits": false, "reason": "item_too_large"},
                      {"box": "Box S", "fits": true, "reason": null}]
}
```

`evaluated_boxes` explains why each box was rejected, so the warehouse can see the decision:
`too_heavy`, `item_too_large`, `volume_exceeded`, `no_arrangement_found`.

Status codes: `200` ok, `201` order created, `400` invalid input or unknown SKU (lists `unknown_skus`),
`404` order not found, `405` wrong method, `409` duplicate order reference.

If no single box can hold the order, `/api/recommend-box/` returns `200` with `"recommended_box": null`
and a message. A saved order in that case gets status `needs_review`.

## How the recommendation works

For every active box, in this order (cheap checks first):

1. **Weight**: total weight of all units <= box max weight.
2. **Each item fits alone**: its sorted dimensions are <= the box's sorted dimensions (rotation allowed).
3. **Volume**: total item volume <= box volume. Necessary, not sufficient.
4. **Real arrangement**: an extreme-point packing heuristic places every unit inside the box.
   Biggest items first, each at the lowest free corner where it fits, trying all 6 rotations,
   and three rotation preferences (flat / flat-other-way / tall).

Among the boxes that pass, the **cheapest** wins. Ties go to the smaller box, then the name.

The logic lives in `packing/algorithm.py`. It does not import Django, so it is easy to test and read.
`services.py` loads data from the database and calls it; `views.py` is only HTTP.

## Assumptions

- Dimensions in cm, weights in kg. Box dimensions are **internal** (usable) dimensions.
- Max weight is a limit on the contents. Packaging weight is not modelled.
- Items may be rotated in any of the 6 axis-aligned orientations. Items are rigid boxes
  (no squeezing or nesting) and can be stacked freely.
- One order goes into one box. If it cannot, the order is flagged for manual review (no multi-parcel splitting).
- Decimal arithmetic is used throughout, so boundary cases (exactly at the limit) are exact.

## Limitations (deliberate, and worth knowing)

- 3D bin packing is NP-hard. The heuristic is **conservative**: if it says a box fits, it really does
  (placements are verified in the tests by an independent checker), but on a very tight packing it may
  say "no arrangement found" even though a perfect packing exists. The effect is a slightly larger box
  being chosen, never a box that is too small.
- Orders are limited to 50 units (`MAX_UNITS`) to keep the search bounded. Larger orders get a `400`.
- The API has no authentication and the POST endpoints are CSRF-exempt, which is fine for this exercise
  but must be changed before any real use.
- Non-positive dimensions are rejected by model validators (admin/`full_clean`) and again by the
  algorithm layer, but not by a database constraint.

## Tests

```bash
python manage.py test -v 2
```

- `packing/tests/test_algorithm.py`: pure logic (selection, tie-breaks, every rejection reason, rotation,
  tight packings, validation). Runs without a database; also runnable with
  `python -m unittest packing.tests.test_algorithm`.
- `packing/tests/test_api.py`: endpoints, validation, order persistence, atomicity, models, seed command.

CI: `.github/workflows/ci.yml` runs the suite on Python 3.11 and 3.12 for every push.
Test output is recorded in `TEST_OUTPUT.md`.

## Project layout

```
config/                 Django project (settings, urls, wsgi)
packing/algorithm.py    pure box-selection logic
packing/models.py       Product, Box, Order, OrderItem
packing/services.py     database <-> algorithm glue
packing/views.py        JSON endpoints
packing/admin.py        admin screens
packing/management/     seed_demo command
packing/tests/          unit + API tests
AI_USAGE.md             how AI tools were used
```
