"""Conservative source deposition into an explicitly supplied physical COM measure.

This is a component, NOT a full native/COM split or a stencil-builder authority.
The caller supplies the actual network mode_measure (m^-3), its photon energies
(J), angular-average weights (sum one), and a declared source deposition map.
No finite volumes are inferred from zero-width native spikes. No Aup/Adn proxy
is called a physical photon flux. Signed emission/absorption source rates are
per H per second; they are not themselves positive occupation states.

For B[i,s] with sum_i B[i,s]=1 and sum_i E[i] B[i,s]=E_source[s],
 df[i,a]/dt = n_H/mu[i] * sum_s B[i,s] R[s,a].
B is fixed in apply/JVP; temperature-dependent map/measure derivatives must be
supplied by the future coupled owner, not silently dropped. This implementation
uses O(M*S + M*A) storage and O(M*S*A) time per action.

Four-vectors use (-,+,+,+), the hydrogen orthonormal frame, and report c G^a
(all four components W m^-3). No independent atomic four-force is fabricated.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np


def _array(value, ndim, name):
    raw = np.asarray(value)
    if raw.dtype.kind not in 'fiu' or raw.ndim != ndim:
        raise ValueError(name + ' has invalid real-array shape/type')
    result = np.array(raw, dtype=np.float64, copy=True, order='C')
    if not np.isfinite(result).all():
        raise ValueError(name + ' must be finite')
    return np.frombuffer(result.tobytes(), dtype=result.dtype).reshape(result.shape)


def _gamma(n):
    # Fixed arithmetic error allowance, not an adjustable physics tolerance.
    ne = int(n)*np.finfo(np.float64).eps
    if ne >= .5:
        raise ValueError('dimension exceeds the roundoff certificate domain')
    return ne/(1-ne)


@dataclass(frozen=True)
class COMSourceDepositionPlan:
    mode_measure_m3: np.ndarray
    cell_energy_J: np.ndarray
    source_energy_J: np.ndarray
    number_fractions: np.ndarray
    angular_weights: np.ndarray
    directions: np.ndarray
    measure_id: str
    map_id: str

    def __post_init__(self):
        for name, ndim in [('mode_measure_m3',1),('cell_energy_J',1),
                           ('source_energy_J',1),('number_fractions',2),
                           ('angular_weights',1),('directions',2)]:
            object.__setattr__(self,name,_array(getattr(self,name),ndim,name))
        mu,E,Es,B,w,e = (self.mode_measure_m3,self.cell_energy_J,self.source_energy_J,
                         self.number_fractions,self.angular_weights,self.directions)
        if not len(mu) or not len(Es) or not len(w):
            raise ValueError('empty physical measure or source map')
        if E.shape != mu.shape or B.shape != (len(mu),len(Es)) or e.shape != (len(w),3):
            raise ValueError('incompatible physical-measure/deposition shapes')
        if np.any(mu<=0) or np.any(E<=0) or np.any(Es<=0):
            raise ValueError('physical mode measure and energies must be positive')
        if np.any(w<=0) or np.any(B<0):
            raise ValueError('deposition fractions nonnegative; angular weights positive')
        if not isinstance(self.measure_id,str) or not self.measure_id.strip() or not isinstance(self.map_id,str) or not self.map_id.strip():
            raise ValueError('explicit measure_id and map_id required')
        g = _gamma(2*len(mu)+8)
        number = np.sum(B,axis=0)
        if not np.isfinite(number).all() or np.any(np.abs(number-1)>g*np.sum(np.abs(B),axis=0)):
            raise ValueError('source photon-number partition fails; no normalization applied')
        energy = E@B
        if not np.isfinite(energy).all() or np.any(np.abs(energy-Es)>g*((np.abs(E)@np.abs(B))+np.abs(Es))):
            raise ValueError('source photon-energy moment fails; no fitted correction applied')
        if abs(math.fsum(w)-1)>_gamma(2*len(w)+8)*math.fsum(abs(w)):
            raise ValueError('angular weights must represent an average with sum one')
        # Same unit-sphere tolerance as HarmonicGrid._validated_grid_primitives.
        if np.any(np.abs(np.linalg.norm(e,axis=1)-1)>1.0e-12):
            raise ValueError('angular directions must be unit vectors')

    def _rates(self, rates):
        value = np.asarray(rates)
        if value.dtype.kind not in 'fiu':
            raise ValueError('rates must be real')
        value = np.asarray(value,dtype=np.float64)
        ns,na = len(self.source_energy_J),len(self.angular_weights)
        if value.shape == (ns,):
            value = np.broadcast_to(value[:,None],(ns,na))
        elif value.shape != (ns,na):
            raise ValueError('rates require exactly (S,) isotropic or (S,A) directional values')
        if not np.isfinite(value).all():
            raise ValueError('rates must be finite')
        return value

    @staticmethod
    def _density(nH):
        if isinstance(nH,(bool,np.bool_,complex,np.complexfloating)) or not np.isscalar(nH) or not np.isfinite(nH) or nH<=0:
            raise ValueError('n_H must be finite positive physical density in m^-3')
        return float(nH)

    def _result(self, numerator):
        with np.errstate(over='ignore',invalid='ignore',divide='ignore'):
            result = numerator/self.mode_measure_m3[:,None]
        if not np.isfinite(result).all():
            raise FloatingPointError('nonfinite common-measure deposition action')
        return result

    def apply(self, rates_per_H_s, nH_m3):
        rates=self._rates(rates_per_H_s);nH=self._density(nH_m3)
        return self._result(nH*(self.number_fractions@rates))

    def jvp(self, rates_per_H_s, rate_tangent_per_H_s, nH_m3, nH_tangent_m3=0.):
        nH=self._density(nH_m3)
        if not np.isscalar(nH_tangent_m3) or not np.isfinite(nH_tangent_m3):
            raise ValueError('density tangent must be a finite scalar')
        rates=self._rates(rates_per_H_s);dr=self._rates(rate_tangent_per_H_s)
        return self._result(self.number_fractions@(nH*dr+float(nH_tangent_m3)*rates))

    def photon_power_four_vector(self, occupation_action_s_inv):
        action=_array(occupation_action_s_inv,2,'occupation_action_s_inv')
        if action.shape != (len(self.mode_measure_m3),len(self.angular_weights)) or not np.isfinite(action).all():
            raise ValueError('occupation action shape or finite-domain error')
        by_angle=np.einsum('i,i,ia->a',self.cell_energy_J,self.mode_measure_m3,action)
        result = np.concatenate(([self.angular_weights@by_angle],
                                 (self.angular_weights*by_angle)@self.directions))
        if not np.isfinite(result).all():
            raise FloatingPointError('nonfinite photon moment')
        return result

    def source_power_four_vector(self, rates_per_H_s, nH_m3):
        # Independently contracted source-side moments; not minus photon output.
        rates=self._rates(rates_per_H_s);nH=self._density(nH_m3)
        by_angle=nH*(self.source_energy_J@rates)
        result = np.concatenate(([self.angular_weights@by_angle],
                                 (self.angular_weights*by_angle)@self.directions))
        if not np.isfinite(result).all():
            raise FloatingPointError('nonfinite photon moment')
        return result
