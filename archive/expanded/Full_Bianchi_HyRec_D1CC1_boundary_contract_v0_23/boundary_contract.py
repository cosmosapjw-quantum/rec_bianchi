"""
Reference boundary-contract functions for Full Bianchi-HyRec.

All fluxes are positive when they leave the line-window interior.
"""

from __future__ import annotations

import numpy as np


def positive_part(value):
    return np.maximum(value, 0.0)


def doppler_coordinate_speed(
    nu: np.ndarray,
    delta_nu_D: float,
    R_H: np.ndarray,
    nu_abs_dot: float,
    x: np.ndarray,
    d_log_delta_nu_D: float,
    boundary_x_dot: float = 0.0,
):
    """
    Relative characteristic speed through a possibly moving x-boundary.

    x = (nu_H - nu_abs) / delta_nu_D.
    """
    return (
        (nu * R_H - nu_abs_dot) / delta_nu_D
        - x * d_log_delta_nu_D
        - boundary_x_dot
    )


def red_outward_flux(a_red, interior_trace, red_exterior_trace):
    """
    Positive = line window -> red exterior.
    """
    return (
        positive_part(-a_red) * interior_trace
        - positive_part(a_red) * red_exterior_trace
    )


def blue_outward_flux(a_blue, interior_trace, blue_exterior_trace):
    """
    Positive = line window -> blue exterior.
    """
    return (
        positive_part(a_blue) * interior_trace
        - positive_part(-a_blue) * blue_exterior_trace
    )


def scattering_edge_flux(S, f_interior, f_exterior, psi_interior, psi_exterior):
    """
    Positive = interior photon state -> exterior photon state.
    """
    return (
        S
        * (1.0 + f_interior)
        * (1.0 + f_exterior)
        * (np.exp(psi_interior) - np.exp(psi_exterior))
    )


def scattering_edge_four_momentum(J, p_interior, p_exterior):
    """
    Returns (interior photon, exterior photon, hydrogen) updates.
    """
    dP_interior = -J[..., None] * p_interior
    dP_exterior = J[..., None] * p_exterior
    dP_hydrogen = J[..., None] * (p_interior - p_exterior)
    return dP_interior, dP_exterior, dP_hydrogen
