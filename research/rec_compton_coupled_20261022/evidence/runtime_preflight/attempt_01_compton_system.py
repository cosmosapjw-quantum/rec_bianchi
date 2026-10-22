"""Native full63 gas Compton adapter with an explicit, unapplied bath ledger.

The inherited geometry, number network and Mao-hybrid RR closure are unchanged.
Only the log-temperature RHS row receives a source. ``actual_hot`` and
``planck_reference`` are exclusive CMB owners; both use the same dilute UV bins.
No Compton energy source is inserted into the photon hierarchy or Einstein
equations. Its opposite transfer is recorded only as bookkeeping.

All derivatives are with respect to the native scaled 63-vector. Solver trial
abundances may be signed; the source algebra does not divide by electron
fraction or photon monopole and does not clip those trial coordinates.
"""
from __future__ import annotations

import math
from pathlib import Path
import sys

import numpy as np

UNIT = Path(__file__).resolve().parents[1]
THERMAL = UNIT.parent / "rec_thermal_moments_20261022"
OMITTED = UNIT.parent / "rec_thermal_omitted_budget_20261022"
for _path in (THERMAL / "code", OMITTED / "code"):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from thermal_system import ThermalSystem, thermal_uv
from compton_budget import (
    A_RAD_J_M3_K4, KB_J_K, MEC2_J, SIGMA_T_C_M3_S,
    uv_reference_moments,
)

K_COMPTON = SIGMA_T_C_M3_S / MEC2_J
# Independently chosen Planck-reference bath, FROZEN_CONTRACT section 2.
# The actual hierarchy energy remains rho_crit * Omega_gamma * y[4] / a**4.
TCMB0_K = 2.7255
BRANCHES = ("actual_hot", "planck_reference")


