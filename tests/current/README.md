# Current regression suite

Run the maintained current product regressions from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tests/current/run_current_tests.py
```

The runner derives release markers and audio totals from current canonical
sources before executing the extracted JavaScript and Python regressions. It
does not read the historical phase test originals. Those originals remain
individually runnable at their existing paths as historical evidence.
