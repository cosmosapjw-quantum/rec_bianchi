//! Pure-hydrogen, one-temperature Peebles reference, with a retained n=2 shell.
//!
//! This is a pointwise source/reduction module, not an admitted cosmological
//! history, a general Bianchi radiation solver, or the existing He consumer.
//! `x_p = n_p/n_H = x_e`, `x_2 = n_(n=2)/n_H`, and `x_1=1-x_p-x_2`.
//! All densities and recombination coefficients are SI; rates are in s^-1.
//! The shell weights are x_2s=x_2/4 and x_2p=3*x_2/4.

use std::f64::consts::PI;

pub const SOURCE_PROFILE: &str = "HYREC2_TLA_2020_PEEBLES_FUDGE1";
pub const SOURCE_COMMIT: &str = "09e8243d0e08edd3603a94dfbc445ae06cafe139";
pub const HYREC_KB_EV_K: f64 = 8.617_343e-5;
pub const HYREC_EI_EV: f64 = 13.598_286_071_938_324;
pub const HYREC_E21_EV: f64 = 10.198_714_553_953_742;
pub const HYREC_LAMBDA_2GAMMA_S: f64 = 8.2206;
pub const HYREC_SAHA_PER_CM3_EV32: f64 = 3.016_103_031_869_581e21;
pub const HYREC_LYA_PER_CM3: f64 = 4.662_899_067_555_897e15;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum HydrogenError {
    NonFinite,
    Domain,
    UnequalTemperatures,
    DegenerateRates,
    ZeroGroundSobolev,
    NonPhysicalQss,
    Overflow,
}

fn finite(x: f64) -> Result<f64, HydrogenError> {
    if x.is_finite() { Ok(x) } else { Err(HydrogenError::NonFinite) }
}
fn nonnegative(x: f64) -> Result<f64, HydrogenError> {
    finite(x)?;
    if x >= 0.0 { Ok(x) } else { Err(HydrogenError::Domain) }
}
fn positive(x: f64) -> Result<f64, HydrogenError> {
    finite(x)?;
    if x > 0.0 { Ok(x) } else { Err(HydrogenError::Domain) }
}
fn output(x: f64) -> Result<f64, HydrogenError> {
    if x.is_finite() { Ok(x) } else { Err(HydrogenError::Overflow) }
}

/// Explicit physical constants; no silent replacement by the source-rounded
/// HYREC profile. E21 is derived as h*c/lambda, and chi1=chi2+E21.
#[derive(Debug, Clone, Copy)]
pub struct PhysicalConstantsSI {
    pub h_j_s: f64,
    pub k_b_j_k: f64,
    pub c_m_s: f64,
    pub reduced_mass_kg: f64,
    pub chi2_j: f64,
    pub lambda_lya_m: f64,
}
impl PhysicalConstantsSI {
    pub fn thermal_factors(
        self, t_m_k: f64, t_r_k: f64, alpha_b_m3_s: f64,
    ) -> Result<(f64, f64), HydrogenError> {
        positive(t_m_k)?;
        positive(t_r_k)?;
        nonnegative(alpha_b_m3_s)?;
        for v in [self.h_j_s, self.k_b_j_k, self.c_m_s,
                  self.reduced_mass_kg, self.chi2_j, self.lambda_lya_m] {
            positive(v)?;
        }
        if t_m_k != t_r_k { return Err(HydrogenError::UnequalTemperatures); }
        let kt = output(self.k_b_j_k * t_r_k)?;
        positive(kt)?;
        let e21 = output(self.h_j_s * self.c_m_s / self.lambda_lya_m)?;
        let log_phi = 1.5 * ((2.0 * PI).ln() + self.reduced_mass_kg.ln()
            + self.k_b_j_k.ln() + t_r_k.ln() - 2.0 * self.h_j_s.ln());
        let beta = if alpha_b_m3_s == 0.0 { 0.0 } else {
            output((alpha_b_m3_s.ln() + log_phi - self.chi2_j / kt).exp())?
        };
        Ok((beta, (-e21 / kt).exp()))
    }
}

