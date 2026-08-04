"""Channel-resolved physical Ly-alpha true-kernel compiler.

The primary N_nu equation is Chluba-Sunyaev Eq. (4):

 (1/c) dN_nu/dt = sum_i phi_i/(4 pi DeltaNu_D)
   [p_em R_i^+ - p_d^i h nu_21 B_12 N_1s f_th(nu) N_nu].

For arbitrary occupation n=N_nu/g_nu, its exact positivity-preserving
bosonic completion is

 C_i[n] = eta_i(1+n)-chi_i n,
 eta_i=A_i/g_nu, chi_i=eta_i+B_i.
"""
from __future__ import annotations
import numpy as np


def exact_thermodynamic_factor(nu, nu0, beta_h, npl, npl0):
    return (
        (nu0/nu)**2
        * np.exp(beta_h*(nu-nu0))
        * (1.0+npl0)/(1.0+npl)
    )


def compile_true_kernel(profiles, p_d, p_em, R_plus, kappa, f_th,
                        N_nu, g_nu, c_light, delta_nu_D):
    pref = c_light/(4.0*np.pi*delta_nu_D)
    A = pref*profiles*(p_em*R_plus)[:,None]
    B = pref*profiles*(p_d*kappa)[:,None]*f_th[None,:]
    eta = A/g_nu[None,:]
    chi = eta+B
    n = N_nu/g_nu
    C_N = A-B*N_nu[None,:]
    C_n = eta*(1.0+n[None,:])-chi*n[None,:]
    return C_N, C_n, eta, chi
