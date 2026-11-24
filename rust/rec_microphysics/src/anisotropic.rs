//! Direction-resolved inputs of the one-temperature effective-atom source on a
//! homogeneous anisotropic background (BASS R110 THEORY D8).
//!
//! The radiation field is supplied as positively weighted directions in the
//! baryon (atom) rest frame, each with its own Planck temperature T(e) (exact for
//! free streaming from isotropic Planck data; bolometric effective otherwise),
//! and the velocity-gradient factor f(e) = 1 + Sigma:ee of K = H(I + Sigma).
//!
//! * Lyman-alpha Sobolev escape: tau(e) = tau0 / f(e) and the direction average
//!   P = <(1 - e^-tau)/tau> = <f>/tau0 - <e^-tau/tau>. For a trace-free Sigma
//!   on a symmetric quadrature <f> = 1, so the escape rate per 2p atom is
//!   A_2p1s P = r_alpha(H) (1 - tau0 <e^-tau/tau>): the shear correction to the
//!   optically thick rate vanishes to all orders.
//! * n = 2 photoionization is the direction average of the per-direction
//!   detailed-balance rate beta(T(e)) (HYREC-2 TLA expression).
//! * The blue-wing Lyman-alpha occupation is escape-weighted:
//!   b = <f e^{-E21/kT}> / <f> in the optically thick limit.
//! * The one-temperature matter temperature is the Compton equilibrium
//!   temperature of the direction-averaged occupation
//!   kT_C = h int nbar(1+nbar) nu^4 / (4 int nbar nu^3).
//!
//! These are pointwise source assemblies, not a recombination history.

use crate::hydrogen_peebles::{
    HYREC_E21_EV, HYREC_EI_EV, HYREC_KB_EV_K, HYREC_LAMBDA_2GAMMA_S, HYREC_LYA_PER_CM3,
    HYREC_SAHA_PER_CM3_EV32, RetainedState, ShellRates, hyrec2_ppb_alpha_b_si,
};

/// Einstein A of H 2p -> 1s [s^-1] (NIST), used only for the finite-depth
/// escape correction tau0 = A_2p1s / r_alpha.
pub const A_2P1S_S: f64 = 6.2649e8;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum AnisotropyError {
    Shape,
    NonFinite,
    NonPositiveWeight,
    NonPositiveTemperature,
    /// A direction has f(e) <= 0: the flow contracts along it and the Sobolev
    /// reduction does not apply.
    ContractingDirection,
    Domain,
    Hydrogen,
}

/// Weighted directions with temperatures and velocity-gradient factors.
#[derive(Debug, Clone, Copy)]
pub struct DirectionalSky<'a> {
    pub weights: &'a [f64],
    pub temperature_k: &'a [f64],
    pub expansion_factor: &'a [f64],
}

impl DirectionalSky<'_> {
    pub fn validate(&self) -> Result<(), AnisotropyError> {
        let n = self.weights.len();
        if n == 0 || self.temperature_k.len() != n || self.expansion_factor.len() != n {
            return Err(AnisotropyError::Shape);
        }
        for ((w, t), f) in self
            .weights
            .iter()
            .zip(self.temperature_k)
            .zip(self.expansion_factor)
        {
            if !w.is_finite() || !t.is_finite() || !f.is_finite() {
                return Err(AnisotropyError::NonFinite);
            }
            if *w <= 0.0 {
                return Err(AnisotropyError::NonPositiveWeight);
            }
            if *t <= 0.0 {
                return Err(AnisotropyError::NonPositiveTemperature);
            }
            if *f <= 0.0 {
                return Err(AnisotropyError::ContractingDirection);
            }
        }
        Ok(())
    }
    fn total_weight(&self) -> f64 {
        self.weights.iter().sum()
    }
}

/// Direction-averaged Sobolev escape probability for isotropic depth tau0.
pub fn sobolev_escape_average(tau0: f64, sky: &DirectionalSky) -> Result<f64, AnisotropyError> {
    sky.validate()?;
    if !tau0.is_finite() || tau0 <= 0.0 {
        return Err(AnisotropyError::Domain);
    }
    let mut sum = 0.0;
    for (w, f) in sky.weights.iter().zip(sky.expansion_factor) {
        let tau = tau0 / f;
        sum += w * (-(-tau).exp_m1()) / tau;
    }
    Ok(sum / sky.total_weight())
}

