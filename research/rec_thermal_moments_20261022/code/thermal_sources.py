"""Source-bound RR/DR kinetic loss and explicit prompt radiative escape.

Mao2017 supplies f=L/(k_B T alpha), indexed by the RECOMBINED electron
count. The primary product with unchanged donor alpha is deliberately named
a hybrid; the alternate loss is implied by differentiating the donor fit.
Binding, primary kinetic energy and Li core escape have distinct owners.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import numpy as np

from recombination_moments import RecombinationMoments, KB_J_K

UNIT = Path(__file__).resolve().parents[1]
EV_J = 1.602176634e-19


def mao_factor(temperature_K, parameters):
    """Return f and df/dlnT; Eq7 uses T_eV and NATURAL logarithms."""
    t = np.asarray(temperature_K, dtype=float) * KB_J_K / EV_J
    if np.any(~np.isfinite(t)) or np.any(t <= 0):
        raise ValueError('Mao temperature must be positive and finite')
    a0, b0, c0, a1, b1, a2, b2 = parameters
    lt = np.log(t)
    u = a1 * np.exp(-b1 * lt)
    v = a2 * np.exp(-b2 * lt)
    f = a0 * np.exp(-b0 * lt - c0 * lt**2) * (1 + v) / (1 + u)
    slope = -b0 - 2*c0*lt - b2*v/(1+v) + b1*u/(1+u)
    return f, f*slope


class ThermalSources:
    """Finite common-T, case-A, instantaneous primary-thermalization model.

    Smooth signed population trials are accepted for Newton iterations.
    Accepted solutions require the separately specified positivity gates.
    The continuation runner rejects nonzero initial/accepted neutron/tritium:
    no nuclear energy is owned here. Off-manifold signed Newton trials have a
    smooth numerical extension and carry no nuclear-energy closure claim.
    """
    def __init__(self, atomic, rr_closure='mao2017'):
        if rr_closure not in ('mao2017', 'rate_derivative'):
            raise ValueError('unknown RR kinetic closure')
        self.atomic = atomic
        self.closure = rr_closure
        self.moments = RecombinationMoments(atomic)
        lock = json.loads((UNIT/'provenance/MAO_SOURCE_LOCK.json').read_text())
        for row in lock['files']:
            path = UNIT/row['path']
            if path.stat().st_size != row['bytes'] or hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
                raise ValueError('MAO_SOURCE_CHANGED:'+row['path'])
        selected = UNIT/lock['selected_file']
        if hashlib.sha256(selected.read_bytes()).hexdigest() != lock['selected_sha256']:
            raise ValueError('MAO_SELECTED_SOURCE_CHANGED')
        self.rows = {(r['initial_Z'], r['initial_q']):r for r in json.loads(selected.read_text())['rows']}
        self.particle_weight = 1 + atomic.q
        self.downward_binding_J = np.zeros(21)
        for i in atomic.recombination_indices:
            self.downward_binding_J[i] = atomic.ionization_energy_J[i]-atomic.ionization_energy_J[i-1]

    def coefficients(self, temperature_K):
        out = self.moments.evaluate(temperature_K)
        if self.closure == 'mao2017':
            f = np.zeros(21)
            df = np.zeros(21)
            for i in self.atomic.recombination_indices:
                row = self.rows[(int(self.atomic.Z[i]), int(self.atomic.q[i]))]
                f[i], df[i] = mao_factor(temperature_K, row['a0_b0_c0_a1_b1_a2_b2'])
            a = out['rr_m3_s']
            da = out['drr_dlogT']
            out['rr_loss_J_m3_s'] = KB_J_K*temperature_K*a*f
            out['drr_loss_dlogT'] = KB_J_K*temperature_K*((a+da)*f+a*df)
            out['rr_loss_factor'] = f
        else:
            f = np.zeros(21)
            ii = self.atomic.recombination_indices
            f[ii] = out['rr_loss_J_m3_s'][ii]/(KB_J_K*temperature_K*out['rr_m3_s'][ii])
            out['rr_loss_factor'] = f
        out['loss_J_m3_s'] = out['rr_loss_J_m3_s'] + out['dr_loss_J_m3_s']
        out['dloss_dlogT'] = out['drr_loss_dlogT'] + out['ddr_loss_dlogT']
        return out

    def evaluate(self, Y, temperature_K, uv_scale, nb, network=None):
        Y = np.asarray(Y, dtype=float)
        if Y.shape != (21,) or not np.all(np.isfinite(Y)):
            raise ValueError('finite native isotope vector required')
        n = self.atomic.evaluate(Y, temperature_K, uv_scale, nb) if network is None else network
        coeff = self.coefficients(temperature_K)
        eta = float(self.particle_weight @ Y)
        if not math.isfinite(eta) or eta <= 0:
            raise ValueError('nonpositive gas particle abundance')
        ne = n['ne']
        loss = coeff['loss_J_m3_s']
        rr_loss = nb*ne*float(Y@coeff['rr_loss_J_m3_s'])
        dr_loss = nb*ne*float(Y@coeff['dr_loss_J_m3_s'])
        kinetic = n['primary_kinetic_power_W_m3']-rr_loss-dr_loss
        recombination_binding = nb*ne*float(Y@(self.downward_binding_J*(coeff['rr_m3_s']+coeff['dr_m3_s'])))
        escape = n['unresolved_core_power_W_m3']+recombination_binding+rr_loss+dr_loss
        ion_source = nb*float(self.atomic.ionization_energy_J@n['dY_dt'])
        residual = n['photo_absorbed_power_W_m3']-escape-kinetic-ion_source
        throughput = abs(n['photo_absorbed_power_W_m3'])+abs(escape)+abs(kinetic)+abs(ion_source)
        return dict(network=n, coefficients=coeff, eta=eta,
                    particle_source_per_baryon_s=float(self.particle_weight@n['dY_dt']),
                    kinetic_net_W_m3=kinetic, rr_cooling_W_m3=rr_loss,
                    dr_cooling_W_m3=dr_loss, recombination_binding_escape_W_m3=recombination_binding,
                    core_escape_W_m3=n['unresolved_core_power_W_m3'],
                    total_escape_W_m3=escape, ion_source_W_m3=ion_source,
                    energy_source_residual_W_m3=residual,
                    energy_source_residual_scaled=abs(residual)/max(throughput,1e-300))


def temperature_log_rhs(H, temperature_K, nb, eta, particle_source, kinetic_W_m3):
    """dlnT/dln(a), derived from du/dt+3H(u+p)=Q_kin."""
    return -2 + (2*kinetic_W_m3/(3*KB_J_K*temperature_K*nb)-particle_source)/(H*eta)
