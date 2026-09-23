use crate::coverage::{CoverageError, d86_w};
use core::ops::{Add, AddAssign, Mul, Neg, Sub};
use std::f64::consts::PI;

pub const C_M_S: f64 = 299_792_458.0;
pub const H_J_S: f64 = 6.626_070_15e-34;
pub const HBAR_J_S: f64 = H_J_S / (2.0 * PI);
pub const KB_J_K: f64 = 1.380_649e-23;
pub const EV_J: f64 = 1.602_176_634e-19;
pub const ME_KG: f64 = 9.109_383_713_9e-31;
pub const MB_TO_M2: f64 = 1.0e-22;
pub const JACOBS_F_TO_MB: f64 = 8.067_283_725_760_34;

#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct Complex64 {
    pub re: f64,
    pub im: f64,
}
impl Complex64 {
    pub const fn new(re: f64, im: f64) -> Self {
        Self { re, im }
    }
    pub const fn conj(self) -> Self {
        Self {
            re: self.re,
            im: -self.im,
        }
    }
    pub fn abs(self) -> f64 {
        self.re.hypot(self.im)
    }
    pub const fn scale(self, x: f64) -> Self {
        Self {
            re: self.re * x,
            im: self.im * x,
        }
    }
    pub fn approx_eq(self, rhs: Self, tol: f64) -> bool {
        (self - rhs).abs() <= tol * (1.0 + self.abs() + rhs.abs())
    }
}
impl Add for Complex64 {
    type Output = Self;
    fn add(self, rhs: Self) -> Self {
        Self::new(self.re + rhs.re, self.im + rhs.im)
    }
}
impl AddAssign for Complex64 {
    fn add_assign(&mut self, rhs: Self) {
        *self = *self + rhs;
    }
}
impl Sub for Complex64 {
    type Output = Self;
    fn sub(self, rhs: Self) -> Self {
        Self::new(self.re - rhs.re, self.im - rhs.im)
    }
}
impl Neg for Complex64 {
    type Output = Self;
    fn neg(self) -> Self {
        Self::new(-self.re, -self.im)
    }
}
impl Mul for Complex64 {
    type Output = Self;
    fn mul(self, rhs: Self) -> Self {
        Self::new(
            self.re * rhs.re - self.im * rhs.im,
            self.re * rhs.im + self.im * rhs.re,
        )
    }
}
impl Mul<f64> for Complex64 {
    type Output = Self;
    fn mul(self, rhs: f64) -> Self {
        self.scale(rhs)
    }
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Mat2(pub [[Complex64; 2]; 2]);
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Mat3(pub [[Complex64; 3]; 3]);

impl core::ops::Index<usize> for Mat2 {
    type Output = [Complex64; 2];
    fn index(&self, i: usize) -> &Self::Output {
        &self.0[i]
    }
}
impl core::ops::IndexMut<usize> for Mat2 {
    fn index_mut(&mut self, i: usize) -> &mut Self::Output {
        &mut self.0[i]
    }
}
impl core::ops::Index<usize> for Mat3 {
    type Output = [Complex64; 3];
    fn index(&self, i: usize) -> &Self::Output {
        &self.0[i]
    }
}
impl core::ops::IndexMut<usize> for Mat3 {
    fn index_mut(&mut self, i: usize) -> &mut Self::Output {
        &mut self.0[i]
    }
}
impl From<[[Complex64; 2]; 2]> for Mat2 {
    fn from(x: [[Complex64; 2]; 2]) -> Self {
        Self(x)
    }
}
impl From<[[Complex64; 3]; 3]> for Mat3 {
    fn from(x: [[Complex64; 3]; 3]) -> Self {
        Self(x)
    }
}

impl Mat2 {
    pub const fn zero() -> Self {
        Self([[Complex64::new(0.0, 0.0); 2]; 2])
    }
    pub const fn identity() -> Self {
        Self([
            [Complex64::new(1.0, 0.0), Complex64::new(0.0, 0.0)],
            [Complex64::new(0.0, 0.0), Complex64::new(1.0, 0.0)],
        ])
    }
    pub fn scalar(x: f64) -> Self {
        Self::identity().scale(x)
    }
    pub fn trace(self) -> Complex64 {
        self[0][0] + self[1][1]
    }
    pub fn transpose(self) -> Self {
        let mut r = Self::zero();
        for i in 0..2 {
            for j in 0..2 {
                r[i][j] = self[j][i];
            }
        }
        r
    }
    pub fn dagger(self) -> Self {
        let mut r = Self::zero();
        for i in 0..2 {
            for j in 0..2 {
                r[i][j] = self[j][i].conj();
            }
        }
        r
    }
    pub fn scale(self, x: f64) -> Self {
        let mut r = self;
        for i in 0..2 {
            for j in 0..2 {
                r[i][j] = r[i][j].scale(x);
            }
        }
        r
    }
    pub fn max_abs(self) -> f64 {
        let mut m: f64 = 0.0;
        for i in 0..2 {
            for j in 0..2 {
                m = m.max(self[i][j].abs());
            }
        }
        m
    }
    pub fn is_hermitian(self, tol: f64) -> bool {
        for i in 0..2 {
            for j in 0..2 {
                if !self[i][j].approx_eq(self[j][i].conj(), tol) {
                    return false;
                }
            }
        }
        true
    }
}
impl Add for Mat2 {
    type Output = Self;
    fn add(self, rhs: Self) -> Self {
        let mut r = Self::zero();
        for i in 0..2 {
            for j in 0..2 {
                r[i][j] = self[i][j] + rhs[i][j];
            }
        }
        r
    }
}
impl Sub for Mat2 {
    type Output = Self;
    fn sub(self, rhs: Self) -> Self {
        let mut r = Self::zero();
        for i in 0..2 {
            for j in 0..2 {
                r[i][j] = self[i][j] - rhs[i][j];
            }
        }
        r
    }
}

impl Mat3 {
    pub const fn zero() -> Self {
        Self([[Complex64::new(0.0, 0.0); 3]; 3])
    }
    pub const fn identity() -> Self {
        Self([
            [
                Complex64::new(1.0, 0.0),
                Complex64::new(0.0, 0.0),
                Complex64::new(0.0, 0.0),
            ],
            [
                Complex64::new(0.0, 0.0),
                Complex64::new(1.0, 0.0),
                Complex64::new(0.0, 0.0),
            ],
            [
                Complex64::new(0.0, 0.0),
                Complex64::new(0.0, 0.0),
                Complex64::new(1.0, 0.0),
            ],
        ])
    }
    pub fn scalar(x: f64) -> Self {
        Self::identity().scale(x)
    }
    pub fn trace(self) -> Complex64 {
        self[0][0] + self[1][1] + self[2][2]
    }
    pub fn transpose(self) -> Self {
        let mut r = Self::zero();
        for i in 0..3 {
            for j in 0..3 {
                r[i][j] = self[j][i];
            }
        }
        r
    }
    pub fn dagger(self) -> Self {
        let mut r = Self::zero();
        for i in 0..3 {
            for j in 0..3 {
                r[i][j] = self[j][i].conj();
            }
        }
        r
    }
    pub fn scale(self, x: f64) -> Self {
        let mut r = self;
        for i in 0..3 {
            for j in 0..3 {
                r[i][j] = r[i][j].scale(x);
            }
        }
        r
    }
    pub fn max_abs(self) -> f64 {
        let mut m: f64 = 0.0;
        for i in 0..3 {
            for j in 0..3 {
                m = m.max(self[i][j].abs());
            }
        }
        m
    }
    pub fn is_hermitian(self, tol: f64) -> bool {
        for i in 0..3 {
            for j in 0..3 {
                if !self[i][j].approx_eq(self[j][i].conj(), tol) {
                    return false;
                }
            }
        }
        true
    }
}
impl Add for Mat3 {
    type Output = Self;
    fn add(self, rhs: Self) -> Self {
        let mut r = Self::zero();
        for i in 0..3 {
            for j in 0..3 {
                r[i][j] = self[i][j] + rhs[i][j];
            }
        }
        r
    }
}
impl Sub for Mat3 {
    type Output = Self;
    fn sub(self, rhs: Self) -> Self {
        let mut r = Self::zero();
        for i in 0..3 {
            for j in 0..3 {
                r[i][j] = self[i][j] - rhs[i][j];
            }
        }
        r
    }
}

fn mat2_mul(a: Mat2, b: Mat2) -> Mat2 {
    let mut r = Mat2::zero();
    for i in 0..2 {
        for j in 0..2 {
            for k in 0..2 {
                r[i][j] += a[i][k] * b[k][j];
            }
        }
    }
    r
}
fn anticommutator2(a: Mat2, b: Mat2) -> Mat2 {
    mat2_mul(a, b) + mat2_mul(b, a)
}
fn mat3_mul(a: Mat3, b: Mat3) -> Mat3 {
    let mut r = Mat3::zero();
    for i in 0..3 {
        for j in 0..3 {
            for k in 0..3 {
                r[i][j] += a[i][k] * b[k][j];
            }
        }
    }
    r
}
fn anticommutator3(a: Mat3, b: Mat3) -> Mat3 {
    mat3_mul(a, b) + mat3_mul(b, a)
}

pub type RealV = [[f64; 2]; 3];

fn v_x_vt(v: RealV, x: Mat2) -> Mat3 {
    let mut r = Mat3::zero();
    for a in 0..3 {
        for b in 0..3 {
            for i in 0..2 {
                for j in 0..2 {
                    r[a][b] += x[i][j].scale(v[a][i] * v[b][j]);
                }
            }
        }
    }
    r
}
fn vt_x_v(v: RealV, x: Mat3) -> Mat2 {
    let mut r = Mat2::zero();
    for i in 0..2 {
        for j in 0..2 {
            for a in 0..3 {
                for b in 0..3 {
                    r[i][j] += x[a][b].scale(v[a][i] * v[b][j]);
                }
            }
        }
    }
    r
}

#[derive(Clone, Copy, Debug)]
pub struct AngularSample {
    pub v: RealV,
    pub weight_sr: f64,
}
impl AngularSample {
    pub fn octahedron_6() -> Vec<Self> {
        let w = 4.0 * PI / 6.0;
        let vx = [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]];
        let vy = [[1.0, 0.0], [0.0, 0.0], [0.0, 1.0]];
        let vz = [[1.0, 0.0], [0.0, 1.0], [0.0, 0.0]];
        vec![
            Self {
                v: vx,
                weight_sr: w,
            },
            Self {
                v: vx,
                weight_sr: w,
            },
            Self {
                v: vy,
                weight_sr: w,
            },
            Self {
                v: vy,
                weight_sr: w,
            },
            Self {
                v: vz,
                weight_sr: w,
            },
            Self {
                v: vz,
                weight_sr: w,
            },
        ]
    }
}

