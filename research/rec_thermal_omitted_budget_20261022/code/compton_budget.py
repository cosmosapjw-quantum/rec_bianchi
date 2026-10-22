"""Identifiable leading Compton terms; explicit spectral reference ownership.

The hot-electron term uses the actual radiation energy monopole. A Planck
reference constructs its OWN energy density, rather than inferring a spectrum
from the Bianchi hierarchy. UV recoil uses the inherited bin energies/flux.
Powers are positive INTO gas. No state is integrated or modified here.
"""
from __future__ import annotations

import math
import numpy as np

C_M_S = 299792458.0
KB_J_K = 1.380649e-23
H_J_S = 6.62607015e-34
EV_J = 1.602176634e-19
# Same Thomson value as the pinned lrs_boltzmann.py owner, converted cm2→m2.
SIGMA_T_M2 = 6.6524587051e-29
# CODATA 2022 value, also the actual SciPy 1.17.0 runtime's electron mass.
ME_KG = 9.1093837139e-31
MEC2_J = ME_KG * C_M_S**2
SIGMA_T_C_M3_S = SIGMA_T_M2 * C_M_S
A_RAD_J_M3_K4 = 8 * math.pi**5 * KB_J_K**4 / (15 * H_J_S**3 * C_M_S**3)


def _nonnegative(**values):
    for name, value in values.items():
        if not math.isfinite(float(value)) or float(value) < 0:
            raise ValueError(name + ' must be finite and nonnegative')


def hot_electron_power(ne_m3, T_K, photon_energy_J_m3):
    """Leading thermal inverse-Compton gas power, arbitrary photon anisotropy.

    Isotropic non-tilted nonrelativistic electrons, Thomson photon energies.
    Recoil and induced scattering are separate terms and are not inferred.
    """
    _nonnegative(ne_m3=ne_m3, T_K=T_K, U=photon_energy_J_m3)
    return -4 * SIGMA_T_C_M3_S * ne_m3 * KB_J_K * T_K * photon_energy_J_m3 / MEC2_J


def planck_reference_power(ne_m3, T_K, T_rad_K):
    """Net gas power for an independently specified isotropic Planck reference."""
    _nonnegative(ne_m3=ne_m3, T_K=T_K, T_rad_K=T_rad_K)
    U = A_RAD_J_M3_K4 * T_rad_K**4
    return 4 * SIGMA_T_C_M3_S * ne_m3 * KB_J_K * U * (T_rad_K - T_K) / MEC2_J


def dilute_spectrum_power(ne_m3, T_K, U_J_m3, M_J2_m3):
    """First-order recoil plus thermal exchange, negligible photon occupation.

    M=integral epsilon^2 dn_gamma. Its units are J2/m3. A photon energy
    density alone does not determine this moment. Positive sign heats gas.
    """
    _nonnegative(ne_m3=ne_m3, T_K=T_K, U=U_J_m3, M=M_J2_m3)
    if U_J_m3 == 0 and M_J2_m3 != 0:
        raise ValueError('nonzero recoil moment with zero photon energy')
    return SIGMA_T_C_M3_S * ne_m3 * (M_J2_m3 - 4*KB_J_K*T_K*U_J_m3) / MEC2_J


def uv_reference_moments(energy_eV, flux_bins_m2_s, edges_eV, number_power_index):
    """Moments of the EXACT adopted bin-centre photon representation at uv=1.

    The continuous prescribed power law is used only to bound occupation and
    to measure the existing bin-centre quadrature difference. Neither replaces
    the bins used by the inherited number/photo-heating network.
    """
    energy = np.asarray(energy_eV, dtype=float)
    flux = np.asarray(flux_bins_m2_s, dtype=float)
    edges = np.asarray(edges_eV, dtype=float)
    if (energy.ndim != 1 or flux.shape != energy.shape or
            edges.shape != (energy.size+1,) or not np.all(np.isfinite(energy)) or
            not np.all(np.isfinite(flux)) or not np.all(np.isfinite(edges)) or
            np.any(flux < 0) or np.any(edges <= 0) or np.any(np.diff(edges) <= 0) or
            np.any(energy <= edges[:-1]) or np.any(energy >= edges[1:])):
        raise ValueError('invalid positive UV bin representation')
    p = float(number_power_index)
    if not math.isfinite(p):
        raise ValueError('finite spectral power required')
    def moment_integral(power):
        r=power+1
        return math.log(edges[-1]/edges[0]) if r == 0 else (edges[-1]**r-edges[0]**r)/r
    normalization = float(np.sum(flux))/moment_integral(p)
    expected = (np.log(edges[1:]/edges[:-1]) if p == -1 else
                (edges[1:]**(p+1)-edges[:-1]**(p+1))/(p+1))*normalization
    if not np.allclose(flux,expected,rtol=2e-13,atol=0):
        raise ValueError('UV bins do not share the declared continuous power law')
    eps = energy*EV_J
    U = float(flux@eps)/C_M_S
    M = float(flux@(eps*eps))/C_M_S
    edge_at_max = edges[0] if p <= 2 else edges[-1]
    occupation = H_J_S**3*C_M_S**2/(8*math.pi*EV_J**3)*normalization*edge_at_max**(p-2)
    continuous_U=normalization*moment_integral(p+1)*EV_J/C_M_S
    continuous_M=normalization*moment_integral(p+2)*EV_J**2/C_M_S
    return dict(U_J_m3=U, M_J2_m3=M,
                Compton_temperature_K=M/(4*KB_J_K*U) if U else None,
                max_continuous_occupation_at_uv1=occupation,
                photon_energy_max_over_mec2=edges[-1]*EV_J/MEC2_J,
                continuous_power_law_U_J_m3=continuous_U,
                continuous_power_law_M_J2_m3=continuous_M,
                bin_U_relative_difference=U/continuous_U-1 if U else 0.,
                bin_M_relative_difference=M/continuous_M-1 if M else 0.,
                bin_count=int(energy.size),
                flux_frame='isotropic number flux = c times photon number density',
                scope='leading nonrelativistic/Thomson, dilute external UV')


def fixed_path_logT_forcing(Q_kin_W_m3, particle_source_per_baryon_s,
                           H_s, T_K, nb_m3, eta):
    """Direct omitted RHS contribution on a fixed state, not a solved deltaT."""
    if not all(math.isfinite(float(v)) and float(v)>0 for v in (H_s,T_K,nb_m3,eta)):
        raise ValueError('positive finite H,T,nb,eta required')
    if not all(math.isfinite(float(v)) for v in (Q_kin_W_m3,particle_source_per_baryon_s)):
        raise ValueError('finite source required')
    return (2*Q_kin_W_m3/(3*KB_J_K*T_K*nb_m3)-particle_source_per_baryon_s)/(H_s*eta)


def constants():
    return dict(c_m_s=C_M_S,kB_J_K=KB_J_K,h_J_s=H_J_S,eV_J=EV_J,
                sigma_T_m2=SIGMA_T_M2,m_e_kg=ME_KG,
                radiation_constant_J_m3_K4=A_RAD_J_M3_K4)
