"""Select and run the pytest subset associated with changed files."""

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MAPPING = PROJECT_ROOT / "config" / "test_mapping.json"


def _relative_path(value: str, description: str) -> str:
    normalized = value.replace("\\", "/").strip()
    path = PurePosixPath(normalized)
    if not normalized or path.is_absolute() or ".." in path.parts:
        raise ValueError(f"{description} must be a non-empty relative path: {value!r}")
    return path.as_posix()


def load_mapping(path: Path = DEFAULT_MAPPING) -> dict[str, Any]:
    """Load and validate the test mapping JSON."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"could not load test mapping {path}: {error}") from error

    if not isinstance(data, dict):
        raise ValueError("mapping root must be a JSON object")

    raw_mapping = data.get("test_mapping")
    raw_shared = data.get("shared_files")
    if not isinstance(raw_mapping, dict) or not isinstance(raw_shared, list):
        raise ValueError("mapping must define object 'test_mapping' and list 'shared_files'")

    test_mapping: dict[str, list[str]] = {}
    for source, tests in raw_mapping.items():
        if not isinstance(source, str) or not isinstance(tests, list) or not tests:
            raise ValueError("each test_mapping entry must map a source path to a non-empty list")
        source_path = _relative_path(source, "source path")
        if source_path in test_mapping:
            raise ValueError(f"duplicate source path after normalization: {source_path}")

        normalized_tests = []
        for test in tests:
            if not isinstance(test, str):
                raise ValueError(f"test paths for {source_path} must be strings")
            test_path = _relative_path(test, "test path")
            if not test_path.startswith("tests/"):
                raise ValueError(f"mapped test must be under tests/: {test_path}")
            if not (PROJECT_ROOT / test_path).is_file():
                raise ValueError(f"mapped test does not exist: {test_path}")
            normalized_tests.append(test_path)
        test_mapping[source_path] = normalized_tests

    shared_files = []
    for pattern in raw_shared:
        if not isinstance(pattern, str):
            raise ValueError("shared_files patterns must be strings")
        shared_files.append(_relative_path(pattern, "shared-file pattern"))

    if not test_mapping:
        raise ValueError("test_mapping must contain at least one source mapping")
    return {"test_mapping": test_mapping, "shared_files": shared_files}


def select_tests(changed_files: list[str], mapping: dict[str, Any]) -> tuple[list[str], str]:
    """Return selected test paths and an explanation; an empty selection means full suite."""
    if not changed_files:
        return [], "no changed files were detected"

    normalized_changed = [_relative_path(path, "changed path") for path in changed_files]
    tests: set[str] = set()
    test_mapping = mapping["test_mapping"]
    shared_patterns = mapping["shared_files"]

    for changed in normalized_changed:
        if any(fnmatch.fnmatchcase(changed, pattern) for pattern in shared_patterns):
            return [], f"shared file changed: {changed}"
        mapped = test_mapping.get(changed)
        if mapped is None:
            return [], f"no test mapping for changed file: {changed}"
        tests.update(mapped)

    return sorted(tests), "all changed files have test mappings"


def get_changed_files(base: str, head: str) -> list[str]:
    """Get paths changed between two Git revisions."""
    result = subprocess.run(
        ["git", "diff", "--name-only", "-z", base, head, "--"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [path for path in result.stdout.split("\0") if path]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", help="base Git revision (required unless --changed-files is used)")
    parser.add_argument("--head", default="HEAD", help="head Git revision (default: HEAD)")
    parser.add_argument(
        "--changed-files",
        nargs="+",
        metavar="PATH",
        help="use explicit changed paths instead of querying Git",
    )
    parser.add_argument(
        "--mapping",
        type=Path,
        default=DEFAULT_MAPPING,
        help="path to mapping JSON (default: config/test_mapping.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print the selected pytest command without running tests",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if args.changed_files is None and not args.base:
        print("error: --base is required unless --changed-files is supplied", file=sys.stderr)
        return 2

    try:
        mapping = load_mapping(args.mapping.resolve())
        changed_files = (
            args.changed_files
            if args.changed_files is not None
            else get_changed_files(args.base, args.head)
        )
        selected_tests, reason = select_tests(changed_files, mapping)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    targets = selected_tests or ["tests"]
    print(f"Changed files: {', '.join(changed_files) if changed_files else '(none)'}")
    print(f"Selection: {'mapped subset' if selected_tests else 'full suite'} ({reason})")
    command = [sys.executable, "-m", "pytest", *targets]
    print("Command:", " ".join(command))
    if args.dry_run:
        return 0

    return subprocess.run(command, cwd=PROJECT_ROOT, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
