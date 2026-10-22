"""THERM02 current-state RR/Compton adapter; every energy quantity is SI.

The immutable THERM01 donor owns all number coefficients, isotope inventory,
geometry and the exact compact map. This adapter owns the Mao hybrid RR
kinetic moment, scalar Compton contraction and explicitly separate gas/bath
ledgers. The external Planck bath is not an inferred grey photon spectrum.
Neither Compton branch modifies the hierarchy or the Einstein constraint.
"""
from __future__ import annotations

from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import sys
import time

import numpy as np

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor/therm01/code"))
import thermal as _donor

from geometry import C as C_LIGHT

KB = _donor.KB
EV_J = _donor.EV_J
THOMSON = _donor.THOMSON  # Already sigma_T*c, in m^3/s.
XEND = _donor.XEND
lift34 = _donor.lift34
restrict63 = _donor.restrict63
R_EXT = _donor.R_EXT
P_EXT = _donor.P_EXT
M_E = 9.1093837139e-31
H_PLANCK = 6.62607015e-34
HBAR = H_PLANCK / (2 * math.pi)
A_RAD = math.pi**2 * KB**4 / (15 * HBAR**3 * C_LIGHT**3)
K_COMPTON = THOMSON / (M_E * C_LIGHT**2)
LEDGER_COLUMNS = ("absorption", "escape", "adiabatic_work",
                  "CMB_or_reference", "UV_Compton")
RR_CLOSURES = ("mao2017", "rate_derivative")
COMPTON_BRANCHES = ("off", "actual_hot", "planck_reference")


@lru_cache(maxsize=1)
def verify_reused_files():
    """Verify the immutable retained payload once per Python process."""
    manifest = json.loads((ROOT / "provenance/REUSED_FILES.json").read_text())
    for row in manifest["files"]:
        data = (ROOT / row["path"]).read_bytes()
        blob = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
        if (len(data) != row["bytes"] or
                hashlib.sha256(data).hexdigest() != row["sha256"] or
                blob != row["git_blob_sha"]):
            raise ValueError("REUSED_SOURCE_CHANGED:" + row["path"])
    return manifest


def compton_coefficients(branch, *, ne, nb, eta, temperature, w, H,
                         U_gamma, scale_factor, U_uv, M_uv):
    """Current-state scalar moments, with signed gas heating Q in W/m^3.

    M_uv is the energy-weighted UV density in J^2/m^3. A is dimensionless;
    B and B-A*w have units K per unit x. The direct-volume form is retained
    independently for diagnostics. ``off`` disables both Compton sources.
    """
    if branch not in COMPTON_BRANCHES:
        raise ValueError("unknown Compton branch")
    values = (ne, nb, eta, temperature, w, H, U_gamma, scale_factor, U_uv, M_uv)
    if not all(math.isfinite(float(v)) for v in values):
        raise ValueError("nonfinite Compton point")
    if (ne < 0 or nb <= 0 or eta <= 0 or temperature <= 0 or H <= 0 or
            U_gamma < 0 or scale_factor <= 0 or U_uv < 0 or M_uv < 0):
        raise ValueError("invalid Compton density/temperature/moment")
    U_ref = T_ref = U_star = R_star = 0.
    Q_C = Q_UV = A = B = 0.
    if branch != "off":
        if branch == "actual_hot":
            U_star = U_gamma
            Q_C = -4 * K_COMPTON * ne * KB * temperature * U_gamma
        else:
            T_ref = 2.7255 / scale_factor
            U_ref = A_RAD * T_ref**4
            U_star = U_ref
            R_star = 4 * U_ref * T_ref
            Q_C = 4 * K_COMPTON * ne * KB * U_ref * (T_ref - temperature)
        Q_UV = K_COMPTON * ne * (M_uv - 4 * KB * temperature * U_uv)
        x_e = ne / nb
        A = 8 * K_COMPTON * x_e * (U_star + U_uv) / (3 * H * eta)
        B = K_COMPTON * x_e * (R_star + M_uv / KB) / H
    direct = (Q_C + Q_UV) / (nb * KB * H)
    affine = B - A * w
    affine_scale = abs(B) + abs(A * w) + abs(direct)
    return dict(Q_C=Q_C, Q_UV=Q_UV, A=A, B=B, w_source=affine,
                direct_w_source=direct, U_gamma=U_gamma, U_ref=U_ref,
                T_ref=T_ref, U_uv=U_uv, M_uv=M_uv,
                affine_direct_scaled=abs(affine-direct)/max(affine_scale, 1e-300))


