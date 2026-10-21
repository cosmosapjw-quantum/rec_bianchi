"""Pinned PR147 model and analytic initial seed map; no trajectory solve.

Signed shear is a smooth coordinate. Historical pilot S>=0 rows keep their
original interpretation. The signed extension only defines a derivative at 0.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / 'vendor'
sys.path.insert(0, str(VENDOR))
from lrs_boltzmann import SourceLock  # noqa: E402
from canonical_fv import CanonicalMomentumFV, CanonicalFVSpecies  # noqa: E402


@lru_cache(maxsize=1)
def verify_source():
    source = json.loads((ROOT / 'provenance/SOURCE_MANIFEST.json').read_text())
    for name, expected in source['files'].items():
        if hashlib.sha256((VENDOR / name).read_bytes()).hexdigest() != expected:
            raise ValueError('PINNED_SOURCE_CHANGED:' + name)
    return source['source_commit']


@lru_cache(maxsize=1)
def cosmology():
    verify_source()
    lock = json.loads((VENDOR / 'REI_BACKGROUND_FAMILY_LOCK.json').read_text())
    c = lock['cosmology']
    return SourceLock(c['H0_per_s'], c['Omega_m'], c['Omega_r'],
                      c['Omega_lambda'], lock['clock']['a_ref'], 1 / 3), c['Tcmb0_K']


@lru_cache(maxsize=1)
def calibration_constants():
    src, _ = cosmology()
    grid = CanonicalMomentumFV(30., 0., 24, 12, 3)
    energy = np.sqrt(30. ** 2 + grid._q ** 2)
    q = float(np.sum(grid._numbers * grid._q ** 2 / energy)
              / grid.reference_energy_norm)
    km0 = math.sqrt(6) / 5 * (src.h0 / src.href) ** 2 * (
        .1 * src.omega_m / src.aref ** 3) * q
    kr0 = math.sqrt(6) / 5 * (src.h0 / src.href) ** 2 * (
        src.omega_r / src.aref ** 4)
    return km0, kr0


@dataclass(frozen=True)
class SeedMap:
    axes: tuple[float, float, float]
    amplitude: float
    radiation_seed: float
    amplitude_gradient: np.ndarray
    initial_tangents: np.ndarray


def make_model(signed_shear: float, matter: float, radiation: float):
    """Return (original model, SeedMap) with parameters in Frobenius units.

    The source admits |S|<sqrt(6), -1<=A<=2 and |k|<=.5. The finite
    verification fixture uses the historical S in [0,.1] and fixed stress grid.
    """
    values = np.asarray([signed_shear, matter, radiation])
    if np.iscomplexobj(values) or values.shape != (3,) or not np.isfinite(values).all():
        raise ValueError('REAL_FINITE_THREE_SEEDS_REQUIRED')
    s, m, r = map(float, values)
    if abs(s) >= math.sqrt(6):
        raise ValueError('INITIAL_SHEAR_OUTSIDE_SOURCE_DOMAIN')
    src, temperature = cosmology()
    km0, kr0 = calibration_constants()
    factor = 1 - s * s / 6
    km, kr = km0 * factor, kr0 * factor
    amp, k = m / km, r / kr
    if not (-1 <= amp <= 2 and abs(k) <= .5):
        raise ValueError('INITIAL_STRESS_OUTSIDE_POSITIVE_SOURCE_DOMAIN')
    model = CanonicalFVSpecies(src, temperature, 8,
        Sigma_ref=abs(s) / math.sqrt(2), orientation=int(np.sign(s)),
        kappa_gamma=k, kappa_nu=k, ne_source=None,
        mass_fraction=.1, massive_A=amp, mass_over_Tref=30.,
        radial_cells=24, angular_cells=12, subcell_gauss_order=3)
    da = np.array([2 * s * amp / (6 - s * s), 1 / km, 0.])
    dk = np.array([2 * s * k / (6 - s * s), 0., 1 / kr])
    z0 = np.zeros((40, 3))
    z0[2, 0] = 6 / (6 - s * s) ** 1.5
    for block in range(4):
        z0[4 + block * 9 + 2] = dk / 5
    da.flags.writeable = False
    z0.flags.writeable = False
    return model, SeedMap((s, m, r), amp, k, da, z0)
