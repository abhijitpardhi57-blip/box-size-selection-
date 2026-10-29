"""Box selection logic.

Pure Python, no Django imports, so it can be tested and reasoned about on its own.

How a box is chosen
-------------------
For every candidate box we run four checks, cheapest first:

1. total weight  <= box max weight
2. every single item fits the box in some rotation
3. total item volume <= box volume      (necessary, not sufficient)
4. a real 3D arrangement exists         (found with a heuristic, see try_pack)

Among the boxes that pass, the cheapest wins. Ties: smaller volume, then name.

Important property: a box is only ever recommended if try_pack produced a concrete,
verifiable placement. The heuristic can miss a tight packing that exists (3D bin
packing is NP-hard), but it can never claim a fit that does not exist.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from itertools import permutations
from typing import Iterable, Optional, Sequence, Tuple

# Upper bound on units per order. Keeps the packing search fast and bounded.
MAX_UNITS = 50

REASON_TOO_HEAVY = "too_heavy"
REASON_ITEM_TOO_LARGE = "item_too_large"
REASON_VOLUME = "volume_exceeded"
REASON_NO_ARRANGEMENT = "no_arrangement_found"

ZERO = Decimal(0)


class PackingError(ValueError):
    """Invalid input: bad dimensions, empty order, bad quantity, too many units."""


def _to_decimal(value) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


@dataclass(frozen=True)
class Item:
    """A product. Dimensions in cm, weight in kg."""

    sku: str
    length: Decimal
    width: Decimal
    height: Decimal
    weight: Decimal

    def __post_init__(self):
        for name in ("length", "width", "height", "weight"):
            value = _to_decimal(getattr(self, name))
            if value <= 0:
                raise PackingError(f"{self.sku}: {name} must be greater than zero.")
            object.__setattr__(self, name, value)

    @property
    def dims(self) -> Tuple[Decimal, Decimal, Decimal]:
        return (self.length, self.width, self.height)

    @property
    def volume(self) -> Decimal:
        return self.length * self.width * self.height


@dataclass(frozen=True)
class BoxSpec:
    """A shipping box. Internal dimensions in cm, max weight in kg."""

    name: str
    length: Decimal
    width: Decimal
    height: Decimal
    max_weight: Decimal
    cost: Decimal
    id: Optional[int] = None

    def __post_init__(self):
        for name in ("length", "width", "height", "max_weight"):
            value = _to_decimal(getattr(self, name))
            if value <= 0:
                raise PackingError(f"{self.name}: {name} must be greater than zero.")
            object.__setattr__(self, name, value)
        cost = _to_decimal(self.cost)
        if cost < 0:
            raise PackingError(f"{self.name}: cost cannot be negative.")
        object.__setattr__(self, "cost", cost)

    @property
    def dims(self) -> Tuple[Decimal, Decimal, Decimal]:
        return (self.length, self.width, self.height)

    @property
    def volume(self) -> Decimal:
        return self.length * self.width * self.height


@dataclass(frozen=True)
class Placement:
    """One item placed inside a box: corner (x, y, z) and size (dx, dy, dz)."""

    sku: str
    x: Decimal
    y: Decimal
    z: Decimal
    dx: Decimal
    dy: Decimal
    dz: Decimal


@dataclass(frozen=True)
class FitResult:
    box: BoxSpec
    fits: bool
    reason: Optional[str]
    total_weight: Decimal
    item_volume: Decimal
    utilization_percent: Decimal
    placements: Tuple[Placement, ...] = ()


@dataclass(frozen=True)
class Recommendation:
    best: Optional[FitResult]
    evaluated: Tuple[FitResult, ...]
    total_weight: Decimal
    unit_count: int


# --------------------------------------------------------------------------- input


def expand_units(order_lines: Iterable[Tuple[Item, int]]) -> list:
    """[(item, qty), ...] -> one Item per physical unit. Validates quantities."""
    lines = list(order_lines)
    if not lines:
        raise PackingError("Order has no items.")
    total = 0
    for item, qty in lines:
        if isinstance(qty, bool) or not isinstance(qty, int) or qty < 1:
            raise PackingError(f"{item.sku}: quantity must be a positive integer.")
        total += qty
    # Check the total *before* expanding so a huge quantity cannot exhaust memory.
    if total > MAX_UNITS:
        raise PackingError(
            f"Order has {total} units; at most {MAX_UNITS} are supported. "
            "Split it into several parcels."
        )
    return [item for item, qty in lines for _ in range(qty)]


# ----------------------------------------------------------------------- packing

# Different rotation preferences. try_pack tries each and keeps the first success.
_ROTATION_ORDERS = (
    lambda r: (r[2], -r[0], -r[1]),  # lie flat, longest side along x
    lambda r: (r[2], r[0], r[1]),  # lie flat, shortest side along x
    lambda r: (-r[2], -r[0], -r[1]),  # stand tall
)


def _fits_individually(item: Item, box: BoxSpec) -> bool:
    """Can the item fit in the empty box in some rotation? (sorted-dimension test)"""
    return all(i <= b for i, b in zip(sorted(item.dims), sorted(box.dims)))


def _overlaps(p: Placement, x, y, z, dx, dy, dz) -> bool:
    # Touching faces do not count as overlap.
    return (
        x < p.x + p.dx and p.x < x + dx
        and y < p.y + p.dy and p.y < y + dy
        and z < p.z + p.dz and p.z < z + dz
    )


def _find_position(box, unit, points, placed, rotation_key):
    rotations = sorted(set(permutations(unit.dims)), key=rotation_key)
    for x, y, z in sorted(points, key=lambda p: (p[2], p[1], p[0])):
        for dx, dy, dz in rotations:
            if x + dx > box.length or y + dy > box.width or z + dz > box.height:
                continue
            if any(_overlaps(p, x, y, z, dx, dy, dz) for p in placed):
                continue
            return (x, y, z), (dx, dy, dz)
    return None


def _pack_once(box, ordered_units, rotation_key):
    points = {(ZERO, ZERO, ZERO)}
    placed: list = []
    for unit in ordered_units:
        found = _find_position(box, unit, points, placed, rotation_key)
        if found is None:
            return None
        (x, y, z), (dx, dy, dz) = found
        placed.append(Placement(unit.sku, x, y, z, dx, dy, dz))
        points.discard((x, y, z))
        # New candidate corners: next to, behind and on top of the item just placed.
        for nx, ny, nz in ((x + dx, y, z), (x, y + dy, z), (x, y, z + dz)):
            if nx < box.length and ny < box.width and nz < box.height:
                points.add((nx, ny, nz))
    return tuple(placed)


def try_pack(box: BoxSpec, units: Sequence[Item]) -> Optional[Tuple[Placement, ...]]:
    """Extreme-point heuristic: biggest items first, each at the lowest free corner
    where it fits, trying all 6 rotations. Returns placements or None."""
    ordered = sorted(units, key=lambda u: (-u.volume, -max(u.dims), u.sku))
    for rotation_key in _ROTATION_ORDERS:
        result = _pack_once(box, ordered, rotation_key)
        if result is not None:
            return result
    return None


def placements_are_valid(box: BoxSpec, placements: Sequence[Placement]) -> bool:
    """Independent check: everything inside the box and nothing overlapping."""
    for i, p in enumerate(placements):
        if p.x < 0 or p.y < 0 or p.z < 0:
            return False
        if p.x + p.dx > box.length or p.y + p.dy > box.width or p.z + p.dz > box.height:
            return False
        for q in placements[i + 1:]:
            if _overlaps(q, p.x, p.y, p.z, p.dx, p.dy, p.dz):
                return False
    return True


# ---------------------------------------------------------------------- selection


def _utilization(item_volume: Decimal, box_volume: Decimal) -> Decimal:
    return (item_volume / box_volume * 100).quantize(Decimal("0.01"))


def check_fit(box: BoxSpec, units: Sequence[Item]) -> FitResult:
    total_weight = sum((u.weight for u in units), ZERO)
    item_volume = sum((u.volume for u in units), ZERO)
    utilization = _utilization(item_volume, box.volume)

    def failed(reason: str) -> FitResult:
        return FitResult(box, False, reason, total_weight, item_volume, utilization)

    if total_weight > box.max_weight:
        return failed(REASON_TOO_HEAVY)
    if any(not _fits_individually(u, box) for u in units):
        return failed(REASON_ITEM_TOO_LARGE)
    if item_volume > box.volume:
        return failed(REASON_VOLUME)
    placements = try_pack(box, units)
    if placements is None:
        return failed(REASON_NO_ARRANGEMENT)
    return FitResult(box, True, None, total_weight, item_volume, utilization, placements)


def recommend_box(
    boxes: Iterable[BoxSpec], order_lines: Iterable[Tuple[Item, int]]
) -> Recommendation:
    units = expand_units(order_lines)
    results = tuple(check_fit(box, units) for box in boxes)
    fitting = [r for r in results if r.fits]
    best = (
        min(fitting, key=lambda r: (r.box.cost, r.box.volume, r.box.name, r.box.id or 0))
        if fitting
        else None
    )
    total_weight = sum((u.weight for u in units), ZERO)
    return Recommendation(best, results, total_weight, len(units))
