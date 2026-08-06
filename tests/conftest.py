from __future__ import annotations

import subprocess

import pytest


# The toolchain that produced ORIGINAL_HYREC_PORTABLE_BINARY_SHA256, as recorded
# by the release itself in state/PR04B2A_RECOVERY_INVENTORY.json. A compiled
# binary hash is a compiler artifact, not a physics invariant.
PINNED_BINARY_TOOLCHAIN = "gcc (Debian 14.2.0-19) 14.2.0"


def gcc_identity() -> str:
    """Return the first line of ``gcc --version``, or ``""`` if unavailable."""
    try:
        result = subprocess.run(
            ["gcc", "--version"], capture_output=True, text=True, check=True
        )
    except (OSError, subprocess.CalledProcessError):
        return ""
    return result.stdout.splitlines()[0].strip() if result.stdout else ""


@pytest.fixture(scope="session")
def binary_hash_is_meaningful() -> bool:
    """Whether compiled-binary hashes may be compared with the pinned value."""
    return gcc_identity() == PINNED_BINARY_TOOLCHAIN

SLOW_FILES = {
    'test_full_harmonic_deposition.py',
    'test_pair_cell_conductance.py',
    'test_recoil_bridge.py',
    'test_same_cell_regular.py',
    'test_thermal_deposition.py',
}


def pytest_collection_modifyitems(items):
    slow = pytest.mark.slow
    for item in items:
        if item.path.name in SLOW_FILES:
            item.add_marker(slow)
