from __future__ import annotations

import subprocess

import pytest

# The toolchain that produced ORIGINAL_HYREC_PORTABLE_BINARY_SHA256, as recorded
# by the release itself in state/PR04B2A_RECOVERY_INVENTORY.json. A compiled
# binary's hash is a property of the compiler, not of the physics, so any other
# gcc emits different bytes from identical sources. Tests that pin that hash
# must gate on this, or they fail everywhere but the authoring machine.
PINNED_BINARY_TOOLCHAIN = 'gcc (Debian 14.2.0-19) 14.2.0'


def gcc_identity() -> str:
    """First line of ``gcc --version``, or the empty string if unavailable."""
    try:
        result = subprocess.run(
            ['gcc', '--version'], capture_output=True, text=True, check=True
        )
    except (OSError, subprocess.CalledProcessError):
        return ''
    return result.stdout.splitlines()[0].strip() if result.stdout else ''


@pytest.fixture(scope='session')
def binary_hash_is_meaningful() -> bool:
    """Whether compiled-binary hashes can be compared against pinned constants.

    Shared rather than per-file: the same pinned hash has now appeared in two
    separate test modules, and each new one would otherwise reintroduce a
    failure that says nothing about the science.
    """
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
