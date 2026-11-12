from decimal import Decimal


def total_with_tax(amount: Decimal, tax_rate: Decimal) -> Decimal:
    """Return an amount including a fractional tax rate."""
    if amount < 0:
        raise ValueError("amount must not be negative")
    if tax_rate < 0:
        raise ValueError("tax_rate must not be negative")
    return amount * (Decimal("1") + tax_rate)
