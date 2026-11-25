//! R116: bounded species-resolved matched thermochemistry on eta=ln(a/a_emit).
//! Fractions per H nucleus. W=(1+fHe+xe) Tm [K]; evolve W, not an assumed
//! Compton-equilibrium temperature. SI proper rates, material clock gamma H.
//! This is tracer thermochemistry: the heat and binding-energy ledger does
//! not itself transfer energy to the Einstein or spectral photon sector.
//! NativeHeI uses independent-direction averages of the 2012 fast HeI source,
//! NOT a complete anisotropic line transfer/EMLA solution.
use crate::anisotropic::{
    A_2P1S_S, DirectionalSky, compton_temperature_k, photoionization_average_s, wien_average_ln,
};
use crate::hydrogen_peebles::{
    HYREC_E21_EV, HYREC_LAMBDA_2GAMMA_S, HYREC_LYA_PER_CM3, ShellRates, hyrec2_ppb_alpha_b_si,
};
use std::f64::consts::PI;

pub const KB_J_K: f64 = 1.380649e-23;
pub const EV_J: f64 = 1.602176634e-19;
const C_M_S: f64 = 299792458.;
const ME_KG: f64 = 9.1093837139e-31;
const SIGMA_T: f64 = 6.6524587051e-29;
const A_RAD: f64 = 7.565733250033928e-16;
const HEI_SOURCE_MIN_T: f64 = 3000.;
const HEI_SOURCE_MAX_T: f64 = 20000.;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Error {
    Domain,
    Radiation,
    HeliumCoverage,
    Nonfinite,
    Singular,
    NoConvergence,
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct State {
    /// Neutral H abundance. This avoids losing the tiny neutral fraction
    /// when the hydrogen ionization fraction is close to unity.
    pub x_hi: f64,
    pub x_heii: f64,
    pub x_heiii: f64,
    pub w_k: f64,
}
impl State {
    pub fn from_xp_tm(xp: f64, xheii: f64, xheiii: f64, tm: f64, fhe: f64) -> Result<Self, Error> {
        if !(0.0..=1.0).contains(&xp) {
            return Err(Error::Domain);
        }
        Self::from_hi_tm(1. - xp, xheii, xheiii, tm, fhe)
    }
    pub fn from_hi_tm(
        x_hi: f64,
        x_heii: f64,
        x_heiii: f64,
        tm: f64,
        fhe: f64,
    ) -> Result<Self, Error> {
        let mut s = Self {
            x_hi,
            x_heii,
            x_heiii,
            w_k: tm,
        };
        s.w_k *= s.chi(fhe);
        s.validate(fhe)?;
        Ok(s)
    }
    pub fn xp(self) -> f64 {
        1. - self.x_hi
    }
    pub fn xe(self) -> f64 {
        self.xp() + self.x_heii + 2. * self.x_heiii
    }
    pub fn chi(self, fhe: f64) -> f64 {
        1. + fhe + self.xe()
    }
    pub fn tm(self, fhe: f64) -> f64 {
        self.w_k / self.chi(fhe)
    }
    pub fn x_hei(self, fhe: f64) -> f64 {
        (fhe - self.x_heii) - self.x_heiii
    }
    pub fn thermal_j_per_h(self) -> f64 {
        1.5 * KB_J_K * self.w_k
    }
    pub fn binding_j_per_h(self) -> f64 {
        EV_J * (13.598286071938324 * self.xp()
            + 24.587389 * (self.x_heii + self.x_heiii)
            + 54.417765 * self.x_heiii)
    }
    pub fn validate(self, fhe: f64) -> Result<(), Error> {
        if !fhe.is_finite()
            || fhe < 0.
            || !(0.0..=1.0).contains(&self.x_hi)
            || !self.x_heii.is_finite()
            || !self.x_heiii.is_finite()
            || self.x_heii < 0.
            || self.x_heiii < 0.
            || self.x_hei(fhe) < 0.
            || !self.w_k.is_finite()
            || self.w_k <= 0.
            || !self.tm(fhe).is_finite()
            || self.tm(fhe) <= 0.
        {
            Err(Error::Domain)
        } else {
            Ok(())
        }
    }
    fn array(self) -> [f64; 4] {
        [self.x_hi, self.x_heii, self.x_heiii, self.w_k]
    }
    fn from_array(a: [f64; 4]) -> Self {
        Self {
            x_hi: a[0],
            x_heii: a[1],
            x_heiii: a[2],
            w_k: a[3],
        }
    }
}
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct TransitionRates {
    pub ionization_s: f64,
    pub recombination_m3_s: f64,
}
impl TransitionRates {
    pub const ZERO: Self = Self {
        ionization_s: 0.,
        recombination_m3_s: 0.,
    };
    fn valid(self) -> bool {
        [self.ionization_s, self.recombination_m3_s]
            .iter()
            .all(|v| v.is_finite() && *v >= 0.)
    }
}
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum HeliumModel {
    /// Post-HeIII phase only: use the source-locked fast HeI prescription.
    NativeHeI,
    /// H-only owner phase: both helium ion fractions must already be zero.
    /// This does not silently discard residual helium.
    NeutralHelium,
    /// Explicit caller-owned rates, not an internally certified HeIII model.
    Supplied {
        hei: TransitionRates,
        heii: TransitionRates,
    },
}
impl HeliumModel {
    fn active(self, fhe: f64) -> [bool; 4] {
        [
            true,
            fhe > 0. && self != Self::NeutralHelium,
            fhe > 0. && matches!(self, Self::Supplied { .. }),
            true,
        ]
    }
    fn check(self, y: State) -> Result<(), Error> {
        match self {
            Self::NativeHeI if y.x_heiii != 0. => Err(Error::HeliumCoverage),
            Self::NeutralHelium if y.x_heii != 0. || y.x_heiii != 0. => Err(Error::HeliumCoverage),
            _ => Ok(()),
        }
    }
}
#[derive(Debug, Clone)]
struct Ray {
    w: f64,
    t: f64,
    f: f64,
}
#[derive(Debug, Clone)]
pub struct Point {
    rays: Vec<Ray>,
    n_h_m3: f64,
    hubble_s: f64,
    gamma: f64,
    /// Theta_b/(gamma_b H), which need not be 3.
    expansion_ratio: f64,
    /// External kinetic thermal heating [J/s per H], not binding or bulk recoil.
    external_heat_j_s_per_h: f64,
    helium: HeliumModel,
    compton_temperature_k: f64,
    energy_j_m3: f64,
    beta_p_s: f64,
    wien: f64,
}
impl Point {
    pub fn new(
        sky: &DirectionalSky,
        n_h_m3: f64,
        hubble_s: f64,
        gamma: f64,
        expansion_ratio: f64,
        external_heat_j_s_per_h: f64,
        helium: HeliumModel,
    ) -> Result<Self, Error> {
        sky.validate().map_err(|_| Error::Radiation)?;
        if ![
            n_h_m3,
            hubble_s,
            gamma,
            expansion_ratio,
            external_heat_j_s_per_h,
        ]
        .iter()
        .all(|v| v.is_finite())
            || n_h_m3 <= 0.
            || hubble_s <= 0.
            || gamma < 1.
            || !(gamma * hubble_s).is_finite()
        {
            return Err(Error::Domain);
        }
        if let HeliumModel::Supplied { hei, heii } = helium {
            if !hei.valid() || !heii.valid() {
                return Err(Error::Domain);
            }
        }
        let sum = sky.weights.iter().sum::<f64>();
        if !sum.is_finite() || sum <= 0. {
            return Err(Error::Radiation);
        }
        let rays = sky
            .weights
            .iter()
            .zip(sky.temperature_k)
            .zip(sky.expansion_factor)
            .map(|((&w, &t), &f)| Ray { w: w / sum, t, f })
            .collect::<Vec<_>>();
        if helium == HeliumModel::NativeHeI
            && rays
                .iter()
                .any(|r| !(HEI_SOURCE_MIN_T..=HEI_SOURCE_MAX_T).contains(&r.t))
        {
            return Err(Error::HeliumCoverage);
        }
        let t0 = rays[0].t;
        let compton_temperature_k = if rays.iter().all(|r| r.t == t0) {
            t0
        } else {
            compton_temperature_k(sky).map_err(|_| Error::Radiation)?
        };
        let energy_j_m3 = A_RAD * rays.iter().map(|r| r.w * r.t.powi(4)).sum::<f64>();
        let beta_p_s = photoionization_average_s(sky).map_err(|_| Error::Radiation)?;
        let wien = wien_average_ln(HYREC_E21_EV, sky, true)
            .map_err(|_| Error::Radiation)?
            .exp();
        if !energy_j_m3.is_finite()
            || energy_j_m3 <= 0.
            || !beta_p_s.is_finite()
            || !wien.is_finite()
        {
            return Err(Error::Nonfinite);
        }
        Ok(Self {
            rays,
            n_h_m3,
            hubble_s,
            gamma,
            expansion_ratio,
            external_heat_j_s_per_h,
            helium,
            compton_temperature_k,
            energy_j_m3,
            beta_p_s,
            wien,
        })
    }
    pub fn compton_temperature_k(&self) -> f64 {
        self.compton_temperature_k
    }
    pub fn energy_j_m3(&self) -> f64 {
        self.energy_j_m3
    }
    pub fn clock_s(&self) -> f64 {
        self.gamma * self.hubble_s
    }
}

fn escape(tau: f64) -> f64 {
    if tau == 0. {
        1.
    } else {
        -(-tau).exp_m1() / tau
    }
}

/// Original May/Oct 2012 HyRec helium.c rate with fsR=meR=1, at local
/// scalar radiation temperature, density and expansion. Formula assumes
/// excited HeI levels in equilibrium with the continuum and includes
/// H continuum and intercombination escape. No HeIII source.
/// A small-depth guard is a numerical/model domain limit, not a calibrated
/// anisotropic validity threshold. Temperature range is likewise bounded.
pub fn native_hei_rate_s(y: State, fhe: f64, n: f64, h: f64, tr: f64) -> Result<f64, Error> {
    y.validate(fhe)?;
    if y.x_heiii != 0.
        || !(HEI_SOURCE_MIN_T..=HEI_SOURCE_MAX_T).contains(&tr)
        || !n.is_finite()
        || n <= 0.
        || !h.is_finite()
        || h <= 0.
    {
        return Err(Error::HeliumCoverage);
    }
    let tau = 4.277e-14 * n / h * y.x_hei(fhe);
    if !tau.is_finite() || tau < 1. {
        return Err(Error::HeliumCoverage);
    }
    let s0 = 4. * 2.414194e21 * tr * tr.sqrt() / n;
    let s = s0 * (-285325. / tr).exp();
    let y2s = (46090. / tr).exp() / s0;
    let y2p = 3. * (39101. / tr).exp() / s0;
    // Reciprocal continuum scale avoids division by a vanishing H I fraction.
    let eta_c = n * y.x_hi / (9.15776e28 * h);
    let width = 1.976e6 / -(-6989. / tr).exp_m1()
        + 6.03e6 / (19754. / tr).exp_m1()
        + 1.06e8 / (21539. / tr).exp_m1()
        + 2.18e6 / (28496. / tr).exp_m1()
        + 3.37e7 / (29224. / tr).exp_m1()
        + 1.04e6 / (32414. / tr).exp_m1()
        + 1.51e7 / (32781. / tr).exp_m1();
    let tauc = width * tau / (4. * PI * PI) * eta_c;
    let enh = (1. + PI * PI * tauc).sqrt() + 7.74 * tauc / (1. + 70. * tauc);
    let pesc = enh / tau
        + (-(-1.023e-7 * tau).exp_m1())
            * (0.964525 * (2947. / tr).exp() - enh * (-6.14e13 * eta_c).exp())
            / tau;
    let down = 50.94 * y2s + 1.7989e9 * y2p * pesc;
    let r = down * (y.x_hei(fhe) * s - y.x_heii * y.xe());
    if !r.is_finite() || !down.is_finite() || down < 0. || pesc < 0. {
        return Err(Error::Nonfinite);
    }
    Ok(r)
}

#[derive(Debug, Clone, Copy)]
pub struct Rate {
    pub d_x_hi: f64,
    pub d_x_heii: f64,
    pub d_x_heiii: f64,
    pub d_w_k: f64,
    /// Separate W source components per proper second.
    pub adiabatic_w_k_s: f64,
    pub compton_w_k_s: f64,
    pub external_w_k_s: f64,
}
impl Rate {
    fn array(self) -> [f64; 4] {
        [self.d_x_hi, self.d_x_heii, self.d_x_heiii, self.d_w_k]
    }
}

/// Proper-time rate. H uses actual xe*xp and the finite-depth escape limit
/// r_alpha=A at xHI=0. HeI directional effective source is conditional;
/// directional spectra are Planck approximations after spectral mixing.
pub fn proper_rate(y: State, fhe: f64, p: &Point) -> Result<Rate, Error> {
    y.validate(fhe)?;
    p.helium.check(y)?;
    let tm = y.tm(fhe);
    let xe = y.xe();
    let alpha = hyrec2_ppb_alpha_b_si(tm).map_err(|_| Error::Domain)?;
    let tau0 = A_2P1S_S * p.n_h_m3 * y.x_hi / (HYREC_LYA_PER_CM3 * 1e6 * p.hubble_s);
    if !tau0.is_finite() {
        return Err(Error::Nonfinite);
    }
    let ralpha = A_2P1S_S * p.rays.iter().map(|r| r.w * escape(tau0 / r.f)).sum::<f64>();
    let rates = ShellRates::new(p.beta_p_s, HYREC_LAMBDA_2GAMMA_S, ralpha, p.wien)
        .map_err(|_| Error::Domain)?;
    let d_x_hi = rates.c_factor() * (p.n_h_m3 * alpha * y.xp() * xe - p.beta_p_s * y.x_hi * p.wien);
    let (d_x_heii, d_x_heiii) = match p.helium {
        HeliumModel::NeutralHelium => (0., 0.),
        HeliumModel::NativeHeI => {
            if fhe == 0. {
                (0., 0.)
            } else {
                let mut v = 0.;
                for r in &p.rays {
                    v += r.w * native_hei_rate_s(y, fhe, p.n_h_m3, p.hubble_s * r.f, r.t)?;
                }
                (v, 0.)
            }
        }
        HeliumModel::Supplied { hei, heii } => {
            let ne = p.n_h_m3 * xe;
            let r1 = y.x_hei(fhe) * hei.ionization_s - ne * y.x_heii * hei.recombination_m3_s;
            let r2 = y.x_heii * heii.ionization_s - ne * y.x_heiii * heii.recombination_m3_s;
            (r1 - r2, r2)
        }
    };
    let adiabatic_w_k_s = -(2. / 3.) * p.expansion_ratio * p.clock_s() * y.w_k;
    let gamma0 = 8. * SIGMA_T * p.energy_j_m3 / (3. * ME_KG * C_M_S);
    let compton_w_k_s = gamma0 * xe * (p.compton_temperature_k - tm);
    let external_w_k_s = 2. * p.external_heat_j_s_per_h / (3. * KB_J_K);
    let d_w_k = adiabatic_w_k_s + compton_w_k_s + external_w_k_s;
    let out = Rate {
        d_x_hi,
        d_x_heii,
        d_x_heiii,
        d_w_k,
        adiabatic_w_k_s,
        compton_w_k_s,
        external_w_k_s,
    };
    if out.array().iter().any(|v| !v.is_finite()) {
        Err(Error::Nonfinite)
    } else {
        Ok(out)
    }
}

#[derive(Debug, Clone, Copy, Default)]
pub struct StepDiagnostics {
    pub iterations: usize,
    /// Max scaled nonlinear residual in the solved physical coordinates.
    pub scaled_residual: f64,
    pub physical_adiabatic_j_per_h: f64,
    pub physical_compton_j_per_h: f64,
    pub physical_external_j_per_h: f64,
    /// Reference increment minus reference RHS; not physical heat.
    pub matched_thermal_correction_j_per_h: f64,
    pub thermal_balance_defect_j_per_h: f64,
    /// Chemical ionization energy change (separate from heat ledger).
    pub binding_change_j_per_h: f64,
}

fn linear_solve(mut a: [[f64; 4]; 4], mut b: [f64; 4]) -> Result<[f64; 4], Error> {
    for j in 0..4 {
        let k = (j..4)
            .max_by(|&p, &q| a[p][j].abs().total_cmp(&a[q][j].abs()))
            .unwrap();
        a.swap(j, k);
        b.swap(j, k);
        let pivot = a[j][j];
        if !pivot.is_finite() || pivot.abs() < 1e-30 {
            return Err(Error::Singular);
        }
        for i in j + 1..4 {
            let m = a[i][j] / pivot;
            for k in j..4 {
                a[i][k] -= m * a[j][k];
            }
            b[i] -= m * b[j];
        }
    }
    let mut x = [0.; 4];
    for j in (0..4).rev() {
        x[j] = (b[j] - (j + 1..4).map(|k| a[j][k] * x[k]).sum::<f64>()) / a[j][j];
    }
    if x.iter().all(|v| v.is_finite()) {
        Ok(x)
    } else {
        Err(Error::Nonfinite)
    }
}
fn maxabs(a: [f64; 4]) -> f64 {
    a.iter().map(|v| v.abs()).fold(0., f64::max)
}

/// Backward Euler for matched DIFFERENCES. Reference points and actual
/// coefficients must belong to a common phase (no hidden Saha/HeI handover).
/// The reference increment is inherited exactly at zero response, even if
/// the reduced closure does not reproduce the full reference history.
/// No clipping of species or resetting of offsets on a source transition.
/// The caller handles step rejection/subdivision and stage-consistent sky.
pub fn matched_step(
    prev: State,
    ref_prev: State,
    ref_next: State,
    h: f64,
    fhe: f64,
    actual: &Point,
    reference: &Point,
) -> Result<(State, StepDiagnostics), Error> {
    for y in [prev, ref_prev, ref_next] {
        y.validate(fhe)?;
        reference.helium.check(y)?;
        actual.helium.check(y)?;
    }
    if !h.is_finite()
        || h < 0.
        || std::mem::discriminant(&actual.helium) != std::mem::discriminant(&reference.helium)
    {
        return Err(Error::Domain);
    }
    if h == 0. {
        if ref_prev != ref_next {
            return Err(Error::Domain);
        }
        return Ok((prev, StepDiagnostics::default()));
    }
    let rp = ref_prev.array();
    let rn = ref_next.array();
    let yn = prev.array();
    let active = actual.helium.active(fhe);
    let scales = [
        rp[0].max(rn[0]).max(yn[0]).max(1e-10),
        rp[1].max(rn[1]).max(yn[1]).max(1e-8),
        rp[2].max(rn[2]).max(yn[2]).max(1e-8),
        rn[3],
    ];
    let delta0: [f64; 4] = std::array::from_fn(|i| (yn[i] - rp[i]) / scales[i]);
    let rref = proper_rate(ref_next, fhe, reference)?;
    let ref_rhs = rref.array().map(|x| x / reference.clock_s());
    let to_state =
        |d: [f64; 4]| State::from_array(std::array::from_fn(|i| rn[i] + scales[i] * d[i]));
    let residual = |d: [f64; 4]| -> Result<[f64; 4], Error> {
        let r = proper_rate(to_state(d), fhe, actual)?.array();
        Ok(std::array::from_fn(|i| {
            d[i] - delta0[i] - h * (r[i] / actual.clock_s() - ref_rhs[i]) / scales[i]
        }))
    };
    let finish =
        |d: [f64; 4], iterations: usize, r: [f64; 4]| -> Result<(State, StepDiagnostics), Error> {
            let y = to_state(d);
            let rate = proper_rate(y, fhe, actual)?;
            let coeff = 1.5 * KB_J_K;
            let ad = coeff * h * rate.adiabatic_w_k_s / actual.clock_s();
            let cp = coeff * h * rate.compton_w_k_s / actual.clock_s();
            let ext = coeff * h * rate.external_w_k_s / actual.clock_s();
            let corr = coeff * (rn[3] - rp[3] - h * ref_rhs[3]);
            Ok((
                y,
                StepDiagnostics {
                    iterations,
                    scaled_residual: maxabs(r),
                    physical_adiabatic_j_per_h: ad,
                    physical_compton_j_per_h: cp,
                    physical_external_j_per_h: ext,
                    matched_thermal_correction_j_per_h: corr,
                    thermal_balance_defect_j_per_h: y.thermal_j_per_h()
                        - prev.thermal_j_per_h()
                        - ad
                        - cp
                        - ext
                        - corr,
                    binding_change_j_per_h: y.binding_j_per_h() - prev.binding_j_per_h(),
                },
            ))
        };
    let (d, iterations, r) = solve_matched_root(delta0, scales, active, to_state, residual)?;
    finish(d, iterations, r)
}

fn solve_matched_root(
    delta0: [f64; 4],
    scales: [f64; 4],
    active: [bool; 4],
    to_state: impl Fn([f64; 4]) -> State,
    residual: impl Fn([f64; 4]) -> Result<[f64; 4], Error>,
) -> Result<([f64; 4], usize, [f64; 4]), Error> {
    // Predictor may lie outside simplex if the reference itself crossed a
    // boundary. Start from the new reference instead; never clip the state.
    let mut d = delta0;
    if residual(d).is_err() {
        d = [0.; 4];
    }
    let mut r = residual(d)?;
    if maxabs(r) == 0. {
        return Ok((d, 0, r));
    }
    for iteration in 1..=40 {
        let mut jac = [[0.; 4]; 4];
        let y = to_state(d).array();
        for j in 0..4 {
            if !active[j] {
                jac[j][j] = 1.;
                continue;
            }
            let mut step = 1e-5 * (y[j].abs() / scales[j]).max(1e-4);
            let mut found = false;
            for _ in 0..16 {
                let mut plus = d;
                let mut minus = d;
                plus[j] += step;
                minus[j] -= step;
                let p = residual(plus);
                let m = residual(minus);
                match (p, m) {
                    (Ok(p), Ok(m)) => {
                        for i in 0..4 {
                            jac[i][j] = (p[i] - m[i]) / (2. * step);
                        }
                        found = true;
                        break;
                    }
                    (Ok(p), Err(_)) => {
                        for i in 0..4 {
                            jac[i][j] = (p[i] - r[i]) / step;
                        }
                        found = true;
                        break;
                    }
                    (Err(_), Ok(m)) => {
                        for i in 0..4 {
                            jac[i][j] = (r[i] - m[i]) / step;
                        }
                        found = true;
                        break;
                    }
                    _ => step *= 0.25,
                }
            }
            if !found {
                return Err(Error::NoConvergence);
            }
        }
        // Row scaling by the Jacobian norm gives a residual in state units
        // even during extremely stiff Saha/Compton relaxation.
        let rows = jac.map(|row| row.iter().map(|x| x.abs()).sum::<f64>().max(1.));
        let scaled_norm = |v: [f64; 4]| maxabs(std::array::from_fn(|i| v[i] / rows[i]));
        let old = scaled_norm(r);
        let correction = linear_solve(jac, r.map(|v| -v))?;
        // Resolve corrections on the scale of floating-point state
        // reconstruction, not a fixed 1e-11 abundance threshold.
        let tol = 8. * f64::EPSILON * (1. + maxabs(d) + maxabs(delta0));
        if maxabs(correction) <= tol && old <= tol {
            return Ok((d, iteration, r));
        }
        let mut accepted = false;
        let mut lambda = 1.;
        for _ in 0..30 {
            let q = std::array::from_fn(|i| d[i] + lambda * correction[i]);
            if let Ok(v) = residual(q) {
                if scaled_norm(v) < old {
                    d = q;
                    r = v;
                    accepted = true;
                    break;
                }
            }
            lambda *= 0.5;
        }
        if !accepted {
            return Err(Error::NoConvergence);
        }
    }
    Err(Error::NoConvergence)
}

/// One source-owned reference slice on eta=ln(a/a_emit). W, abundances and
/// H are interpolated from a single source; n_H and T_r follow FLRW scaling.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct ReferenceNode {
    pub eta: f64,
    pub state: State,
    pub n_h_m3: f64,
    pub h_s: f64,
    pub tr_k: f64,
}
#[derive(Debug, Clone, PartialEq)]
pub struct ReferenceHistory {
    f_he: f64,
    helium: HeliumModel,
    nodes: Vec<ReferenceNode>,
}
impl ReferenceHistory {
    pub fn parse(input: &str) -> Result<Self, Error> {
        let mut lines = input
            .lines()
            .filter(|l| !l.trim().is_empty() && !l.trim_start().starts_with('#'));
        if lines.next() != Some("rec_species_reference_v1") {
            return Err(Error::Domain);
        }
        let a = lines
            .next()
            .ok_or(Error::Domain)?
            .split_whitespace()
            .collect::<Vec<_>>();
        if a.len() != 2 || a[0] != "f_he" {
            return Err(Error::Domain);
        }
        let f_he = a[1].parse::<f64>().map_err(|_| Error::Domain)?;
        let helium = match lines.next() {
            Some("helium native_hei") => HeliumModel::NativeHeI,
            Some("helium neutral") => HeliumModel::NeutralHelium,
            _ => return Err(Error::HeliumCoverage),
        };
        if !lines.next().is_some_and(|l| {
            l.split_whitespace().eq([
                "eta", "x_hi", "x_heii", "x_heiii", "w_k", "n_h_m3", "h_s", "tr_k",
            ])
        }) {
            return Err(Error::Domain);
        }
        let mut nodes: Vec<ReferenceNode> = Vec::new();
        for line in lines {
            let v = line
                .split_whitespace()
                .map(str::parse::<f64>)
                .collect::<Result<Vec<_>, _>>()
                .map_err(|_| Error::Domain)?;
            if v.len() != 8
                || v.iter().any(|v| !v.is_finite())
                || v[5] <= 0.
                || v[6] <= 0.
                || v[7] <= 0.
            {
                return Err(Error::Domain);
            }
            let state = State::from_array([v[1], v[2], v[3], v[4]]);
            state.validate(f_he)?;
            helium.check(state)?;
            if let Some(p) = nodes.last() {
                if v[0] <= p.eta {
                    return Err(Error::Domain);
                }
                let first = nodes[0];
                if (v[5] / first.n_h_m3 * (-3. * v[0]).exp().recip() - 1.).abs() > 1e-10
                    || (v[7] / first.tr_k * (-v[0]).exp().recip() - 1.).abs() > 1e-10
                {
                    return Err(Error::Domain);
                }
            } else if v[0] != 0. {
                return Err(Error::Domain);
            }
            nodes.push(ReferenceNode {
                eta: v[0],
                state,
                n_h_m3: v[5],
                h_s: v[6],
                tr_k: v[7],
            });
        }
        if nodes.len() < 2 {
            return Err(Error::Domain);
        }
        Ok(Self {
            f_he,
            helium,
            nodes,
        })
    }
    pub fn f_he(&self) -> f64 {
        self.f_he
    }
    pub fn helium(&self) -> HeliumModel {
        self.helium
    }
    pub fn nodes(&self) -> &[ReferenceNode] {
        &self.nodes
    }
    pub fn duration(&self) -> f64 {
        self.nodes.last().unwrap().eta
    }
    pub fn at(&self, eta: f64) -> Result<ReferenceNode, Error> {
        let first = self.nodes[0];
        let end = self.duration();
        let tol = 32. * f64::EPSILON * (1. + end);
        if !eta.is_finite() || eta < -tol || eta > end + tol {
            return Err(Error::Domain);
        }
        let t = eta.clamp(0., end);
        let i = self
            .nodes
            .partition_point(|n| n.eta <= t)
            .saturating_sub(1)
            .min(self.nodes.len() - 2);
        let a = self.nodes[i];
        let b = self.nodes[i + 1];
        if t == a.eta {
            return Ok(a);
        }
        if t == b.eta {
            return Ok(b);
        }
        let u = (t - a.eta) / (b.eta - a.eta);
        let aa = a.state.array();
        let bb = b.state.array();
        let state = State::from_array(std::array::from_fn(|j| aa[j] + u * (bb[j] - aa[j])));
        state.validate(self.f_he)?;
        self.helium.check(state)?;
        Ok(ReferenceNode {
            eta: t,
            state,
            n_h_m3: first.n_h_m3 * (-3. * t).exp(),
            h_s: a.h_s * (u * (b.h_s / a.h_s).ln()).exp(),
            tr_k: first.tr_k * (-t).exp(),
        })
    }
    pub fn point(&self, node: ReferenceNode) -> Result<Point, Error> {
        Point::new(
            &DirectionalSky {
                weights: &[1.],
                temperature_k: &[node.tr_k],
                expansion_factor: &[1.],
            },
            node.n_h_m3,
            node.h_s,
            1.,
            3.,
            0.,
            self.helium,
        )
    }
    /// Min linear reference electron fraction over the full interval, to
    /// reject a negative offset before a legacy opacity path can clamp it.
    pub fn minimum_xe(&self, start: f64, end: f64) -> Result<f64, Error> {
        if start > end {
            return Err(Error::Domain);
        }
        let mut x = self.at(start)?.state.xe().min(self.at(end)?.state.xe());
        let i = self.nodes.partition_point(|n| n.eta <= start);
        for n in &self.nodes[i..] {
            if n.eta >= end {
                break;
            }
            x = x.min(n.state.xe());
        }
        Ok(x)
    }
}

