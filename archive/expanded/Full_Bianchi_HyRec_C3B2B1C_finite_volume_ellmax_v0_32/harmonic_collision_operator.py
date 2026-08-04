"""Matrix-free scalar harmonic collision operator."""
from __future__ import annotations
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent

class HarmonicCollisionOperator:
    def __init__(self):
        data=np.load(HERE/"finite_volume_legendre_kernel.npz")
        self.gain=data["physical_gain_sInv"]
        self.loss=data["within_core_loss_sInv"]
        self.ell_max=self.gain.shape[0]-1
        self.n_frequency=self.gain.shape[1]

    def apply_coefficients(self, coefficients):
        coefficients=np.asarray(coefficients)
        output=np.zeros_like(coefficients)
        offset=self.ell_max
        for ell in range(self.ell_max+1):
            for m in range(-ell,ell+1):
                mi=m+offset
                output[ell,mi]=(
                    self.gain[ell]@coefficients[ell,mi]
                    -self.loss*coefficients[ell,mi]
                )
        return output