#[derive(Debug, Clone, Copy)]
pub struct ShellRates {
    beta_p_s: f64,
    beta_shell_s: f64,
    d_ground_s: f64,
    boltzmann_lya: f64,
}
impl ShellRates {
    /// `r_alpha_s` is the escape rate per 2p atom. The model requires a thermal
    /// inverse term and statistical 2s:2p weights of 1:3.
    pub fn new(beta_p_s: f64, lambda_2gamma_s: f64, r_alpha_s: f64,
               boltzmann_lya: f64) -> Result<Self, HydrogenError> {
        for v in [beta_p_s, lambda_2gamma_s, r_alpha_s, boltzmann_lya] {
            nonnegative(v)?;
        }
        if boltzmann_lya > 1.0 { return Err(HydrogenError::Domain); }
        let beta_shell_s = beta_p_s * 0.25;
        let d_ground_s = output(lambda_2gamma_s * 0.25 + r_alpha_s * 0.75)?;
        if beta_shell_s == 0.0 && d_ground_s == 0.0 {
            return Err(HydrogenError::DegenerateRates);
        }
        Ok(Self { beta_p_s, beta_shell_s, d_ground_s, boltzmann_lya })
    }
    /// Stable D/(D+beta_shell), including C=0 and C=1 endpoints.
    pub fn c_factor(self) -> f64 {
        let scale = self.beta_shell_s.max(self.d_ground_s);
        let d = self.d_ground_s / scale;
        d / (d + self.beta_shell_s / scale)
    }
    pub fn beta_p_s(self) -> f64 { self.beta_p_s }
    pub fn beta_shell_s(self) -> f64 { self.beta_shell_s }
    pub fn d_ground_s(self) -> f64 { self.d_ground_s }
    pub fn boltzmann_lya(self) -> f64 { self.boltzmann_lya }
    fn over_total(self, numerator: f64) -> f64 {
        let scale = self.beta_shell_s.max(self.d_ground_s);
        (numerator / scale) / (self.beta_shell_s / scale + self.d_ground_s / scale)
    }
}

#[derive(Debug, Clone, Copy)]
pub struct RetainedState { pub xp: f64, pub x2: f64 }
impl RetainedState {
    pub fn ground(self) -> Result<f64, HydrogenError> {
        nonnegative(self.xp)?;
        nonnegative(self.x2)?;
        if self.xp > 1.0 || self.x2 > 1.0 - self.xp {
            return Err(HydrogenError::Domain);
        }
        Ok((1.0 - self.xp) - self.x2)
    }
}
fn recombination_flux(n_h_m3: f64, alpha_b_m3_s: f64, xp: f64)
    -> Result<f64, HydrogenError> {
    positive(n_h_m3)?;
    nonnegative(alpha_b_m3_s)?;
    nonnegative(xp)?;
    if xp > 1.0 { return Err(HydrogenError::Domain); }
    output((n_h_m3 * xp) * (alpha_b_m3_s * xp))
}

#[derive(Debug, Clone, Copy)]
pub struct RetainedRhs {
    pub dxp_dt: f64,
    pub dx2_dt: f64,
    pub dx1_dt: f64,
    /// Net continuum-to-shell flux: n_H alpha_B xp^2-beta_shell*x2.
    pub continuum_flux: f64,
    /// Net shell-to-ground flux: D*(x2-4*x1*exp(-E21/kT)).
    pub ground_flux: f64,
}
/// The rates are frozen inputs at this evaluation. A physical local Sobolev
/// caller must reassemble them at each changed retained state.
pub fn retained_rhs(n_h_m3: f64, alpha_b_m3_s: f64,
                    rates: ShellRates, state: RetainedState)
    -> Result<RetainedRhs, HydrogenError> {
    let x1 = state.ground()?;
    let a = recombination_flux(n_h_m3, alpha_b_m3_s, state.xp)?;
    let continuum_flux = output(a - rates.beta_shell_s * state.x2)?;
    let ground_flux = output(rates.d_ground_s
        * (state.x2 - 4.0 * (x1 * rates.boltzmann_lya)))?;
    Ok(RetainedRhs {
        dxp_dt: -continuum_flux,
        dx2_dt: output(continuum_flux - ground_flux)?,
        dx1_dt: ground_flux,
        continuum_flux, ground_flux,
    })
}

