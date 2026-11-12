from decimal import Decimal

import pytest

from src.payment import total_with_tax


def test_total_with_tax_uses_fractional_rate():
    assert total_with_tax(Decimal("10.00"), Decimal("0.08")) == Decimal("10.8000")


@pytest.mark.parametrize(
    ("amount", "tax_rate"),
    [(Decimal("-1"), Decimal("0.1")), (Decimal("1"), Decimal("-0.1"))],
)
def test_total_with_tax_rejects_negative_values(amount, tax_rate):
    with pytest.raises(ValueError):
        total_with_tax(amount, tax_rate)
