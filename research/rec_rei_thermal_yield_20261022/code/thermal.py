"""THERM01 bounded dynamic thermal/ionic-yield owner; SI units throughout.

The pinned donor owns atomic coefficients, inventory, invariant maps, geometry.
This module owns actual-T chemistry, recombination energy moments and diagnostics.
Fitted-rate derivative cooling is conditional, not measured cooling accuracy.
"""
from __future__ import annotations
import math
from pathlib import Path
import sys
sys.dont_write_bytecode = True
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT/'vendor/rei_pr220'
sys.path.insert(0, str(VENDOR/'code'))
from compact_system import verify_donor, restrict, lift, R, P
from coupled import THOMSON
from geometry import Geometry, KB, KAPPA_T
from atomic_network import AtomicNetwork, EV_J, CM3_M3, _readonly

XEND = math.log(7.)
MYR_S = 31557600e6
R_EXT = np.zeros((34,63)); R_EXT[:33,:62] = R; R_EXT[33,62] = 1
P_EXT = np.zeros((63,34)); P_EXT[:62,:33] = P; P_EXT[62,33] = 1

def restrict63(y):
    y=np.asarray(y)
    if y.shape[0]!=63: raise ValueError('expected full63')
    return np.concatenate((restrict(y[:62]),y[62:63]),axis=0)

def lift34(v):
    v=np.asarray(v)
    if v.shape[0]!=34: raise ValueError('expected compact34')
    return np.concatenate((lift(v[:33]),v[33:34]),axis=0)

class ThermalAtomic(AtomicNetwork):
    def __init__(self, emax=60., bins=64):
        if not math.isfinite(emax) or not 13.6 < emax <= 60.:
            raise ValueError('THERM01 source requires 13.6 < Emax <= 60 eV')
        if bins not in (64,128): raise ValueError('only frozen 64/128-bin source checks')
        self.base_bins=bins
        super().__init__(uv_cutoff_eV=emax)

    def _prepare_spectrum(self, cutoff):
        # Q1: fixed GL4 in unchanged threshold-split energy bins. Only this
        # adapter changes; donor coefficients/files and physical source do not.
        from numpy.polynomial.legendre import leggauss
        field=dict(self.model['photon_field'],base_log_bins=self.base_bins,
            energy_max_eV=60.,quadrature='fixed Gauss-Legendre4 within energy bins')
        self.model['photon_field']=field
        emin=field['energy_min_eV'];emax=float(cutoff)
        thresholds=list(self.transition_energy_eV[self.photo_indices])+[64.39]
        edges=np.unique(np.r_[np.geomspace(emin,emax,self.base_bins+1),
            [t for t in thresholds if emin<t<emax]])
        nodes,weights=leggauss(4)
        midpoint=(edges[:-1]+edges[1:])/2
        halfwidth=(edges[1:]-edges[:-1])/2
        energy=(midpoint[:,None]+halfwidth[:,None]*nodes).ravel()
        density=energy**field['number_power_index']
        raw_weights=(halfwidth[:,None]*weights).ravel()*density
        sigma,inner=self.photo_cross_sections(energy)
        normalization=field['late_Gamma_HI_s']/float(sigma[1]@raw_weights)
        flux=normalization*raw_weights
        self.uv_config=dict(field,actual_energy_max_eV=emax,
            actual_bin_count=len(edges)-1,quadrature_nodes=len(energy),within_bin_GL_order=4)
        self.photon_bin_edges_eV=_readonly(edges)
        self.photon_energy_eV=_readonly(energy)
        self.photon_flux_bins_base=_readonly(flux)
        self.photo_sigma_m2=_readonly(sigma)
        self.li1s_photo_sigma_m2=_readonly(inner)
        self._photo_s=_readonly(sigma@flux)
        self._li1s_photo_s=_readonly(inner@flux)
        self._absorbed_W=_readonly((sigma*(energy*EV_J))@flux)
        self._inner_absorbed_W=_readonly((inner*(energy*EV_J))@flux)
        self._core_W=_readonly(np.zeros(self.size))
        self._primary_W=_readonly((sigma*((energy[None,:]-self.transition_energy_eV[:,None])*EV_J))@flux)
        self._Gphoto=_readonly(self._transition_matrix(self._photo_s,upward=True))
        if np.any(inner!=0):
            raise ValueError('unexpected core channel inside admitted source support')

    def moments(self, temperature, rates=None):
        rates=self.rates(temperature,0.) if rates is None else rates
        a,b,t0,t1,c,t2=self._rr_parameters.T
        u,v=np.sqrt(temperature/t0),np.sqrt(temperature/t1)
        exp=np.exp(-t2/temperature)
        B=b+c*exp; b1=c*t2/temperature*exp
        theta=(1-B)/(2*(1+u))+(1+B)/(2*(1+v))+b1*(np.log1p(u)-np.log1p(v))
        rr=np.zeros(21);dr=np.zeros(21)
        rr[self.recombination_indices]=KB*temperature*rates['rr_m3_s'][self.recombination_indices]*theta
        dr[self._dr_indices]=KB*CM3_M3*temperature**(-1.5)*np.sum(
            self._dr_c*self._dr_E*np.exp(-self._dr_E/temperature),axis=1)
        if not np.isfinite(rr+dr).all() or np.any(rr<0) or np.any(dr<0):
            raise ValueError('nonfinite/negative summed recombination energy moment')
        return rr,dr

    def thermal_evaluate(self,Y,T,uv,nb):
        # Same immutable adjacent generator and electron coupling as donor;
        # explicit new owner avoids donor's prescribed thermal diagnostics.
        rates=self.rates(T,uv)
        ne=nb*float(self.q@Y)
        photo=rates['G0']@Y
        rec=ne*(rates['Gne']@Y)
        decay=rates['D']@Y
        beta_rr,beta_dr=self.moments(T,rates)
        alpha=rates['rr_m3_s']+rates['dr_m3_s']
        beta=beta_rr+beta_dr
        chi=np.zeros(21)
        chi[self.recombination_indices]=self.transition_energy_eV[self.recombination_indices-1]*EV_J
        absorbed=nb*float(Y@rates['absorbed_power_per_ion_W'])
        heat=nb*float(Y@rates['primary_kinetic_power_per_ion_W'])
        cooling=nb*ne*float(Y@beta)
        binding_escape=nb*ne*float(Y@(chi*alpha))
        uv_energy=float(rates['photon_flux_bins']@(self.photon_energy_eV*EV_J))/299792458.
        return dict(dY_dt=photo+rec+decay,ne=ne,absorbed=absorbed,heat=heat,
            cooling=cooling,escape=cooling+binding_escape,binding_escape=binding_escape,
            uv_energy=uv_energy,decay_max=float(np.max(abs(decay))))