/// Algebraic elimination at supplied fixed ground abundance. For actual x1 this
/// gives the instantaneous target; it is not a self-consistent finite-shell root.
pub fn qss_at_fixed_ground(n_h_m3: f64, alpha_b_m3_s: f64,
                          rates: ShellRates, xp: f64, x1: f64)
    -> Result<f64, HydrogenError> {
    nonnegative(x1)?;
    if x1 > 1.0 { return Err(HydrogenError::Domain); }
    let a = recombination_flux(n_h_m3, alpha_b_m3_s, xp)?;
    output(rates.over_total(a)
        + 4.0 * rates.c_factor() * (x1 * rates.boltzmann_lya))
}

/// Exact finite-population QSS only in the explicitly frozen-Ralpha model.
/// This includes x1=1-xp-x2 in the thermal inverse. It is NOT the nonlinear
/// root with Ralpha proportional to 1/x1 as x2 changes.
pub fn frozen_escape_qss(n_h_m3: f64, alpha_b_m3_s: f64,
                         rates: ShellRates, xp: f64)
    -> Result<RetainedState, HydrogenError> {
    let collapsed = qss_at_fixed_ground(n_h_m3, alpha_b_m3_s, rates, xp, 1.0-xp)?;
    let x2 = output(collapsed / (1.0 + 4.0 * rates.c_factor() * rates.boltzmann_lya))?;
    let state = RetainedState { xp, x2 };
    state.ground().map_err(|_| HydrogenError::NonPhysicalQss)?;
    Ok(state)
}

/// Collapsed Peebles equation at supplied instantaneous rates, x1=1-xp in
/// the inverse term. For the complete standard Sobolev Peebles profile, assemble
/// these rates with RetainedState { xp, x2: 0.0 }. For a retained state x2>0,
/// the actual-ground Sobolev C differs too; closure_defect intentionally holds
/// the SAME instantaneous rates on both sides to isolate shell/depletion errors.
pub fn peebles_rhs(n_h_m3: f64, alpha_b_m3_s: f64,
                   rates: ShellRates, xp: f64) -> Result<f64, HydrogenError> {
    let a = recombination_flux(n_h_m3, alpha_b_m3_s, xp)?;
    output(-rates.c_factor() * (a
        - rates.beta_p_s * ((1.0 - xp) * rates.boltzmann_lya)))
}

#[derive(Debug, Clone, Copy)]
pub struct ClosureDefect {
    pub direct: f64,
    pub shell_lag: f64,
    pub ground_depletion: f64,
    pub reconstructed: f64,
}
/// Exact pointwise identity: retained dxp minus collapsed Peebles equals
/// -(1-C)*dx2 - C*beta_P*exp(-E21/kT)*x2. Valid for the same instantaneous rates.
pub fn closure_defect(n_h_m3: f64, alpha_b_m3_s: f64,
                       rates: ShellRates, state: RetainedState)
    -> Result<ClosureDefect, HydrogenError> {
    let rhs = retained_rhs(n_h_m3, alpha_b_m3_s, rates, state)?;
    let peebles = peebles_rhs(n_h_m3, alpha_b_m3_s, rates, state.xp)?;
    // beta/(beta+D) is evaluated directly, not as 1-C, when C rounds to 1.
    let scale = rates.beta_shell_s.max(rates.d_ground_s);
    let beta_weight = (rates.beta_shell_s / scale)
        / (rates.beta_shell_s / scale + rates.d_ground_s / scale);
    let shell_lag = output(-beta_weight * rhs.dx2_dt)?;
    let ground_depletion = output(-rates.c_factor() * rates.beta_p_s
        * (rates.boltzmann_lya * state.x2))?;
    Ok(ClosureDefect {
        direct: output(rhs.dxp_dt - peebles)?, shell_lag, ground_depletion,
        reconstructed: output(shell_lag + ground_depletion)?,
    })
}

