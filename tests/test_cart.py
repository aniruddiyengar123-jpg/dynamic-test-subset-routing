from decimal import Decimal

import pytest

from src.cart import calculate_total


def test_calculate_total_sums_prices_and_quantities():
    assert calculate_total(
        [(Decimal("2.50"), 2), (Decimal("1.25"), 4)]
    ) == Decimal("10.00")


@pytest.mark.parametrize(
    "items",
    [[(Decimal("-1"), 1)], [(Decimal("1"), -1)]],
)
def test_calculate_total_rejects_negative_inputs(items):
    with pytest.raises(ValueError):
        calculate_total(items)
