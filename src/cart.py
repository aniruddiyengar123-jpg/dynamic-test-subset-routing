from collections.abc import Iterable
from decimal import Decimal


def calculate_total(items: Iterable[tuple[Decimal, int]]) -> Decimal:
    """Calculate a cart total from (unit price, quantity) pairs."""
    total = Decimal("0")
    for unit_price, quantity in items:
        if unit_price < 0:
            raise ValueError("unit prices must not be negative")
        if quantity < 0:
            raise ValueError("quantities must not be negative")
        total += unit_price * quantity
    return total