/// Alexander's two-stage, stiffly accurate L-stable SDIRK.
pub const SDIRK_GAMMA: f64 = 1. - std::f64::consts::FRAC_1_SQRT_2;

/// An accepted first stage, tied to the initial physical/reference state and
/// full step. Carries the increment in difference coordinates rather than
/// subtracting two reconstructed physical states (important near equilibrium).
#[derive(Clone, Debug)]
pub struct SdirkFirst {
    prev: State,
    ref_prev: State,
    state: State,
    h: f64,
    fhe: f64,
    mode: HeliumModel,
    delta0: [f64; 4],
    increment: [f64; 4],
    heat: [f64; 3],
    ref_w_rhs: f64,
    iterations: usize,
    residual: f64,
}
impl SdirkFirst {
    pub fn state(&self) -> State {
        self.state
    }
    pub fn iterations(&self) -> usize {
        self.iterations
    }
    pub fn scaled_residual(&self) -> f64 {
        self.residual
    }
}
struct StageRoot {
    state: State,
    delta: [f64; 4],
    increment: [f64; 4],
    heat: [f64; 3],
    ref_w_rhs: f64,
    iterations: usize,
    residual: f64,
}
fn implicit_difference_stage(
    base: [f64; 4],
    ref_y: State,
    diag_h: f64,
    fhe: f64,
    actual: &Point,
    reference: &Point,
) -> Result<StageRoot, Error> {
    ref_y.validate(fhe)?;
    actual.helium.check(ref_y)?;
    reference.helium.check(ref_y)?;
    if !diag_h.is_finite()
        || diag_h <= 0.
        || base.iter().any(|x| !x.is_finite())
        || std::mem::discriminant(&actual.helium) != std::mem::discriminant(&reference.helium)
    {
        return Err(Error::Domain);
    }
    let rn = ref_y.array();
    let scales = std::array::from_fn(|i| {
        rn[i]
            .abs()
            .max((rn[i] + base[i]).abs())
            .max([1e-10, 1e-8, 1e-8, 1e-30][i])
    });
    let delta0 = std::array::from_fn(|i| base[i] / scales[i]);
    let to_state =
        |d: [f64; 4]| State::from_array(std::array::from_fn(|i| rn[i] + scales[i] * d[i]));
    let rref = proper_rate(ref_y, fhe, reference)?
        .array()
        .map(|x| x / reference.clock_s());
    let residual = |d: [f64; 4]| -> Result<[f64; 4], Error> {
        let r = proper_rate(to_state(d), fhe, actual)?.array();
        Ok(std::array::from_fn(|i| {
            d[i] - delta0[i] - diag_h * (r[i] / actual.clock_s() - rref[i]) / scales[i]
        }))
    };
    let (d, iterations, r) = solve_matched_root(
        delta0,
        scales,
        actual.helium.active(fhe),
        to_state,
        residual,
    )?;
    let y = to_state(d);
    let rate = proper_rate(y, fhe, actual)?;
    let heat = [
        rate.adiabatic_w_k_s,
        rate.compton_w_k_s,
        rate.external_w_k_s,
    ]
    .map(|v| v / actual.clock_s());
    Ok(StageRoot {
        state: y,
        delta: std::array::from_fn(|i| scales[i] * d[i]),
        increment: std::array::from_fn(|i| scales[i] * (d[i] - delta0[i])),
        heat,
        ref_w_rhs: rref[3],
        iterations,
        residual: maxabs(r),
    })
}
/// SDIRK first stage at eta_n + gamma*h. Caller supplies actual and reference
/// environment at that time; geometry/opacity iteration is not owned by REC.
pub fn sdirk_first(
    prev: State,
    ref_prev: State,
    ref_stage: State,
    h: f64,
    fhe: f64,
    actual: &Point,
    reference: &Point,
) -> Result<SdirkFirst, Error> {
    for y in [prev, ref_prev] {
        y.validate(fhe)?;
        actual.helium.check(y)?;
        reference.helium.check(y)?;
    }
    let delta0 = std::array::from_fn(|i| prev.array()[i] - ref_prev.array()[i]);
    let a = implicit_difference_stage(delta0, ref_stage, SDIRK_GAMMA * h, fhe, actual, reference)?;
    Ok(SdirkFirst {
        prev,
        ref_prev,
        state: a.state,
        h,
        fhe,
        mode: actual.helium,
        delta0,
        increment: a.increment,
        heat: a.heat,
        ref_w_rhs: a.ref_w_rhs,
        iterations: a.iterations,
        residual: a.residual,
    })
}
/// Stiffly accurate second stage at eta_n+h, with full-step weighted heat
/// ledger. First-stage algebraic increment supplies the explicit tableau
/// term, avoiding subtractive cancellation in the stiff rate difference.
pub fn sdirk_second(
    first: &SdirkFirst,
    ref_next: State,
    actual: &Point,
    reference: &Point,
) -> Result<(State, StepDiagnostics), Error> {
    if std::mem::discriminant(&first.mode) != std::mem::discriminant(&actual.helium) {
        return Err(Error::HeliumCoverage);
    }
    let g = SDIRK_GAMMA;
    let base = std::array::from_fn(|i| first.delta0[i] + ((1. - g) / g) * first.increment[i]);
    let b = implicit_difference_stage(base, ref_next, g * first.h, first.fhe, actual, reference)?;
    let coeff = 1.5 * KB_J_K;
    let h = first.h;
    let heat: [f64; 3] =
        std::array::from_fn(|i| coeff * h * ((1. - g) * first.heat[i] + g * b.heat[i]));
    let corr = coeff
        * (ref_next.w_k - first.ref_prev.w_k - h * ((1. - g) * first.ref_w_rhs + g * b.ref_w_rhs));
    let y = b.state;
    // b.delta retained internally for future stage/correction APIs.
    if b.delta.iter().any(|x| !x.is_finite()) {
        return Err(Error::Nonfinite);
    }
    Ok((
        y,
        StepDiagnostics {
            iterations: first.iterations + b.iterations,
            scaled_residual: first.residual.max(b.residual),
            physical_adiabatic_j_per_h: heat[0],
            physical_compton_j_per_h: heat[1],
            physical_external_j_per_h: heat[2],
            matched_thermal_correction_j_per_h: corr,
            thermal_balance_defect_j_per_h: y.thermal_j_per_h()
                - first.prev.thermal_j_per_h()
                - heat.iter().sum::<f64>()
                - corr,
            binding_change_j_per_h: y.binding_j_per_h() - first.prev.binding_j_per_h(),
        },
    ))
}