#[derive(Clone, Copy, Debug)]
pub struct HeConstants {
    pub delta_s_ev: f64,
    pub delta_p_ev: f64,
    pub i_he_ev: f64,
    pub epsilon_ir_ev: f64,
    pub chi_p_ev: f64,
    pub chi_s_ev: f64,
    pub rydberg_ev: f64,
}
impl HeConstants {
    pub fn canonical() -> Self {
        let hc_ev_m = H_J_S * C_M_S / EV_J;
        let delta_s = 166_277.440_3 * 100.0 * hc_ev_m;
        let delta_p = 171_134.897_0 * 100.0 * hc_ev_m;
        let i_he = 198_310.669_1 * 100.0 * hc_ev_m;
        Self {
            delta_s_ev: delta_s,
            delta_p_ev: delta_p,
            i_he_ev: i_he,
            epsilon_ir_ev: delta_p - delta_s,
            chi_p_ev: i_he - delta_p,
            chi_s_ev: i_he - delta_s,
            rydberg_ev: 13.605_693_122_843_6,
        }
    }
}
impl Default for HeConstants {
    fn default() -> Self {
        Self::canonical()
    }
}

pub fn planck_occupation(energy_ev: f64, t: f64) -> f64 {
    if energy_ev <= 0.0 || t <= 0.0 {
        return f64::NAN;
    }
    let x = energy_ev * EV_J / (KB_J_K * t);
    1.0 / x.exp_m1()
}

