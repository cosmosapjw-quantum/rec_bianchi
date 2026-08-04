"""Import every module in the package and report the ones that fail.

CI checks out only committed files, so a module that exists on the author's
disk but was never `git add`-ed disappears.  Any tracked file importing it
then dies during pytest collection, which aborts the whole run before a
single test executes.  The same shape catches a dependency that is imported
at module scope but missing from the extra CI installs.

Running this immediately after the install step turns that failure into an
explicit list of module names, seconds into the job, instead of a collection
traceback after the suite has already spun up.
"""
from __future__ import annotations

import importlib
import pkgutil
import sys
import traceback

import full_bianchi_hyrec


def main() -> int:
    failures: list[tuple[str, BaseException]] = []
    for module in pkgutil.walk_packages(
        full_bianchi_hyrec.__path__, full_bianchi_hyrec.__name__ + "."
    ):
        try:
            importlib.import_module(module.name)
        except BaseException as exc:  # noqa: BLE001 - report, never mask
            failures.append((module.name, exc))

    if not failures:
        return 0

    print(f"{len(failures)} module(s) failed to import:", file=sys.stderr)
    for name, exc in failures:
        print(f"\n--- {name}: {type(exc).__name__}: {exc}", file=sys.stderr)
        traceback.print_exception(type(exc), exc, exc.__traceback__, file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
