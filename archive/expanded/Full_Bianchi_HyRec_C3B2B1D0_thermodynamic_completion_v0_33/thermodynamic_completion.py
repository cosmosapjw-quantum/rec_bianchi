"""Finite-volume Rybicki thermodynamic completion."""
from __future__ import annotations
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent


class ThermodynamicCompletedKernel:
    def __init__(self):
        data = np.load(HERE / "thermodynamic_completed_kernel.npz")
        self.mode_measure = data["mode_measure_m3"]
        self.Pi = data["dilute_equilibrium_weight_m3"]
        self.z = data["cell_activity"]
        self.rate = data["completed_rate_sInv"]
        self.occupation_gain = data["occupation_gain_sInv"]
        self.loss = data["completed_loss_sInv"]

    def linear_harmonic_action(self, coefficients):
        coefficients = np.asarray(coefficients)
        output = np.zeros_like(coefficients)
        for ell in range(coefficients.shape[0]):
            output[ell] = (
                self.occupation_gain[ell] @ coefficients[ell]
                - self.loss * coefficients[ell]
            )
        return output

    def bose_frequency_action(self, occupation):
        occupation = np.asarray(occupation)
        number_action = np.zeros_like(occupation, dtype=float)

        for i in range(len(occupation)):
            for j in range(i + 1, len(occupation)):
                flux = (
                    self.rate[0, i, j]
                    * self.mode_measure[j]
                    * occupation[j]
                    * (1.0 + occupation[i])
                    - self.rate[0, j, i]
                    * self.mode_measure[i]
                    * occupation[i]
                    * (1.0 + occupation[j])
                )
                number_action[i] += flux
                number_action[j] -= flux

        return number_action / self.mode_measure