class ComptonFull63(ThermalSystem):
    """Full63 adapter; ``yscale`` aliases the inherited 21 isotope scales."""

    size = 63

    def __init__(self, config, branch="actual_hot"):
        if branch not in BRANCHES:
            raise ValueError("unknown exclusive Compton branch: " + str(branch))
        super().__init__(config, rr_closure="mao2017")
        self.branch = branch
        self.yscale = self.scale
        self.uv_moments = uv_reference_moments(
            self.atomic.photon_energy_eV, self.atomic.photon_flux_bins_base,
            self.atomic.photon_bin_edges_eV,
            self.atomic.uv_config["number_power_index"],
        )
        self._uv_U = self.uv_moments["U_J_m3"]
        self._uv_M = self.uv_moments["M_J2_m3"]
        self._particle_weight = 1 + self.atomic.q

    def _compton_state(self, x, y, field=None):
        """Small algebraic state, with no atomic rate or momentum quadrature."""
        if field is None:
            field = self.geometry.fields(x, y[:40])
        T = math.exp(float(y[62]))
        Y = np.asarray(y[40:61]) * self.scale
        xe = float(self.atomic.q @ Y)
        eta = float(self._particle_weight @ Y)
        H, a = field["H"], field["a"]
        if not all(math.isfinite(v) and v > 0 for v in (T, eta, H, a)):
            raise ValueError("positive finite T, particle count, H and a required")
        uv = thermal_uv(x)[1]
        nb = self.geometry.baryon_number_density(x)
        U_per_E0 = (self.geometry.source.rhocrit_j_m3 *
                    self.geometry.model.omega_gamma / a**4)
        U_actual = U_per_E0 * float(y[4])
        Tr = TCMB0_K / a
        U_ref = A_RAD_J_M3_K4 * Tr**4
        U_uv, M_uv = uv * self._uv_U, uv * self._uv_M
        B_hot = -(8 * K_COMPTON / 3) * U_actual
        B_ref = (8 * K_COMPTON / 3) * U_ref * (Tr / T - 1)
        B_uv = (2 * K_COMPTON / 3) * (M_uv / (KB_J_K * T) - 4 * U_uv)
        B_selected = B_hot if self.branch == "actual_hot" else B_ref
        return dict(field=field, T=T, xe=xe, eta=eta, H=H, nb=nb,
                    U_per_E0=U_per_E0, U_actual=U_actual, Tr=Tr, U_ref=U_ref,
                    U_uv=U_uv, M_uv=M_uv, B_selected=B_selected,
                    B_uv=B_uv, B=B_selected+B_uv)

    def compton_logT_rhs(self, x, y):
        s = self._compton_state(x, y)
        return s["xe"] * s["B"] / (s["H"] * s["eta"])

    def compton_jacobian_row(self, x, y):
        """Analytic addition to row 62; includes the live photon E0 column."""
        s = self._compton_state(x, y)
        H, eta, xe = s["H"], s["eta"], s["xe"]
        field = s["field"]
        source, model = self.geometry.source, self.geometry.model
        hgrad = np.zeros(40)
        # Compact exact d(log H)/dy from the unchanged Geometry owner.
        hgrad[1] = -3 * source.h0**2 * field["Pi_matter_norm"] / H**2
        hgrad[2] = source.href**2 * y[2] / H**2
        hgrad[4] = source.h0**2 * model.omega_gamma / (2 * H**2 * field["a"]**4)
        hgrad[22] = source.h0**2 * model.omega_nu / (2 * H**2 * field["a"]**4)
        g = xe * s["B"] / (H * eta)
        row = np.zeros(63)
        row[:40] = -g * hgrad
        if self.branch == "actual_hot":
            row[4] -= xe / (H * eta) * (8 * K_COMPTON / 3) * s["U_per_E0"]
        # This quotient derivative remains regular when xe is exactly zero.
        row[40:61] = ((s["B"] / H) *
                      (self.atomic.q * eta - xe * self._particle_weight) /
                      eta**2) * self.scale
        dB_dlogT = -(2 * K_COMPTON / 3) * s["M_uv"] / (KB_J_K * s["T"])
        if self.branch == "planck_reference":
            dB_dlogT -= (8 * K_COMPTON / 3) * s["U_ref"] * s["Tr"] / s["T"]
        row[62] = xe * dB_dlogT / (H * eta)
        # tau_T has no source dependence; row[61] is exactly zero.
        return row

    def rhs(self, x, y):
        out = super().rhs(x, y)
        out[62] += self.compton_logT_rhs(x, y)
        return out

    def jac(self, x, y):
        out = super().jac(x, y)
        out[62] += self.compton_jacobian_row(x, y)
        return out

    def compton_terms(self, x, y):
        """Both candidate powers are reported; only one enters the equation."""
        s = self._compton_state(x, y)
        ne, T = s["nb"] * s["xe"], s["T"]
        Q_hot = -4 * K_COMPTON * ne * KB_J_K * T * s["U_actual"]
        Q_ref = 4 * K_COMPTON * ne * KB_J_K * s["U_ref"] * (s["Tr"] - T)
        Q_uv_recoil = K_COMPTON * ne * s["M_uv"]
        Q_uv_thermal = -4 * K_COMPTON * ne * KB_J_K * T * s["U_uv"]
        Q_uv = Q_uv_recoil + Q_uv_thermal
        Q_selected = Q_hot if self.branch == "actual_hot" else Q_ref
        # The backreaction diagnostic is defined on admitted positive-energy
        # states. Undefined trial-state ratios are not used in RHS/Jacobian.
        ratio = (abs(Q_selected) / (s["H"] * s["U_actual"])
                 if s["U_actual"] > 0 else float("nan"))
        factor = s["xe"] / (s["H"] * s["eta"])
        return dict(
            compton_selected_W_m3=Q_selected,
            compton_actual_hot_W_m3=Q_hot,
            compton_planck_reference_W_m3=Q_ref,
            compton_uv_W_m3=Q_uv,
            compton_uv_recoil_W_m3=Q_uv_recoil,
            compton_uv_thermal_W_m3=Q_uv_thermal,
            compton_total_W_m3=Q_selected+Q_uv,
            U_gamma_actual_J_m3=s["U_actual"],
            U_planck_reference_J_m3=s["U_ref"],
            T_planck_reference_K=s["Tr"],
            U_uv_J_m3=s["U_uv"], M_uv_J2_m3=s["M_uv"],
            compton_logT_rhs=factor*s["B"],
            compton_cmb_logT_rhs=factor*s["B_selected"],
            compton_uv_logT_rhs=factor*s["B_uv"],
            compton_backreaction_ratio=ratio,
        )

    def sample(self, x, y):
        """Physical-state sample, including the combined transfer ledger.

        The gas source is independently formed from kinetic plus binding
        source. Thus the four-store residual also checks the inherited
        photo/RR/DR partition, rather than only cancelling assigned copies.
        No opposite bath source in this dictionary is applied dynamically.
        """
        out = super().thermal_diagnostics(x, y)
        c = self.compton_terms(x, y)
        out["photo_rr_dr_source_energy_residual"] = out["source_energy_residual"]
        out["kinetic_net_without_compton_W_m3"] = out["kinetic_net_W_m3"]
        out["kinetic_net_W_m3"] += c["compton_total_W_m3"]
        out.update(c)
        gas = out["kinetic_net_W_m3"] + out["ion_source_W_m3"]
        cmb_bath = -c["compton_selected_W_m3"]
        uv_bath = -out["photo_absorbed_W_m3"] - c["compton_uv_W_m3"]
        escaped = out["total_escape_W_m3"]
        residual = math.fsum((gas, cmb_bath, uv_bath, escaped))
        throughput = math.fsum(abs(v) for v in (gas, cmb_bath, uv_bath, escaped))
        scaled = abs(residual) / max(throughput, 1e-300)
        radiation_source = (out["photo_absorbed_W_m3"] - escaped +
                            c["compton_total_W_m3"])
        out.update(
            gas_energy_source_W_m3=gas,
            gas_source_from_radiation_W_m3=radiation_source,
            compton_bath_source_W_m3=cmb_bath,
            uv_bath_source_W_m3=uv_bath,
            escaped_radiation_source_W_m3=escaped,
            transfer_ledger_residual_W_m3=residual,
            transfer_ledger_residual_scaled=scaled,
            source_energy_residual=scaled,
            gas_energy_source_J_per_baryon_per_x=
                radiation_source / (out["nb_m3"] * out["H_s"]),
        )
        return out

    def thermal_diagnostics(self, x, y):
        return self.sample(x, y)

    def diagnostics(self, x, y):
        # ThermalSystem dynamically calls our thermal_diagnostics, so its gas
        # input is already the new kinetic+binding source. Replace its explicit
        # old zero-bath assignments; all inherited geometry gates stay intact.
        out = super().diagnostics(x, y)
        c = self.compton_terms(x, y)
        total = c["compton_total_W_m3"]
        out["external_bath_W_m3"] = total
        out["bath_minus_escape_W_m3"] += total
        out.update(c)
        return out
