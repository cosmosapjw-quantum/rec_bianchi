"""Native full63 thermal continuation of exact saved REC119 states.

Only the temperature equation is newly closed. Geometry/radiation and number
operators are reused by source identity; no inherited trajectory is rerun.
"""
from __future__ import annotations

import math
from pathlib import Path
import sys
import numpy as np

UNIT = Path(__file__).resolve().parents[1]
DONOR = UNIT.parent/'rec_rei_hheli_sandbox_20261021'
sys.path.insert(0, str(DONOR/'code'))
from coupled import CoupledSystem, thermal_uv, THOMSON
from geometry import KB
from thermal_sources import ThermalSources, temperature_log_rhs


class ThermalSystem(CoupledSystem):
    size = 63

    def __init__(self, config, rr_closure='mao2017'):
        super().__init__(config)
        self.thermal = ThermalSources(self.atomic, rr_closure)
        self.y0 = np.r_[self.y0, math.log(thermal_uv(0)[0])]

    def point(self, x, y):
        field = self.geometry.fields(x, y[:40])
        T = math.exp(float(y[62]))
        uv = thermal_uv(x)[1]
        nb = self.geometry.baryon_number_density(x)
        network = self.atomic.evaluate(y[40:61]*self.scale, T, uv, nb)
        return field, network, T, uv, 0.0, nb

    def rhs(self, x, y):
        parent = super().rhs(x, y)
        field, network, T, uv, _, nb = self.point(x, y)
        th = self.thermal.evaluate(y[40:61]*self.scale, T, uv, nb, network)
        last = temperature_log_rhs(field['H'],T,nb,th['eta'],
                                  th['particle_source_per_baryon_s'],th['kinetic_net_W_m3'])
        return np.r_[parent,last]

    def jac(self, x, y):
        jac = np.zeros((63,63))
        jac[:62,:62] = super().jac(x, y)
        field, network, T, uv, _, nb = self.point(x,y)
        H = field['H']
        Y = y[40:61]*self.scale
        th = self.thermal.evaluate(Y,T,uv,nb,network)
        co = th['coefficients']
        eta = th['eta']
        w = self.thermal.particle_weight
        rates_T = co['drr_dlogT']+co['ddr_dlogT']
        dR = self.atomic._transition_matrix(rates_T,upward=False)
        F_T = network['ne']*(dR@Y)
        jac[40:61,62] = F_T/self.scale/H
        L = co['loss_J_m3_s']
        LT = co['dloss_dlogT']
        qkin_per_b = th['kinetic_net_W_m3']/nb
        particle_rate = th['particle_source_per_baryon_s']
        numerator = 2*qkin_per_b/(3*KB*T)-particle_rate
        qkin_Y = uv*self.atomic._primary_W - nb*((self.atomic.q@Y)*L+(L@Y)*self.atomic.q)
        numerator_Y = 2*qkin_Y/(3*KB*T)-w@network['jac']
        jac[62,40:61] = ((numerator_Y/eta-numerator*w/eta**2)/H)*self.scale
        _, hgrad = self.geometry.jacobian_blocks(x,y[:40],field,network['ne'] if self.opacity else 0.0)
        jac[62,:40] = -numerator/(H*eta)*hgrad
        qkin_T = -network['ne']*float(Y@LT)
        numerator_T = 2*(qkin_T-qkin_per_b)/(3*KB*T)-float(w@F_T)
        jac[62,62] = numerator_T/(H*eta)
        return jac

    def thermal_diagnostics(self,x,y):
        field, network, T, uv, _, nb = self.point(x,y)
        Y=y[40:61]*self.scale
        th=self.thermal.evaluate(Y,T,uv,nb,network)
        u_per_b=1.5*KB*T*th['eta']+float(self.atomic.ionization_energy_J@Y)
        return dict(T_K=T,H_s=field['H'],nb_m3=nb,ne_m3=network['ne'],
                    gas_particles_per_baryon=th['eta'],
                    elapsed_Myr=y[0]/self.geometry.source.href/31557600e6,
                    tau_T=y[61],photo_absorbed_W_m3=network['photo_absorbed_power_W_m3'],
                    photo_primary_W_m3=network['primary_kinetic_power_W_m3'],
                    rr_cooling_W_m3=th['rr_cooling_W_m3'],dr_cooling_W_m3=th['dr_cooling_W_m3'],
                    core_escape_W_m3=th['core_escape_W_m3'],
                    binding_escape_W_m3=th['recombination_binding_escape_W_m3'],
                    total_escape_W_m3=th['total_escape_W_m3'],kinetic_net_W_m3=th['kinetic_net_W_m3'],
                    ion_source_W_m3=th['ion_source_W_m3'],
                    source_energy_residual=th['energy_source_residual_scaled'],
                    gas_energy_J_per_baryon=u_per_b,
                    gas_energy_source_J_per_baryon_per_x=(network['photo_absorbed_power_W_m3']-th['total_escape_W_m3'])/(nb*field['H']),
                    work_J_per_baryon_per_x=3*KB*T*th['eta'])

    def diagnostics(self,x,y):
        # Parent diagnostics contains a prescribed-temperature source formula.
        # Replace that formula with the actual dynamic-T balance. The dummy
        # point tuple's tdx=0 is never published as a temperature derivative.
        out=super().diagnostics(x,y)
        d=self.thermal_diagnostics(x,y)
        out['net_required_gas_input_W_m3']=d['kinetic_net_W_m3']+d['ion_source_W_m3']
        out['bath_minus_escape_W_m3']=-d['total_escape_W_m3']
        out['external_bath_W_m3']=0.0
        out['core_escape_W_m3']=d['core_escape_W_m3']
        out.pop('unresolved_core_W_m3',None)
        return out