fn phi_m3(t: f64) -> f64 {
    (ME_KG * KB_J_K * t / (2.0 * PI * HBAR_J_S * HBAR_J_S)).powf(1.5)
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ElectronFramePolicy {
    CommonMaterialMaxwell,
    SpeciesDriftUnsupported,
}

#[derive(Clone, Copy, Debug)]
pub struct SourceState {
    pub ng: f64,
    pub ns: f64,
    pub wp: Mat3,
    pub n_he_plus: f64,
    pub ne: f64,
    pub temperature_k: f64,
    pub f: Mat2,
    pub v: RealV,
    pub constants: HeConstants,
    pub electron_frame: ElectronFramePolicy,
}
impl SourceState {
    pub fn simple(
        ng: f64,
        ns: f64,
        wp: Mat3,
        n_he_plus: f64,
        ne: f64,
        temperature_k: f64,
    ) -> Result<Self, CoverageError> {
        if [ng, ns, n_he_plus, ne, temperature_k]
            .iter()
            .any(|x| !x.is_finite())
            || temperature_k <= 0.0
            || ng < 0.0
            || ns < 0.0
            || n_he_plus < 0.0
            || ne < 0.0
        {
            return Err(CoverageError::InvalidInput(
                "state densities must be finite/nonnegative and T positive",
            ));
        }
        if !wp.is_hermitian(1e-12) {
            return Err(CoverageError::InvalidInput("W_P must be Hermitian"));
        }
        Ok(Self {
            ng,
            ns,
            wp,
            n_he_plus,
            ne,
            temperature_k,
            f: Mat2::zero(),
            v: [[1.0, 0.0], [0.0, 1.0], [0.0, 0.0]],
            constants: HeConstants::canonical(),
            electron_frame: ElectronFramePolicy::CommonMaterialMaxwell,
        })
    }
    pub fn lte_populations(
        temperature_k: f64,
        n_he_plus: f64,
        ne: f64,
    ) -> Result<Self, CoverageError> {
        let c = HeConstants::canonical();
        let phi = phi_m3(temperature_k);
        let ng = n_he_plus * ne * (c.i_he_ev * EV_J / (KB_J_K * temperature_k)).exp() / (4.0 * phi);
        let ns = ng * (-c.delta_s_ev * EV_J / (KB_J_K * temperature_k)).exp();
        let wp = Mat3::scalar(ng * (-c.delta_p_ev * EV_J / (KB_J_K * temperature_k)).exp());
        Self::simple(ng, ns, wp, n_he_plus, ne, temperature_k)
    }
    fn validate(&self) -> Result<(), CoverageError> {
        if [self.ng, self.ns, self.n_he_plus, self.ne]
            .iter()
            .any(|x| !x.is_finite() || *x < 0.0)
        {
            return Err(CoverageError::InvalidInput(
                "state densities must be finite and nonnegative",
            ));
        }
        if !self.wp.is_hermitian(1e-12) {
            return Err(CoverageError::InvalidInput("W_P must be Hermitian"));
        }
        if !self.f.is_hermitian(1e-12) {
            return Err(CoverageError::InvalidInput("F must be Hermitian"));
        }
        if self.temperature_k <= 0.0 || !self.temperature_k.is_finite() {
            return Err(CoverageError::InvalidInput("temperature must be positive"));
        }
        Ok(())
    }
    fn validate_bf(&self) -> Result<(), CoverageError> {
        self.validate()?;
        if self.electron_frame != ElectronFramePolicy::CommonMaterialMaxwell {
            return Err(CoverageError::MissingAuthority {
                family: "BOUND_FREE_SPECIES_DRIFT",
                value: 0.0,
                detail: "inverse kernel is authorized only for common material/electron frame with isotropic nondegenerate Maxwell electrons",
            });
        }
        Ok(())
    }
}

#[derive(Clone, Copy, Debug)]
pub enum BoundBoundChannel {
    He584,
    IrPToS,
}
impl BoundBoundChannel {
    pub const fn a_s_inv(self) -> f64 {
        match self {
            Self::He584 => 1.7989e9,
            Self::IrPToS => 1.9746e6,
        }
    }
    pub fn energy_ev(self) -> f64 {
        let c = HeConstants::canonical();
        match self {
            Self::He584 => c.delta_p_ev,
            Self::IrPToS => c.epsilon_ir_ev,
        }
    }
}

#[derive(Clone, Copy, Debug)]
pub struct SharpLineConvention {
    pub energy_ev: f64,
    pub shell_integrated: bool,
}
#[derive(Clone, Debug)]
pub struct BoundBoundOutput {
    pub atomic_b: Mat3,
    pub angular_j: Vec<Mat2>,
    pub event_rate: f64,
    pub spectral: SharpLineConvention,
}

/// Shell-integrated sharp-line source. The Dirac-delta convention is represented
/// explicitly by `spectral`; no finite-bin line profile is invented here.
pub fn he_bb_source(
    channel: BoundBoundChannel,
    n_lower: f64,
    wp: Mat3,
    f: Mat2,
    angular: &[AngularSample],
) -> Result<BoundBoundOutput, CoverageError> {
    if n_lower < 0.0 || !n_lower.is_finite() {
        return Err(CoverageError::InvalidInput("lower population"));
    }
    if !wp.is_hermitian(1e-12) || !f.is_hermitian(1e-12) {
        return Err(CoverageError::InvalidInput("BB W_P/F must be Hermitian"));
    }
    if angular.is_empty() {
        return Err(CoverageError::InvalidInput("angular stencil empty"));
    }
    let a = channel.a_s_inv();
    let b = 3.0 * a / (8.0 * PI);
    let h = Mat2::identity() + f;
    let mut atomic = Mat3::zero();
    let mut js = Vec::with_capacity(angular.len());
    let mut rate = 0.0;
    for s in angular {
        if s.weight_sr < 0.0 || !s.weight_sr.is_finite() {
            return Err(CoverageError::InvalidInput("angular weight"));
        }
        let vfv = v_x_vt(s.v, f);
        let vhv = v_x_vt(s.v, h);
        let bi = vfv.scale(n_lower) - anticommutator3(vhv, wp).scale(0.5);
        atomic = atomic + bi.scale(b * s.weight_sr);
        let vtwpv = vt_x_v(s.v, wp);
        let ji = anticommutator2(h, vtwpv).scale(0.5) - f.scale(n_lower);
        let ji = ji.scale(b);
        rate += s.weight_sr * ji.trace().re;
        js.push(ji);
    }
    Ok(BoundBoundOutput {
        atomic_b: atomic,
        angular_j: js,
        event_rate: rate,
        spectral: SharpLineConvention {
            energy_ev: channel.energy_ev(),
            shell_integrated: true,
        },
    })
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum DipoleGauge {
    Length,
    Velocity,
}
#[derive(Clone, Copy, Debug)]
pub struct PPartialXs {
    pub sigma_s_mb: f64,
    pub sigma_d_mb: f64,
}
#[derive(Clone, Copy, Debug)]
pub struct PBoundFreeTable {
    gauge: DipoleGauge,
}
impl PBoundFreeTable {
    pub const fn jacobs_high_length() -> Self {
        Self {
            gauge: DipoleGauge::Length,
        }
    }
    pub const fn jacobs_high_velocity() -> Self {
        Self {
            gauge: DipoleGauge::Velocity,
        }
    }
    pub fn lookup(self, q: f64) -> Result<PPartialXs, CoverageError> {
        if !q.is_finite() {
            return Err(CoverageError::InvalidInput("q"));
        }
        if !(1.0..=1.4).contains(&q) {
            return Err(CoverageError::MissingAuthority {
                family: "P_BOUND_FREE_JACOBS_HIGH",
                value: q,
                detail: "selected source subset contains exact numerical rows only for q=1.0,1.2,1.4; do not invent low/high extrapolation",
            });
        }
        let (fs, fd) = match self.gauge {
            DipoleGauge::Length => (
                [0.002114, 0.001486, 0.001134],
                [0.003201, 0.001247, 0.0003970],
            ),
            DipoleGauge::Velocity => (
                [0.001935, 0.001380, 0.001075],
                [0.002810, 0.001010, 0.0002663],
            ),
        };
        let interp = |v: [f64; 3]| -> f64 {
            if q <= 1.2 {
                v[0] + (v[1] - v[0]) * (q - 1.0) / 0.2
            } else {
                v[1] + (v[2] - v[1]) * (q - 1.2) / 0.2
            }
        };
        Ok(PPartialXs {
            sigma_s_mb: JACOBS_F_TO_MB * interp(fs),
            sigma_d_mb: JACOBS_F_TO_MB * interp(fd),
        })
    }
}
#[derive(Clone, Copy, Debug)]
pub struct SBoundFreeTable {
    gauge: DipoleGauge,
}
impl SBoundFreeTable {
    pub const fn jacobs_high_length() -> Self {
        Self {
            gauge: DipoleGauge::Length,
        }
    }
    pub const fn jacobs_high_velocity() -> Self {
        Self {
            gauge: DipoleGauge::Velocity,
        }
    }
    pub fn lookup(self, q: f64) -> Result<f64, CoverageError> {
        if !q.is_finite() {
            return Err(CoverageError::InvalidInput("q"));
        }
        if !(1.0..=1.4).contains(&q) {
            return Err(CoverageError::MissingAuthority {
                family: "S_BOUND_FREE_JACOBS_HIGH",
                value: q,
                detail: "Bhatia low branch and Jacobs high branch are not stitched; selected subset provides high numerical rows only",
            });
        }
        let f = match self.gauge {
            DipoleGauge::Length => [0.06737, 0.04812, 0.03526],
            DipoleGauge::Velocity => [0.06635, 0.04696, 0.03398],
        };
        let v = if q <= 1.2 {
            f[0] + (f[1] - f[0]) * (q - 1.0) / 0.2
        } else {
            f[1] + (f[2] - f[1]) * (q - 1.2) / 0.2
        };
        Ok(JACOBS_F_TO_MB * v)
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum CoverageState {
    Represented,
    PhysicalZeroBelowThreshold,
}
#[derive(Clone, Copy, Debug)]
pub struct PBoundFreeOutput {
    pub photon_c: Mat2,
    pub atomic_b: Mat3,
    pub event_rate_density: f64,
    pub gross_scale: f64,
    pub atomic_gross_scale: f64,
    pub coverage: CoverageState,
}
#[derive(Clone, Copy, Debug)]
pub struct SBoundFreeOutput {
    pub photon_c: Mat2,
    pub event_rate_density: f64,
    pub gross_scale: f64,
    pub coverage: CoverageState,
}

fn te_map(x: Mat3, sigma_s: f64, sigma_d: f64) -> Mat3 {
    x.scale(3.0 * sigma_s - 3.0 * sigma_d / 5.0)
        + x.transpose().scale(9.0 * sigma_d / 10.0)
        + Mat3::identity().scale(9.0 * sigma_d / 10.0 * x.trace().re)
}
fn eta(state: &SourceState, energy_ev: f64, chi_ev: f64) -> f64 {
    state.n_he_plus
        * state.ne
        * (-(energy_ev - chi_ev) * EV_J / (KB_J_K * state.temperature_k)).exp()
        / (4.0 * phi_m3(state.temperature_k))
}

pub fn he_p_bf_source(
    energy_ev: f64,
    state: &SourceState,
    table: PBoundFreeTable,
) -> Result<PBoundFreeOutput, CoverageError> {
    state.validate_bf()?;
    if energy_ev < state.constants.chi_p_ev {
        return Ok(PBoundFreeOutput {
            photon_c: Mat2::zero(),
            atomic_b: Mat3::zero(),
            event_rate_density: 0.0,
            gross_scale: 0.0,
            atomic_gross_scale: 0.0,
            coverage: CoverageState::PhysicalZeroBelowThreshold,
        });
    }
    let q = (energy_ev - state.constants.chi_p_ev) / state.constants.rydberg_ev;
    let xs = table.lookup(q)?;
    let ss = xs.sigma_s_mb * MB_TO_M2;
    let sd = xs.sigma_d_mb * MB_TO_M2;
    let st = ss + sd;
    let et = eta(state, energy_ev, state.constants.chi_p_ev);
    let h = Mat2::identity() + state.f;
    let kw = vt_x_v(state.v, te_map(state.wp.transpose(), ss, sd));
    let gain = h.scale(3.0 * et * st);
    let loss = anticommutator2(state.f, kw).scale(0.5);
    let cph = (gain - loss).scale(C_M_S);
    let e_j = energy_ev * EV_J;
    let ag = 1.0 / (H_J_S * C_M_S).powi(3);
    let j_f = v_x_vt(state.v, state.f.transpose());
    let j_h = v_x_vt(state.v, h.transpose());
    let kf = te_map(j_f, ss, sd);
    let atom_gain = te_map(j_h, ss, sd).scale(et);
    let atom_loss = anticommutator3(kf, state.wp).scale(0.5);
    let ab = (atom_gain - atom_loss).scale(C_M_S * ag * e_j * e_j);
    let event = -ag * e_j * e_j * cph.trace().re;
    Ok(PBoundFreeOutput {
        photon_c: cph,
        atomic_b: ab,
        event_rate_density: event,
        gross_scale: C_M_S * (gain.max_abs() + loss.max_abs()),
        atomic_gross_scale: C_M_S * ag * e_j * e_j * (atom_gain.max_abs() + atom_loss.max_abs()),
        coverage: CoverageState::Represented,
    })
}

pub fn he_s_bf_source(
    energy_ev: f64,
    state: &SourceState,
    table: SBoundFreeTable,
) -> Result<SBoundFreeOutput, CoverageError> {
    state.validate_bf()?;
    if energy_ev < state.constants.chi_s_ev {
        return Ok(SBoundFreeOutput {
            photon_c: Mat2::zero(),
            event_rate_density: 0.0,
            gross_scale: 0.0,
            coverage: CoverageState::PhysicalZeroBelowThreshold,
        });
    }
    let q = (energy_ev - state.constants.chi_s_ev) / state.constants.rydberg_ev;
    let sigma = table.lookup(q)? * MB_TO_M2;
    let et = eta(state, energy_ev, state.constants.chi_s_ev);
    let h = Mat2::identity() + state.f;
    let gain = h.scale(et);
    let loss = state.f.scale(state.ns);
    let cph = (gain - loss).scale(C_M_S * sigma);
    let e_j = energy_ev * EV_J;
    let ag = 1.0 / (H_J_S * C_M_S).powi(3);
    let event = -ag * e_j * e_j * cph.trace().re;
    Ok(SBoundFreeOutput {
        photon_c: cph,
        event_rate_density: event,
        gross_scale: C_M_S * sigma * (gain.max_abs() + loss.max_abs()),
        coverage: CoverageState::Represented,
    })
}

#[derive(Clone, Copy, Debug)]
pub struct TwoPhotonPairOutput {
    /// Unweighted material-frame M12 kernel.
    pub pair_matrix: Mat2,
    pub event_rate_density: f64,
    pub photon_tags_per_event: u8,
    pub atom_pair_factor: f64,
    pub w_s_inv: f64,
    /// Weight for the unordered atomic event integrand: (1/2) w g_ang.
    pub atomic_event_weight_s_inv: f64,
    /// Weight for one tagged-photon marginal before E/angular measures: w g_ang.
    /// No extra unordered-pair 1/2 belongs here.
    pub photon_marginal_weight_s_inv: f64,
}

pub fn he_two_photon_pair_source(
    y: f64,
    state: &SourceState,
    f1: Mat2,
    f2: Mat2,
) -> Result<TwoPhotonPairOutput, CoverageError> {
    state.validate()?;
    if !f1.is_hermitian(1e-12) || !f2.is_hermitian(1e-12) {
        return Err(CoverageError::InvalidInput("pair F must be Hermitian"));
    }
    let w = d86_w(y)?;
    let h1 = Mat2::identity() + f1;
    let h2 = Mat2::identity() + f2;
    // Identity real screen adapter T12 for fixed-input parity. General transport may
    // supply a rotated screen before calling this source.
    let emit = anticommutator2(h1, h2.transpose()).scale(0.5 * state.ns);
    let absorb = anticommutator2(f1, f2.transpose()).scale(0.5 * state.ng);
    let m = emit - absorb;
    let g = 3.0 / (64.0 * PI * PI);
    let atomic_event_weight = 0.5 * w * g;
    let photon_marginal_weight = w * g;
    Ok(TwoPhotonPairOutput {
        pair_matrix: m,
        event_rate_density: atomic_event_weight * m.trace().re,
        photon_tags_per_event: 2,
        atom_pair_factor: 0.5,
        w_s_inv: w,
        atomic_event_weight_s_inv: atomic_event_weight,
        photon_marginal_weight_s_inv: photon_marginal_weight,
    })
}