/// tau0 times the escape average, evaluated as <f> - tau0 <e^-tau/tau> for
/// tau0 >= 1 to keep the exponentially small optically thick correction exact,
/// and as tau0 * sobolev_escape_average for tau0 < 1 to avoid thin-limit cancellation.
pub fn escape_rate_factor(tau0: f64, sky: &DirectionalSky) -> Result<f64, AnisotropyError> {
    sky.validate()?;
    if !tau0.is_finite() || tau0 <= 0.0 {
        return Err(AnisotropyError::Domain);
    }
    if tau0 < 1.0 {
        return Ok(tau0 * sobolev_escape_average(tau0, sky)?);
    }
    let total = sky.total_weight();
    let mut mean_f = 0.0;
    let mut tail = 0.0;
    for (w, f) in sky.weights.iter().zip(sky.expansion_factor) {
        let tau = tau0 / f;
        mean_f += w * f;
        tail += w * (-tau).exp() / tau;
    }
    Ok(mean_f / total - tau0 * tail / total)
}

/// ln of the weighted direction average of exp(-E/kT(e)); log-sum-exp stable.
/// With `escape_weighted`, the weights are multiplied by f(e).
pub fn wien_average_ln(
    energy_ev: f64,
    sky: &DirectionalSky,
    escape_weighted: bool,
) -> Result<f64, AnisotropyError> {
    sky.validate()?;
    if !energy_ev.is_finite() || energy_ev <= 0.0 {
        return Err(AnisotropyError::Domain);
    }
    let weight = |i: usize| {
        sky.weights[i]
            * if escape_weighted {
                sky.expansion_factor[i]
            } else {
                1.0
            }
    };
    let exponents: Vec<f64> = sky
        .temperature_k
        .iter()
        .map(|t| -energy_ev / (HYREC_KB_EV_K * t))
        .collect();
    let peak = exponents.iter().copied().fold(f64::NEG_INFINITY, f64::max);
    let mut sum = 0.0;
    let mut total = 0.0;
    for (i, x) in exponents.iter().enumerate() {
        sum += weight(i) * (x - peak).exp();
        total += weight(i);
    }
    Ok(peak + (sum / total).ln())
}

/// Direction average of the HYREC-2 TLA n=2 photoionization rate, each
/// direction in detailed balance with its own temperature.
pub fn photoionization_average_s(sky: &DirectionalSky) -> Result<f64, AnisotropyError> {
    sky.validate()?;
    let mut sum = 0.0;
    for (w, t) in sky.weights.iter().zip(sky.temperature_k) {
        let alpha = hyrec2_ppb_alpha_b_si(*t).map_err(|_| AnisotropyError::Hydrogen)?;
        let tev = HYREC_KB_EV_K * t;
        sum += w
            * (alpha.ln() + (HYREC_SAHA_PER_CM3_EV32 * 1e6).ln() + 1.5 * tev.ln()
                - (HYREC_EI_EV / 4.0) / tev)
                .exp();
    }
    let out = sum / sky.total_weight();
    if out.is_finite() {
        Ok(out)
    } else {
        Err(AnisotropyError::NonFinite)
    }
}