class ThermalSystem:
    def __init__(self, config, full=False):
        verify_donor()
        self.config=dict(config);self.full=full;self.size=63 if full else 34
        self.geometry=Geometry(config['Sigma_F'],config['matter_A'],config['radiation_A'])
        self.atomic=ThermalAtomic(config['Emax_eV'])
        self.scale=self.atomic.scales
        Y=self.atomic.initial_Y
        eta=float(Y.sum()+self.atomic.q@Y)
        initial=np.r_[self.geometry.initial,Y/self.scale,0.,1.5*eta*config['T0_K']]
        self.y0=initial if full else restrict63(initial)
        self.started=time.perf_counter(); self.nrhs=0
        self.min_trial_T=math.inf;self.max_trial_T=-math.inf

    def expand(self,y):return np.asarray(y) if self.full else lift34(y)

    def point(self,x,y):
        y=self.expand(y)
        Y=y[40:61]*self.scale
        eta=float(Y.sum()+self.atomic.q@Y)
        T=2*y[62]/(3*eta)
        self.min_trial_T=min(self.min_trial_T,T);self.max_trial_T=max(self.max_trial_T,T)
        # Atomic rates perform the admitted 100..1e6 K guard, including trials.
        z=21*math.exp(-x)-1
        uv=.5*(1+math.tanh((7-z)/.8))*self.config['uv_multiplier']
        nb=self.geometry.baryon_number_density(x)
        network=self.atomic.thermal_evaluate(Y,T,uv,nb)
        field=self.geometry.fields(x,y[:40])
        return y,Y,eta,T,uv,nb,network,field

    def full_rhs_from_point(self,p):
        y,Y,eta,T,uv,nb,n,f=p
        out=np.empty(63);H=f['H']
        out[:40]=self.geometry.rhs_from_fields(y[:40],f,n['ne'])
        out[40:61]=n['dY_dt']/self.scale/H
        out[61]=THOMSON*n['ne']/H
        out[62]=-2*y[62]+(n['heat']-n['cooling'])/(nb*KB*H)
        return out

    def rhs(self,x,y):
        self.nrhs+=1
        if time.perf_counter()-self.started>180.:
            raise TimeoutError('THERM01 cooperative 180 s ceiling')
        out=self.full_rhs_from_point(self.point(x,y))
        return out if self.full else restrict63(out)

    def diagnostics(self,x,state):
        p=self.point(x,state); y,Y,eta,T,uv,nb,n,f=p;H=f['H']
        derivative=self.full_rhs_from_point(p)
        eth=KB*y[62];eion=float(self.atomic.ionization_energy_J@Y)
        dion=float(self.atomic.ionization_energy_J@n['dY_dt'])
        local=KB*H*derivative[62]+dion+2*H*eth-(n['absorbed']-n['escape'])/nb
        rho=3*H*H/KAPPA_T
        lhs=3*H*H
        rhs=3*self.geometry.source.h0**2*(f['dust_energy_norm']+f['massive_energy_norm']+
            f['rad_energy_norm']+self.geometry.source.omega_lambda)+3*f['s']**2
        obs=self.geometry.normalized(x,y[:40],f)
        return dict(elapsed_Myr=y[0]/self.geometry.source.href/MYR_S,T_K=T,
            eta=eta,nb_m3=nb,ne_m3=n['ne'],tau_T=y[61],H_s=H,uv_scale=uv,
            epsilon_th_J=eth,epsilon_ion_J=eion,epsilon_total_J=eth+eion,
            absorbed_W_baryon=n['absorbed']/nb,escaped_W_baryon=n['escape']/nb,
            heat_W_baryon=n['heat']/nb,cooling_W_baryon=n['cooling']/nb,
            work_W_baryon=2*H*eth,local_ledger_W_baryon=local,
            trace_energy_fraction=(nb*(eth+eion)+n['uv_energy'])/rho,
            einstein_residual=abs(lhs-rhs)/lhs,decay_max=n['decay_max'],
            signed_observables=obs)

    def ledger_integrand(self,x,state):
        y,Y,eta,T,uv,nb,n,f=self.point(x,state);H=f['H']
        return np.array([n['absorbed']/nb/H,n['escape']/nb/H,2*KB*y[62]])
