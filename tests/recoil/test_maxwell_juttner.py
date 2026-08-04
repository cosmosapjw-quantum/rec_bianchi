import numpy as np
from scipy.integrate import quad
from scipy.special import kv

from full_bianchi_hyrec.recoil.event_weight import (
    maxwell_juttner_momentum_normalization_dimensionless,
)


def test_maxwell_juttner_bessel_normalization_at_z10():
    z = 10.0
    direct = 4.0 * np.pi * quad(
        lambda q: q * q * np.exp(-z * np.sqrt(1.0 + q * q)),
        0.0,
        np.inf,
        epsabs=1e-15,
        epsrel=1e-13,
        limit=500,
    )[0]
    expected = 4.0 * np.pi * kv(2, z) / z
    implemented = maxwell_juttner_momentum_normalization_dimensionless(z)

    assert abs(direct / expected - 1.0) < 2e-13
    assert abs(implemented / expected - 1.0) < 2e-15