/// Compton equilibrium temperature of the direction-averaged Planck occupation.
/// For a single temperature this returns that temperature (integration by
/// parts of the Planck integrals); for a mixture it lies inside [min T, max T].
pub fn compton_temperature_k(sky: &DirectionalSky) -> Result<f64, AnisotropyError> {
    sky.validate()?;
    let total = sky.total_weight();
    let tref = sky
        .weights
        .iter()
        .zip(sky.temperature_k)
        .map(|(w, t)| w * t)
        .sum::<f64>()
        / total;
    let tmax = sky.temperature_k.iter().copied().fold(0.0, f64::max);
    // x = h nu / (k tref); the integrands decay as exp(-x tref/tmax).
    let upper = 64.0 * tmax / tref;
    const PANELS: usize = 256;
    const NODES: [f64; 8] = [
        -0.960_289_856_497_536_3,
        -0.796_666_477_413_626_7,
        -0.525_532_409_916_329_0,
        -0.183_434_642_495_649_8,
        0.183_434_642_495_649_8,
        0.525_532_409_916_329_0,
        0.796_666_477_413_626_7,
        0.960_289_856_497_536_3,
    ];
    const WEIGHTS: [f64; 8] = [
        0.101_228_536_290_376_3,
        0.222_381_034_453_374_5,
        0.313_706_645_877_887_3,
        0.362_683_783_378_362_0,
        0.362_683_783_378_362_0,
        0.313_706_645_877_887_3,
        0.222_381_034_453_374_5,
        0.101_228_536_290_376_3,
    ];
    let h = upper / PANELS as f64;
    let (mut numerator, mut denominator) = (0.0, 0.0);
    for p in 0..PANELS {
        let mid = (p as f64 + 0.5) * h;
        for (node, weight) in NODES.iter().zip(WEIGHTS) {
            let x = mid + 0.5 * h * node;
            let mut nbar = 0.0;
            for (w, t) in sky.weights.iter().zip(sky.temperature_k) {
                nbar += w / (x * tref / t).exp_m1();
            }
            nbar /= total;
            let x3 = x * x * x;
            numerator += 0.5 * h * weight * nbar * (1.0 + nbar) * x3 * x;
            denominator += 0.5 * h * weight * nbar * x3;
        }
    }
    let out = tref * numerator / (4.0 * denominator);
    if out.is_finite() && out > 0.0 {
        Ok(out)
    } else {
        Err(AnisotropyError::NonFinite)
    }
}

/// Assembled anisotropic one-temperature source.
#[derive(Debug, Clone, Copy)]
pub struct AnisotropicSource {
    pub matter_temperature_k: f64,
    pub alpha_b_m3_s: f64,
    pub beta_p_s: f64,
    pub boltzmann_lya: f64,
    /// Escape rate per 2p atom including the finite-depth correction.
    pub r_alpha_s: f64,
    /// tau0 = A_2p1s / r_alpha(H).
    pub sobolev_depth: f64,
    pub rates: ShellRates,
}

/// HYREC-2 TLA source of `hydrogen_peebles::hyrec2_one_temperature_source`
/// generalized to an anisotropic sky. With equal temperatures and f = 1 in
/// every direction, the rates reduce to the isotropic source up to the
/// finite-depth escape factor, which is exponentially small when tau0 >> 1.
pub fn anisotropic_one_temperature_source(
    sky: &DirectionalSky,
    n_h_m3: f64,
    hubble_s: f64,
    state: RetainedState,
) -> Result<AnisotropicSource, AnisotropyError> {
    sky.validate()?;
    if !n_h_m3.is_finite() || n_h_m3 <= 0.0 || !hubble_s.is_finite() || hubble_s <= 0.0 {
        return Err(AnisotropyError::Domain);
    }
    let x1 = state.ground().map_err(|_| AnisotropyError::Hydrogen)?;
    if x1 <= 0.0 {
        return Err(AnisotropyError::Domain);
    }
    let tm = compton_temperature_k(sky)?;
    let alpha = hyrec2_ppb_alpha_b_si(tm).map_err(|_| AnisotropyError::Hydrogen)?;
    let beta_p = photoionization_average_s(sky)?;
    let b = wien_average_ln(HYREC_E21_EV, sky, true)?.exp();
    let r_alpha_h = (HYREC_LYA_PER_CM3 * 1e6) * (hubble_s / n_h_m3) / x1;
    let tau0 = A_2P1S_S / r_alpha_h;
    let r_alpha = r_alpha_h * escape_rate_factor(tau0, sky)?;
    let rates = ShellRates::new(beta_p, HYREC_LAMBDA_2GAMMA_S, r_alpha, b)
        .map_err(|_| AnisotropyError::Hydrogen)?;
    Ok(AnisotropicSource {
        matter_temperature_k: tm,
        alpha_b_m3_s: alpha,
        beta_p_s: beta_p,
        boltzmann_lya: b,
        r_alpha_s: r_alpha,
        sobolev_depth: tau0,
        rates,
    })
}