def frozen_subflow(w, A, B, dx):
    """Exact fixture for fixed x,Y,geometry: w'=-(2+A)w+B.

    This is not a solver for the coupled system and is not used by its RHS.
    expm1 keeps the source increment accurate for small positive dx.
    """
    if not all(math.isfinite(float(v)) and v >= 0 for v in (w, A, B, dx)):
        raise ValueError("nonnegative finite frozen-subflow input required")
    damping = 2 + A
    exponent = -damping * dx
    return w * math.exp(exponent) + B * (-math.expm1(exponent)) / damping


class CoupledThermalAtomic(_donor.ThermalAtomic):
    """Unchanged donor number generator plus six shared Mao factors."""

    def __init__(self, emax=60., rr_closure="mao2017"):
        verify_reused_files()
        if rr_closure not in RR_CLOSURES:
            raise ValueError("unknown RR kinetic closure")
        self.rr_closure = rr_closure
        super().__init__(emax, bins=64)
        selected = json.loads((ROOT / "vendor/pr121/data/mao2017_selected.json").read_text())
        rows = selected["rows"]
        keys = tuple((int(r["initial_Z"]), int(r["initial_q"])) for r in rows)
        expected = ((1, 1), (2, 1), (2, 2), (3, 1), (3, 2), (3, 3))
        if keys != expected or any(q != z-int(r["recombined_s"])+1
                                   for (z, q), r in zip(keys, rows)):
            raise ValueError("Mao six-row charge mapping changed")
        self.mao_keys = keys
        self.mao_parameters = np.array([r["a0_b0_c0_a1_b1_a2_b2"] for r in rows])
        self.mao_parameters.setflags(write=False)
        self.mao_map = np.array([keys.index((int(self.Z[i]), int(self.q[i])))
                                for i in self.recombination_indices], dtype=int)
        self.mao_map.setflags(write=False)
        self.binding_per_recombination_J = np.zeros(self.size)
        self.binding_per_recombination_J[self.recombination_indices] = (
            self.transition_energy_eV[self.recombination_indices-1] * EV_J)
        self.binding_per_recombination_J.setflags(write=False)
        energy_J = self.photon_energy_eV * EV_J
        # Actual GL4 nodes/flux weights, not bin centres. No contraction in RHS.
        self.U_uv_base = float(self.photon_flux_bins_base @ energy_J) / C_LIGHT
        self.M_uv_base = float(self.photon_flux_bins_base @ energy_J**2) / C_LIGHT

    def mao_factors_six(self, temperature):
        """f and df/dlnT at the six electronic ions; T input is Kelvin."""
        t = float(temperature) * KB / EV_J
        if not math.isfinite(t) or t <= 0:
            raise ValueError("Mao temperature must be positive and finite")
        lt = math.log(t)
        a0, b0, c0, a1, b1, a2, b2 = self.mao_parameters.T
        u = a1 * np.exp(-b1 * lt)
        v = a2 * np.exp(-b2 * lt)
        f = a0 * np.exp(-b0 * lt - c0 * lt**2) * (1 + v) / (1 + u)
        df = f * (-b0 - 2*c0*lt - b2*v/(1+v) + b1*u/(1+u))
        return f, df

    def moments(self, temperature, rates=None):
        if self.rr_closure == "rate_derivative":
            return super().moments(temperature, rates)
        rates = self.rates(temperature, 0.) if rates is None else rates
        f, _df = self.mao_factors_six(temperature)
        rr = np.zeros(self.size)
        dr = np.zeros(self.size)
        ii = self.recombination_indices
        rr[ii] = KB * temperature * rates["rr_m3_s"][ii] * f[self.mao_map]
        # Retain signed DR amplitudes and their summed resonance energy moment.
        dr[self._dr_indices] = KB * _donor.CM3_M3 * temperature**(-1.5) * np.sum(
            self._dr_c * self._dr_E * np.exp(-self._dr_E/temperature), axis=1)
        if not np.isfinite(rr+dr).all() or np.any(rr < 0) or np.any(dr < 0):
            raise ValueError("nonfinite/negative summed recombination energy moment")
        return rr, dr

    def thermal_evaluate(self, Y, T, uv, nb):
        rates = self.rates(T, uv)
        ne = nb * float(self.q @ Y)
        decay = rates["D"] @ Y
        dY = rates["G0"] @ Y + ne * (rates["Gne"] @ Y) + decay
        beta_rr, beta_dr = self.moments(T, rates)
        alpha = rates["rr_m3_s"] + rates["dr_m3_s"]
        rr_cooling = nb * ne * float(Y @ beta_rr)
        dr_cooling = nb * ne * float(Y @ beta_dr)
        cooling = rr_cooling + dr_cooling
        binding_escape = nb * ne * float(Y @ (self.binding_per_recombination_J * alpha))
        return dict(dY_dt=dY, ne=ne,
                    absorbed=nb*float(Y @ rates["absorbed_power_per_ion_W"]),
                    heat=nb*float(Y @ rates["primary_kinetic_power_per_ion_W"]),
                    cooling=cooling, rr_cooling=rr_cooling, dr_cooling=dr_cooling,
                    escape=cooling+binding_escape, binding_escape=binding_escape,
                    uv_energy=uv*self.U_uv_base, uv_moment=uv*self.M_uv_base,
                    decay_max=float(np.max(abs(decay))))


