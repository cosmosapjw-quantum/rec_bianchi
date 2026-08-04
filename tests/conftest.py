from __future__ import annotations

import pytest

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
