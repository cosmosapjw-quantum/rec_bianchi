//! Implicit matched-differential hydrogen history step (BASS R113 THEORY D9).
//!
//! On the e-fold clock eta = ln(a/a_emit) an anisotropic hydrogen ionized
//! fraction x follows a reference history x_ref (an FLRW HYREC table) through
//!
//!   x_{n+1} - x_n = (x_ref,n+1 - x_ref,n)
//!                 + d_eta [ r_ani(x_{n+1}) / (gamma H) - r_ref / H_ref ],
//!
//! where r are net proper-time collapsed-Peebles rates dx/dt [s^-1] of the same
//! TLA closure ([`anisotropic_peebles_rate`]), r_ref is evaluated on the reference
//! state at eta_{n+1}, gamma H is the material clock (`matched_hydrogen_rhs`) and
//! H_ref the reference expansion rate. The step is backward Euler in the matched
//! difference: first order and L-stable in the stiff Saha regime. If the
//! anisotropic and reference inputs coincide and x_n = x_ref,n, its root is
//! x_ref,n+1 to rounding for every step size, so the HYREC baseline is inherited
//! exactly and only the anisotropic response is integrated.
//!
//! The residual G(x) is increasing because the Peebles rate decreases with the
//! ionized fraction, so the root is bracketed on [0, X_MAX] and found by a
//! safeguarded Illinois regula falsi. This is a hydrogen-only matched correction;
//! helium and the matter temperature enter through the supplied closure.
use crate::anisotropic::{
    anisotropic_two_temperature_source, compton_temperature_k, AnisotropyError, DirectionalSky,
};
use crate::hydrogen_peebles::{peebles_rhs, RetainedState};

/// Upper end of the ionized-fraction bracket (the Peebles closure needs x1 > 0).
pub const X_MAX: f64 = 1.0 - 1e-12;

/// Net collapsed-Peebles rate dx_p/dt [s^-1] on a directional sky (atom rest
/// frame) at hydrogen ionized fraction `xp`. The matter temperature is the
/// supplied value or, if None, the Compton temperature of the sky.
pub fn anisotropic_peebles_rate(
    sky: &DirectionalSky,
    n_h_m3: f64,
    hubble_s: f64,
    xp: f64,
    matter_temperature_k: Option<f64>,
) -> Result<f64, AnisotropyError> {
    let tm = match matter_temperature_k {
        Some(t) => t,
        None => compton_temperature_k(sky)?,
    };
    let source = anisotropic_two_temperature_source(
        sky,
        n_h_m3,
        hubble_s,
        RetainedState { xp, x2: 0.0 },
        tm,
    )?;
    peebles_rhs(n_h_m3, source.alpha_b_m3_s, source.rates, xp)
        .map_err(|_| AnisotropyError::Hydrogen)
}

/// The same rate for an isotropic Planck sky at `temperature_k` with f = 1.
pub fn isotropic_peebles_rate(
    temperature_k: f64,
    n_h_m3: f64,
    hubble_s: f64,
    xp: f64,
) -> Result<f64, AnisotropyError> {
    let sky = DirectionalSky {
        weights: &[1.0],
        temperature_k: &[temperature_k],
        expansion_factor: &[1.0],
    };
    anisotropic_peebles_rate(&sky, n_h_m3, hubble_s, xp, None)
}

/// Inputs of one matched step on [eta_n, eta_n+1].
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct MatchedStep {
    pub x_prev: f64,
    pub x_ref_prev: f64,
    pub x_ref_next: f64,
    pub d_eta: f64,
    /// Lorentz factor of the atoms relative to the normal congruence.
    pub gamma: f64,
    /// Normal-frame expansion rate H [s^-1] at eta_n+1.
    pub hubble_s: f64,
    /// Reference rate r_ref = dx_ref/dt [s^-1] at eta_n+1.
    pub reference_rate_s: f64,
    pub reference_hubble_s: f64,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum MatchedStepError {
    Domain,
    Rate(AnisotropyError),
    NoBracket,
    NoConvergence,
}

/// Solve the implicit matched step for x_n+1 with the anisotropic rate closure
/// `rate(x)` [s^-1]. Returns x_n+1 in [0, X_MAX].
pub fn implicit_matched_step<F>(step: &MatchedStep, rate: F) -> Result<f64, MatchedStepError>
where
    F: Fn(f64) -> Result<f64, AnisotropyError>,
{
    let s = step;
    if ![
        s.x_prev,
        s.x_ref_prev,
        s.x_ref_next,
        s.d_eta,
        s.gamma,
        s.hubble_s,
        s.reference_rate_s,
        s.reference_hubble_s,
    ]
    .iter()
    .all(|v| v.is_finite())
        || s.d_eta < 0.0
        || s.gamma < 1.0
        || s.hubble_s <= 0.0
        || s.reference_hubble_s <= 0.0
        || !(0.0..=1.0).contains(&s.x_prev)
        || !(0.0..=1.0).contains(&s.x_ref_prev)
        || !(0.0..=1.0).contains(&s.x_ref_next)
    {
        return Err(MatchedStepError::Domain);
    }
    let clock = s.gamma * s.hubble_s;
    let reference = s.reference_rate_s / s.reference_hubble_s;
    let base = s.x_prev + (s.x_ref_next - s.x_ref_prev);
    let g = |x: f64| -> Result<f64, MatchedStepError> {
        let r = rate(x).map_err(MatchedStepError::Rate)?;
        let value = x - base - s.d_eta * (r / clock - reference);
        if value.is_finite() {
            Ok(value)
        } else {
            Err(MatchedStepError::Rate(AnisotropyError::NonFinite))
        }
    };
    // Predictor: the reference increment, exact in the matched FLRW limit.
    let x0 = base.clamp(0.0, X_MAX);
    let g0 = g(x0)?;
    if g0 == 0.0 {
        return Ok(x0);
    }
    let (mut lo, mut hi, mut glo, mut ghi) = if g0 < 0.0 {
        (x0, X_MAX, g0, g(X_MAX)?)
    } else {
        (0.0, x0, g(0.0)?, g0)
    };
    if glo > 0.0 || ghi < 0.0 {
        return Err(MatchedStepError::NoBracket);
    }
    if glo == 0.0 {
        return Ok(lo);
    }
    if ghi == 0.0 {
        return Ok(hi);
    }
    let mut side = 0i8;
    for _ in 0..400 {
        let mut x = (lo * ghi - hi * glo) / (ghi - glo);
        if x.is_nan() || x <= lo || x >= hi {
            x = 0.5 * (lo + hi);
        }
        let gx = g(x)?;
        if gx == 0.0 {
            return Ok(x);
        }
        if gx < 0.0 {
            lo = x;
            glo = gx;
            if side == -1 {
                ghi *= 0.5;
            }
            side = -1;
        } else {
            hi = x;
            ghi = gx;
            if side == 1 {
                glo *= 0.5;
            }
            side = 1;
        }
        if hi - lo <= 4.0 * f64::EPSILON * hi.max(f64::MIN_POSITIVE) {
            return Ok(if glo.abs() <= ghi.abs() { lo } else { hi });
        }
    }
    Err(MatchedStepError::NoConvergence)
}
