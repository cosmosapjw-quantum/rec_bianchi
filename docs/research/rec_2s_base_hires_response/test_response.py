"""Targeted negative parser tests; prior O1/O2/O3 tests are not invoked."""
import importlib.util
from pathlib import Path
import sys

import numpy as np
import pytest

SPEC = importlib.util.spec_from_file_location("rec_base_hires_checker", Path(__file__).with_name("check_response.py"))
checker = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = checker
SPEC.loader.exec_module(checker)


@pytest.mark.parametrize("data,nvirt", [
    (b"6 1 2 3 4\n", 2),
    (b"6 1 2 3 4\n7 1 2 3\n", 2),
    (b"6 1 nan 3 4\n", 1),
    (b"6 1 -2 3 4\n", 1),
    (b"7 1 2 3 4\n6 1 2 3 4\n", 2),
])
def test_parser_rejects_unsupported_or_invalid_data(data, nvirt):
    with pytest.raises(ValueError):
        checker.parse_table(data, nvirt)


def test_parser_preserves_columns_and_decimal_tokens():
    tokens, values = checker.parse_table(b"6.0000 1e-2 2.5000 3 4\n7.000 0 1.250 2 3\n", 2)
    assert tokens[0] == ["6.0000", "1e-2", "2.5000", "3", "4"]
    assert values.shape == (2, 5)
    assert np.array_equal(values[:, 2], [2.5, 1.25])


def test_one_field_derivative_at_all_frozen_cases():
    # Same nine fields as the run; complex-step is an independent derivative.
    import cmath
    from fractions import Fraction
    for lam in (2, 8, 32):
        for alpha in (-.125, 0., .125):
            for u in (.25, .75):
                f, derivative = checker.field(u, lam, alpha)
                step = 1e-25
                z = lam*u + (alpha+step*1j)*u*(1-u)
                oracle = (1/(cmath.exp(z)-1)).imag/step
                assert f > 0
                assert derivative == pytest.approx(oracle, rel=64*np.finfo(float).eps, abs=0)
    wt = checker.weights(.75, .25, np.exp)
    assert wt[:4] == [1, 2, 1., float(Fraction(5, 8))]
    assert wt[4] == 1.+np.exp(-256.)