/// Independent physical backward-Euler step: no reference state, reference
/// increment, or matched thermal correction. Caller supplies actual geometry,
/// density and radiation at the end of the step; eta uses normal H.
pub fn standalone_step(
    prev: State,
    h: f64,
    fhe: f64,
    actual: &Point,
) -> Result<(State, StepDiagnostics), Error> {
    prev.validate(fhe)?;
    actual.helium.check(prev)?;
    if !h.is_finite() || h < 0. {
        return Err(Error::Domain);
    }
    if h == 0. {
        return Ok((prev, StepDiagnostics::default()));
    }
    let y0 = prev.array();
    let scales = [y0[0].max(1e-10), y0[1].max(1e-8), y0[2].max(1e-8), y0[3]];
    let to_state =
        |d: [f64; 4]| State::from_array(std::array::from_fn(|i| y0[i] + scales[i] * d[i]));
    let residual = |d: [f64; 4]| -> Result<[f64; 4], Error> {
        let r = proper_rate(to_state(d), fhe, actual)?.array();
        Ok(std::array::from_fn(|i| {
            d[i] - h * r[i] / (actual.clock_s() * scales[i])
        }))
    };
    let (d, iterations, r) = solve_matched_root(
        [0.; 4],
        scales,
        actual.helium.active(fhe),
        to_state,
        residual,
    )?;
    let y = to_state(d);
    let rate = proper_rate(y, fhe, actual)?;
    let coeff = 1.5 * KB_J_K * h / actual.clock_s();
    let ad = coeff * rate.adiabatic_w_k_s;
    let cp = coeff * rate.compton_w_k_s;
    let ext = coeff * rate.external_w_k_s;
    Ok((
        y,
        StepDiagnostics {
            iterations,
            scaled_residual: maxabs(r),
            physical_adiabatic_j_per_h: ad,
            physical_compton_j_per_h: cp,
            physical_external_j_per_h: ext,
            matched_thermal_correction_j_per_h: 0.,
            thermal_balance_defect_j_per_h: y.thermal_j_per_h()
                - prev.thermal_j_per_h()
                - ad
                - cp
                - ext,
            binding_change_j_per_h: y.binding_j_per_h() - prev.binding_j_per_h(),
        },
    ))
}
