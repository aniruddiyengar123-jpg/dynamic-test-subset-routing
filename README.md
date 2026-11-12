# Dynamic Test-Subset Routing

This project runs only the pytest files associated with changed source files.
The routing configuration is in `config/test_mapping.json`; each exact source
path maps to one or more test files.

## How routing works

`router/test_router.py` compares two Git revisions, reads changed paths, and
selects the union of their mapped tests. It runs the full `tests/` suite when:

- there are no changed files;
- any changed file matches a `shared_files` pattern; or
- any changed file has no test mapping.

This fail-safe means a partially understood change can never silently skip
tests. Git and configuration errors are reported as errors rather than being
treated as successful test runs.

## Run locally

Install the test dependency and route changes since a base revision:

```powershell
python -m pip install -r requirements.txt
python router/test_router.py --base origin/main --head HEAD
```

For a preview without executing pytest:

```powershell
python router/test_router.py --base origin/main --head HEAD --dry-run
```

To preview a particular change directly (useful when testing the router):

```powershell
python router/test_router.py --changed-files src/auth.py --dry-run
```

That selects only `tests/test_auth.py`. `src/payment.py` selects only
`tests/test_payment.py`, and `src/cart.py` selects only `tests/test_cart.py`.
For example, `python router/test_router.py --changed-files README.md --dry-run`
selects the full suite because the file is unmapped. To run every test without
routing, use `python -m pytest`.

## Update the mapping

Add a source-to-test entry to `test_mapping` for every independently testable
source file. Add shared or high-impact files to `shared_files` so they trigger
the full suite. Paths use forward slashes and are relative to the repository
root. Every mapped test file must exist under `tests/`.

GitHub Actions runs the complete test suite (`python -m pytest -q`) on pushes
to `main` and on pull requests targeting `main`. The local router remains
available for selecting a focused subset when comparing Git revisions.
