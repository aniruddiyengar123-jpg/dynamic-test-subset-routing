from pathlib import Path

import pytest

from router.test_router import load_mapping, select_tests


@pytest.fixture
def mapping():
    return load_mapping()


@pytest.mark.parametrize(
    ("changed_file", "expected"),
    [
        ("src/auth.py", ["tests/test_auth.py"]),
        ("src/payment.py", ["tests/test_payment.py"]),
        ("src/cart.py", ["tests/test_cart.py"]),
    ],
)
def test_source_change_selects_only_its_mapped_test(changed_file, expected, mapping):
    selected, reason = select_tests([changed_file], mapping)
    assert selected == expected
    assert reason == "all changed files have test mappings"


def test_multiple_mapped_changes_select_union_without_duplicates(mapping):
    selected, _ = select_tests(["src/auth.py", "src/auth.py", "src/cart.py"], mapping)
    assert selected == ["tests/test_auth.py", "tests/test_cart.py"]


@pytest.mark.parametrize(
    ("changed_files", "expected_reason"),
    [
        (["README.md"], "shared file"),
        (["notes.txt"], "no test mapping"),
        (["requirements.txt"], "shared file"),
        (["src/auth.py", "src/new_feature.py"], "no test mapping"),
        ([], "no changed files"),
    ],
)
def test_unknown_shared_or_empty_changes_fall_back_to_full_suite(
    changed_files, expected_reason, mapping
):
    selected, reason = select_tests(changed_files, mapping)
    assert selected == []
    assert expected_reason in reason


def test_mapping_paths_are_normalized_to_forward_slashes(mapping):
    selected, _ = select_tests([r"src\auth.py"], mapping)
    assert selected == ["tests/test_auth.py"]