/// dt/dz = -1/[(1+z)H] for an expanding FLRW background.
pub fn to_redshift_rhs(dx_dt: f64, z: f64, hubble_s: f64)
    -> Result<f64, HydrogenError> {
    finite(dx_dt)?; finite(z)?; positive(hubble_s)?;
    if z <= -1.0 { return Err(HydrogenError::Domain); }
    output((-dx_dt / hubble_s) / (1.0 + z))
}

/// Author-published PPB fit as selected by HYREC's TLA Peebles mode, Fudge=1.
/// A clean formula implementation; no upstream source is vendored. The
/// profile is a benchmark identity, not a newly certified physical error bound.
pub fn hyrec2_ppb_alpha_b_si(temperature_k: f64) -> Result<f64, HydrogenError> {
    positive(temperature_k)?;
    let t4 = temperature_k / 1e4;
    positive(t4)?;
    output(4.309e-19 * t4.powf(-0.6166) / (1.0 + 0.6703 * t4.powf(0.5300)))
}
#[derive(Debug, Clone, Copy)]
pub struct SourceBoundPoint {
    pub alpha_b_m3_s: f64,
    pub r_alpha_s: f64,
    pub rates: ShellRates,
}
/// One-temperature, optically thick local Sobolev source profile. Proper n_H
/// is SI. H>0 and x1>0 are required. Source-rounded HYREC constants are retained
/// exactly; this is intentionally distinct from recomputed physical constants.
pub fn hyrec2_one_temperature_source(t_m_k: f64, t_r_k: f64,
                                    n_h_m3: f64, hubble_s: f64,
                                    state: RetainedState)
    -> Result<SourceBoundPoint, HydrogenError> {
    positive(t_m_k)?; positive(t_r_k)?;
    positive(n_h_m3)?; positive(hubble_s)?;
    if t_m_k != t_r_k { return Err(HydrogenError::UnequalTemperatures); }
    let x1 = state.ground()?;
    if x1 == 0.0 { return Err(HydrogenError::ZeroGroundSobolev); }
    let alpha = hyrec2_ppb_alpha_b_si(t_m_k)?;
    let tev = output(HYREC_KB_EV_K * t_r_k)?;
    positive(tev)?;
    let beta_p = output((alpha.ln() + (HYREC_SAHA_PER_CM3_EV32 * 1e6).ln()
        + 1.5 * tev.ln() - (HYREC_EI_EV / 4.0) / tev).exp())?;
    let b = (-HYREC_E21_EV / tev).exp();
    let r_alpha = output((HYREC_LYA_PER_CM3 * 1e6) * (hubble_s / n_h_m3) / x1)?;
    let rates = ShellRates::new(beta_p, HYREC_LAMBDA_2GAMMA_S, r_alpha, b)?;
    Ok(SourceBoundPoint { alpha_b_m3_s: alpha, r_alpha_s: r_alpha, rates })
}

pub fn cm3_rate_to_si(alpha_cm3_s: f64) -> Result<f64, HydrogenError> {
    nonnegative(alpha_cm3_s)?;
    output(alpha_cm3_s * 1e-6)
}
pub fn cm3_density_to_si(n_h_cm3: f64) -> Result<f64, HydrogenError> {
    nonnegative(n_h_cm3)?;
    output(n_h_cm3 * 1e6)
}