class CoupledThermalSystem(_donor.ThermalSystem):
    """Conditional full63/compact34 thermal dynamics with current-state baths."""

    def __init__(self, config, full=False):
        verify_reused_files()
        _donor.verify_donor()
        self.config = dict(config)
        if self.config.get("cmb_branch") not in COMPTON_BRANCHES:
            raise ValueError("explicit cmb_branch required")
        if self.config.get("rr_closure") not in RR_CLOSURES:
            raise ValueError("explicit rr_closure required")
        self.full = bool(full)
        self.size = 63 if full else 34
        self.geometry = _donor.Geometry(config["Sigma_F"], config["matter_A"], config["radiation_A"])
        self.atomic = CoupledThermalAtomic(config["Emax_eV"], config["rr_closure"])
        self.scale = self.atomic.scales
        Y = self.atomic.initial_Y
        eta = float(Y.sum() + self.atomic.q @ Y)
        initial = np.r_[self.geometry.initial, Y/self.scale, 0., 1.5*eta*config["T0_K"]]
        lifted_initial = lift34(restrict63(initial))
        self.initial_compact_residual = float(np.max(abs(lifted_initial-initial)))
        # Retain the donor's 8-epsilon admission of isotope division roundoff.
        # The pinned initial D+ fraction differs from H+ by 2.71e-20. Do not
        # silently alter the full63 IC to erase that independently stored bit.
        if (not np.array_equal(lifted_initial[:40], initial[:40]) or
                np.any(initial[40:61][[0, 5, 6]] != 0) or
                self.initial_compact_residual > 8*np.finfo(float).eps):
            raise ValueError("initial state outside donor compact34 admission")
        self.y0 = initial if full else restrict63(initial)
        self.started = time.perf_counter()
        self.nrhs = 0
        self.min_trial_T = math.inf
        self.max_trial_T = -math.inf

    def point(self, x, state):
        y = self.expand(state)
        if y.shape != (63,) or not np.isfinite(y).all():
            raise ValueError("finite full63 state required")
        Y = y[40:61] * self.scale
        eta = float(Y.sum() + self.atomic.q @ Y)
        if not math.isfinite(eta) or eta <= 0:
            raise ValueError("positive finite particle abundance required")
        T = 2*y[62]/(3*eta)
        self.min_trial_T = min(self.min_trial_T, T)
        self.max_trial_T = max(self.max_trial_T, T)
        z = 21*math.exp(-x)-1
        uv = .5*(1+math.tanh((7-z)/.8))*self.config["uv_multiplier"]
        nb = self.geometry.baryon_number_density(x)
        n = self.atomic.thermal_evaluate(Y, T, uv, nb)
        f = self.geometry.fields(x, y[:40])
        U_gamma = (self.geometry.source.rhocrit_j_m3 * self.geometry.model.omega_gamma
                   * y[4] / f["a"]**4)
        n["compton"] = compton_coefficients(self.config["cmb_branch"],
            ne=n["ne"], nb=nb, eta=eta, temperature=T, w=y[62], H=f["H"],
            U_gamma=U_gamma, scale_factor=f["a"], U_uv=n["uv_energy"], M_uv=n["uv_moment"])
        return y, Y, eta, T, uv, nb, n, f

    def full_rhs_from_point(self, p):
        y, Y, eta, T, uv, nb, n, f = p
        H = f["H"]
        out = np.empty(63)
        out[:40] = self.geometry.rhs_from_fields(y[:40], f, n["ne"])
        out[40:61] = n["dY_dt"] / self.scale / H
        out[61] = THOMSON * n["ne"] / H
        out[62] = -2*y[62] + (n["heat"]-n["cooling"])/(nb*KB*H) + n["compton"]["w_source"]
        return out

    def rhs(self, x, state):
        self.nrhs += 1
        if time.perf_counter()-self.started > 180.:
            raise TimeoutError("THERM02 cooperative 180 s ceiling")
        out = self.full_rhs_from_point(self.point(x, state))
        return out if self.full else restrict63(out)

    def diagnose_from_point(self, p, x):
        """Reuse one evaluated physical point for RHS and all diagnostics."""
        y, Y, eta, T, uv, nb, n, f = p
        H = f["H"]
        c = n["compton"]
        derivative = self.full_rhs_from_point(p)
        eth = KB*y[62]
        eion = float(self.atomic.ionization_energy_J @ Y)
        dion = float(self.atomic.ionization_energy_J @ n["dY_dt"])
        gas = n["absorbed"]-n["escape"]+c["Q_C"]+c["Q_UV"]
        cmb_bath, uv_bath = -c["Q_C"], -n["absorbed"]-c["Q_UV"]
        transfer = gas + cmb_bath + uv_bath + n["escape"]
        transfer_scale = abs(gas)+abs(cmb_bath)+abs(uv_bath)+abs(n["escape"])
        local = KB*H*derivative[62] + dion + 2*H*eth - gas/nb
        local_scale = abs(KB*H*derivative[62])+abs(dion)+abs(2*H*eth)+abs(gas/nb)
        atomic_residual = n["absorbed"]-n["escape"]-(n["heat"]-n["cooling"])-nb*dion
        atomic_scale = abs(n["absorbed"])+abs(n["escape"])+abs(n["heat"]-n["cooling"])+abs(nb*dion)
        lhs = 3*H*H
        rhs = 3*self.geometry.source.h0**2*(f["dust_energy_norm"]+f["massive_energy_norm"]+
            f["rad_energy_norm"]+self.geometry.source.omega_lambda)+3*f["s"]**2
        out = dict(elapsed_Myr=y[0]/self.geometry.source.href/_donor.MYR_S,
            T_K=T, eta=eta, nb_m3=nb, ne_m3=n["ne"], tau_T=y[61], H_s=H, uv_scale=uv,
            epsilon_th_J=eth, epsilon_ion_J=eion, epsilon_total_J=eth+eion,
            absorbed_W_baryon=n["absorbed"]/nb, escaped_W_baryon=n["escape"]/nb,
            heat_W_baryon=n["heat"]/nb, cooling_W_baryon=n["cooling"]/nb,
            rr_cooling_W_baryon=n["rr_cooling"]/nb, dr_cooling_W_baryon=n["dr_cooling"]/nb,
            binding_escape_W_baryon=n["binding_escape"]/nb,
            work_W_baryon=2*H*eth, local_ledger_W_baryon=local,
            local_ledger_scaled=abs(local)/max(local_scale, 1e-300),
            local_transfer_W_baryon=transfer/nb,
            local_transfer_scaled=abs(transfer)/max(transfer_scale, 1e-300),
            atomic_source_scaled=abs(atomic_residual)/max(atomic_scale, 1e-300),
            compton_W_baryon=c["Q_C"]/nb, uv_compton_W_baryon=c["Q_UV"]/nb,
            gas_source_W_baryon=gas/nb, cmb_bath_W_baryon=cmb_bath/nb,
            uv_bath_W_baryon=uv_bath/nb, escaped_owner_W_baryon=n["escape"]/nb,
            U_gamma_J_m3=c["U_gamma"], U_ref_J_m3=c["U_ref"], T_ref_K=c["T_ref"],
            U_uv_J_m3=c["U_uv"], M_uv_J2_m3=c["M_uv"],
            compton_A=c["A"], compton_B_K=c["B"],
            compton_over_HUgamma=abs(c["Q_C"])/max(H*c["U_gamma"], 1e-300),
            compton_over_HUref=(abs(c["Q_C"])/max(H*c["U_ref"], 1e-300)
                               if self.config["cmb_branch"] == "planck_reference" else 0.),
            affine_direct_scaled=c["affine_direct_scaled"],
            trace_energy_fraction=(nb*(eth+eion)+n["uv_energy"])/(lhs/_donor.KAPPA_T),
            einstein_residual=abs(lhs-rhs)/lhs, decay_max=n["decay_max"],
            signed_observables=self.geometry.normalized(x, y[:40], f))
        return out

    def diagnostics(self, x, state):
        return self.diagnose_from_point(self.point(x, state), x)

    @staticmethod
    def ledger_from_point(p):
        y, Y, eta, T, uv, nb, n, f = p
        factor = nb*f["H"]
        return np.array([n["absorbed"]/factor, n["escape"]/factor, 2*KB*y[62],
                         n["compton"]["Q_C"]/factor, n["compton"]["Q_UV"]/factor])

    def ledger_integrand(self, x, state):
        return self.ledger_from_point(self.point(x, state))
