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
        if !self.re.is_finite() || !self.im.is_finite()
            || !rhs.re.is_finite() || !rhs.im.is_finite() || !tol.is_finite() || tol < 0.0 {
            return false;
        }
        let scale = 1.0_f64.max(self.re.abs()).max(self.im.abs()).max(rhs.re.abs()).max(rhs.im.abs());
        let left = Complex64::new(self.re / scale, self.im / scale);
        let right = Complex64::new(rhs.re / scale, rhs.im / scale);
        (left - right).abs() <= tol * (1.0 / scale + left.abs() + right.abs())
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
        match scaled_input(self.0) {
            Ok(m) => hermitian_within(m, tol),
            Err(_) => false,
        }
    }

    /// Finite, Hermitian and principal-minor domain guard for input occupation.
    /// This is not an outward-rounded PSD proof. Input bytes are never changed.
    pub fn validate_occupation(self) -> Result<(), CoverageError> {
        let m = scaled_input(self.0)?;
        if !hermitian_within(m, HERMITIAN_REL_TOLERANCE) {
            return Err(CoverageError::InvalidInput("matrix must be Hermitian"));
        }
        validate_minors(&[
            m[0][0], m[1][1],
            m[0][0] * m[1][1] - m[0][1] * m[1][0],
        ])
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
        match scaled_input(self.0) {
            Ok(m) => hermitian_within(m, tol),
            Err(_) => false,
        }
    }

    /// Finite, Hermitian and principal-minor domain guard for input population.
    /// This is not an outward-rounded PSD proof. Input bytes are never changed.
    pub fn validate_population(self) -> Result<(), CoverageError> {
        let m = scaled_input(self.0)?;
        if !hermitian_within(m, HERMITIAN_REL_TOLERANCE) {
            return Err(CoverageError::InvalidInput("matrix must be Hermitian"));
        }
        let determinant = m[0][0] * m[1][1] * m[2][2]
            + m[0][1] * m[1][2] * m[2][0]
            + m[0][2] * m[1][0] * m[2][1]
            - m[0][2] * m[1][1] * m[2][0]
            - m[0][1] * m[1][0] * m[2][2]
            - m[0][0] * m[1][2] * m[2][1];
        validate_minors(&[
            m[0][0], m[1][1], m[2][2],
            m[0][0] * m[1][1] - m[0][1] * m[1][0],
            m[0][0] * m[2][2] - m[0][2] * m[2][0],
            m[1][1] * m[2][2] - m[1][2] * m[2][1],
            determinant,
        ])
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

// Implementation-only domain thresholds from the approved Task 2 contract.
pub const HERMITIAN_REL_TOLERANCE: f64 = 1.0e-12;
pub const SCREEN_TOLERANCE: f64 = 1.0e-12;
pub const PSD_MINOR_TOLERANCE: f64 = 4096.0 * f64::EPSILON;

fn validate_nonnegative(value: f64, field: &'static str) -> Result<(), CoverageError> {
    if !value.is_finite() || value < 0.0 {
        return Err(CoverageError::InvalidInput(field));
    }
    Ok(())
}

fn validate_positive(value: f64, field: &'static str) -> Result<(), CoverageError> {
    if !value.is_finite() || value <= 0.0 {
        return Err(CoverageError::InvalidInput(field));
    }
    Ok(())
}

fn validate_energy_cycle(lhs: f64, a: f64, b: f64) -> Result<(), CoverageError> {
    // Callers validate positive finite operands first. Scale before adding so
    // an inconsistent large tuple cannot pass by overflowing the reference sum.
    let scale = lhs.max(a).max(b);
    if (lhs / scale - a / scale - b / scale).abs() > PSD_MINOR_TOLERANCE {
        return Err(CoverageError::InvalidInput("inconsistent He energy cycle"));
    }
    Ok(())
}

fn scaled_input<const N: usize>(
    input: [[Complex64; N]; N],
) -> Result<[[Complex64; N]; N], CoverageError> {
    let mut scale = 0.0_f64;
    for row in &input {
        for z in row {
            if !z.re.is_finite() || !z.im.is_finite() {
                return Err(CoverageError::InvalidInput("nonfinite matrix entry"));
            }
            // Do not take an overflowing complex norm and do not add a unit floor.
            scale = scale.max(z.re.abs()).max(z.im.abs());
        }
    }
    if scale == 0.0 {
        return Ok(input);
    }
    let mut result = input;
    for row in &mut result {
        for z in row {
            let old = *z;
            z.re /= scale;
            z.im /= scale;
            if (old.re != 0.0 && z.re == 0.0) || (old.im != 0.0 && z.im == 0.0) {
                return Err(CoverageError::NumericalDomainUncertain {
                    quantity: "matrix scaling",
                    value: scale,
                    detail: "nonzero component underflowed during normalization",
                });
            }
        }
    }
    Ok(result)
}

fn hermitian_within<const N: usize>(m: [[Complex64; N]; N], tol: f64) -> bool {
    if !tol.is_finite() || tol < 0.0 {
        return false;
    }
    for (i, row) in m.iter().enumerate() {
        for (j, z) in row.iter().enumerate() {
            if (*z - m[j][i].conj()).abs() > tol {
                return false;
            }
        }
    }
    true
}

fn validate_minors(minors: &[Complex64]) -> Result<(), CoverageError> {
    // Inspect every minor before returning an uncertain boundary verdict:
    // one clearly negative minor must dominate a different tiny negative minor.
    for minor in minors {
        if !minor.re.is_finite() || !minor.im.is_finite() {
            return Err(CoverageError::NumericalDomainUncertain {
                quantity: "principal minor",
                value: minor.re,
                detail: "nonfinite scaled determinant arithmetic",
            });
        }
        if minor.re < -PSD_MINOR_TOLERANCE {
            return Err(CoverageError::InvalidInput("negative principal minor"));
        }
    }
    for minor in minors {
        if minor.im.abs() > PSD_MINOR_TOLERANCE || minor.re < 0.0 {
            return Err(CoverageError::NumericalDomainUncertain {
                quantity: "principal minor",
                value: minor.re,
                detail: "negative roundoff-boundary minor or non-real determinant; no projection applied",
            });
        }
    }
    Ok(())
}

/// Check a finite real 3x2 physical screen. An optional propagation direction
/// additionally binds the screen plane. No normal/material boost is performed.
pub fn validate_screen(v: RealV, direction: Option<[f64; 3]>) -> Result<(), CoverageError> {
    for row in &v {
        for value in row {
            if !value.is_finite() || value.abs() > 1.0 + SCREEN_TOLERANCE {
                return Err(CoverageError::InvalidInput("invalid screen entry"));
            }
        }
    }
    for i in 0..2 {
        for j in 0..2 {
            let dot: f64 = v.iter().map(|row| row[i] * row[j]).sum();
            let target = if i == j { 1.0 } else { 0.0 };
            if (dot - target).abs() > SCREEN_TOLERANCE {
                return Err(CoverageError::InvalidInput("screen columns must be orthonormal"));
            }
        }
    }
    if let Some(e) = direction {
        if e.iter().any(|x| !x.is_finite() || x.abs() > 1.0 + SCREEN_TOLERANCE) {
            return Err(CoverageError::InvalidInput("invalid photon direction"));
        }
        let norm2: f64 = e.iter().map(|x| x * x).sum();
        if (norm2 - 1.0).abs() > SCREEN_TOLERANCE {
            return Err(CoverageError::InvalidInput("photon direction must be unit length"));
        }
        for i in 0..2 {
            let dot: f64 = v.iter().zip(e).map(|(row, ek)| row[i] * ek).sum();
            if dot.abs() > SCREEN_TOLERANCE {
                return Err(CoverageError::InvalidInput("screen is not transverse to direction"));
            }
        }
    }
    Ok(())
}

/// The measure for number/atomic spectral densities, not for occupation/s.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum SpectralMeasure {
    SharpLineDeltaPerJoule { energy_ev: f64 },
    ContinuousPerJoulePerSteradian,
    PairDyDOmega1DOmega2,
}

/// Convert a positive material photon energy in eV to joules once.
pub fn material_energy_j(energy_ev: f64) -> Result<f64, CoverageError> {
    validate_positive(energy_ev, "material photon energy must be positive finite eV")?;
    let energy_j = energy_ev * EV_J;
    if energy_j == 0.0 || !energy_j.is_finite() {
        return Err(CoverageError::NumericalDomainUncertain {
            quantity: "material energy in joules",
            value: energy_j,
            detail: "positive eV input is not representable in the joule adapter",
        });
    }
    Ok(energy_j)
}

/// Caller-side dE_eV -> dE_J conversion. A zero quadrature weight is permitted.
/// Source kernels never call this adapter or multiply a caller's rate by it.
pub fn energy_width_j(width_ev: f64) -> Result<f64, CoverageError> {
    validate_nonnegative(width_ev, "energy width must be finite nonnegative eV")?;
    if width_ev == 0.0 {
        return Ok(0.0);
    }
    material_energy_j(width_ev)
}

fn jacobs_q_from_material_energy(
    energy_ev: f64,
    chi_ev: f64,
    rydberg_ev: f64,
    family: &'static str,
) -> Result<f64, CoverageError> {
    let lo = chi_ev + rydberg_ev;
    let hi = chi_ev + 1.4 * rydberg_ev;
    let raw_q = (energy_ev - chi_ev) / rydberg_ev;
    if !lo.is_finite() || !hi.is_finite() || lo >= hi {
        return Err(CoverageError::NumericalDomainUncertain {
            quantity: "Jacobs material energy band",
            value: energy_ev,
            detail: "band endpoints cannot be represented distinctly",
        });
    }
    if energy_ev < lo || energy_ev > hi {
        return Err(CoverageError::MissingAuthority {
            family,
            value: raw_q,
            detail: "outside represented material-energy band; no low/high splice or extrapolation",
        });
    }
    // Exact encoded node equality only, after strict physical-band membership.
    // An input one ulp outside [lo,hi] is NOT admitted by this roundtrip adapter.
    for node in [1.0, 1.2, 1.4] {
        if energy_ev == chi_ev + node * rydberg_ev {
            return Ok(node);
        }
    }
    if !(1.0..=1.4).contains(&raw_q) {
        return Err(CoverageError::NumericalDomainUncertain {
            quantity: "Jacobs energy-to-q conversion",
            value: raw_q,
            detail: "in-band energy mapped outside q band; no clamp applied",
        });
    }
    Ok(raw_q)
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
    pub fn validate(self) -> Result<(), CoverageError> {
        for value in [self.delta_s_ev, self.delta_p_ev, self.i_he_ev,
                      self.epsilon_ir_ev, self.chi_p_ev, self.chi_s_ev, self.rydberg_ev] {
            validate_positive(value, "He energies must be finite positive eV")?;
        }
        validate_energy_cycle(self.delta_p_ev, self.delta_s_ev, self.epsilon_ir_ev)?;
        validate_energy_cycle(self.i_he_ev, self.delta_p_ev, self.chi_p_ev)?;
        validate_energy_cycle(self.i_he_ev, self.delta_s_ev, self.chi_s_ev)
    }

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
    if !energy_ev.is_finite() || !t.is_finite() || energy_ev <= 0.0 || t <= 0.0 {
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
        let state = Self {
            ng, ns, wp, n_he_plus, ne, temperature_k,
            f: Mat2::zero(),
            v: [[1.0, 0.0], [0.0, 1.0], [0.0, 0.0]],
            constants: HeConstants::canonical(),
            electron_frame: ElectronFramePolicy::CommonMaterialMaxwell,
        };
        state.validate()?;
        Ok(state)
    }
    pub fn lte_populations(
        temperature_k: f64,
        n_he_plus: f64,
        ne: f64,
    ) -> Result<Self, CoverageError> {
        validate_positive(temperature_k, "temperature must be positive finite K")?;
        validate_nonnegative(n_he_plus, "n_HePlus must be finite and nonnegative")?;
        validate_nonnegative(ne, "n_e must be finite and nonnegative")?;
        let c = HeConstants::canonical();
        let phi = phi_m3(temperature_k);
        let ng = n_he_plus * ne * (c.i_he_ev * EV_J / (KB_J_K * temperature_k)).exp() / (4.0 * phi);
        let ns = ng * (-c.delta_s_ev * EV_J / (KB_J_K * temperature_k)).exp();
        let wp = Mat3::scalar(ng * (-c.delta_p_ev * EV_J / (KB_J_K * temperature_k)).exp());
        Self::simple(ng, ns, wp, n_he_plus, ne, temperature_k)
    }
    /// Recheck mutable public fields at every source entry. These are proper
    /// material densities and occupations, not signed collision-source matrices.
    pub fn validate(&self) -> Result<(), CoverageError> {
        for value in [self.ng, self.ns, self.n_he_plus, self.ne] {
            validate_nonnegative(value, "state densities must be finite and nonnegative")?;
        }
        validate_positive(self.temperature_k, "temperature must be positive finite K")?;
        self.constants.validate()?;
        self.wp.validate_population()?;
        self.f.validate_occupation()?;
        validate_screen(self.v, None)
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

/// One material-frame mode. `f` is evaluated at this channel's line energy
/// in this mode's real screen `v`; `weight_sr` approximates dOmega once.
#[derive(Clone, Copy, Debug)]
pub struct WeightedBbMode {
    pub v: RealV,
    pub f: Mat2,
    pub weight_sr: f64,
}

/// Geometry-only moment diagnostics, NOT an angular convergence certificate.
/// Passing these two moments permits the full-stencil vacuum B = -A W check.
/// Partial stencils remain valid sources and are never renormalized to 4*pi.
#[derive(Clone, Copy, Debug)]
pub struct BbStencilDiagnostics {
    pub weight_sum_sr: f64,
    pub projector_sum_sr: [[f64; 3]; 3],
    pub weight_relative_residual: f64,
    pub projector_relative_residual: f64,
    pub full_sphere_moments_match: bool,
}

pub const BB_STENCIL_MOMENT_TOLERANCE: f64 = 4096.0 * f64::EPSILON;

fn check_bb_finite(value: f64, quantity: &'static str) -> Result<(), CoverageError> {
    if !value.is_finite() {
        return Err(CoverageError::NumericalDomainUncertain {
            quantity,
            value,
            detail: "nonfinite BB arithmetic; no output clipping or renormalization",
        });
    }
    Ok(())
}

fn check_bb_matrix<const N: usize>(
    matrix: [[Complex64; N]; N],
    quantity: &'static str,
) -> Result<(), CoverageError> {
    // Sources are signed. Only numerical finiteness, not PSD, is required here.
    for row in matrix {
        for entry in row {
            check_bb_finite(entry.re, quantity)?;
            check_bb_finite(entry.im, quantity)?;
        }
    }
    Ok(())
}

/// Inspect sum(w) and sum(w V V^T). Only screens and weights enter this audit;
/// source evaluation separately validates all occupations, even at zero weight.
pub fn audit_bb_stencil(
    modes: &[WeightedBbMode],
) -> Result<BbStencilDiagnostics, CoverageError> {
    if modes.is_empty() {
        return Err(CoverageError::InvalidInput("angular stencil empty"));
    }
    let mut weight_sum_sr = 0.0;
    let mut projector_sum_sr = [[0.0; 3]; 3];
    for mode in modes {
        validate_nonnegative(mode.weight_sr, "angular weight must be finite nonnegative sr")?;
        validate_screen(mode.v, None)?;
        weight_sum_sr += mode.weight_sr;
        for (a, row) in projector_sum_sr.iter_mut().enumerate() {
            for (b, entry) in row.iter_mut().enumerate() {
                let projector = mode.v[a][0] * mode.v[b][0] + mode.v[a][1] * mode.v[b][1];
                *entry += mode.weight_sr * projector;
                check_bb_finite(*entry, "angular projector moment")?;
            }
        }
        check_bb_finite(weight_sum_sr, "angular weight sum")?;
    }
    let full_weight = 4.0 * PI;
    let full_projector = 8.0 * PI / 3.0;
    let weight_relative_residual = (weight_sum_sr - full_weight).abs() / full_weight;
    let mut projector_relative_residual = 0.0_f64;
    for (a, row) in projector_sum_sr.iter().enumerate() {
        for (b, entry) in row.iter().enumerate() {
            let target = if a == b { full_projector } else { 0.0 };
            projector_relative_residual = projector_relative_residual
                .max((*entry - target).abs() / full_projector);
        }
    }
    Ok(BbStencilDiagnostics {
        weight_sum_sr,
        projector_sum_sr,
        weight_relative_residual,
        projector_relative_residual,
        full_sphere_moments_match: weight_relative_residual <= BB_STENCIL_MOMENT_TOLERANCE
            && projector_relative_residual <= BB_STENCIL_MOMENT_TOLERANCE,
    })
}

/// Coefficients for ONE direction, with the energy delta integrated out and
/// NO angular weight applied. The only supported line profile is the declared
/// distribution: C_E(E,e) = occupation_c_shell * delta_J(E-epsilon_J).
#[derive(Clone, Copy, Debug)]
pub struct BoundBoundKernelOutput {
    /// Atomic proper-density source per solid angle: m^-3 s^-1 sr^-1.
    pub atomic_b_shell: Mat3,
    /// Photon-number source per solid angle: m^-3 s^-1 sr^-1, in this screen.
    pub photon_j_shell: Mat2,
    /// Coefficient of delta_J in the ray-clock occupation source: J s^-1.
    /// This is not a pointwise occupation/s value or a finite-bin profile.
    pub occupation_c_shell: Mat2,
    /// Signed photon event rate per solid angle, computed from tr(J_shell).
    pub event_rate_per_sr: f64,
    pub spectral: SpectralMeasure,
}

/// WU29 (8)-(9), generalized only by choosing lower=ng for 584 or lower=nS
/// for IR. Both channels use the SAME caller-owned upper matrix W_P.
/// Do not insert the bound-free transpose convention in this BB contraction.
pub fn he_bb_kernel(
    channel: BoundBoundChannel,
    n_lower: f64,
    wp: Mat3,
    f: Mat2,
    v: RealV,
) -> Result<BoundBoundKernelOutput, CoverageError> {
    validate_nonnegative(n_lower, "lower population must be finite nonnegative")?;
    wp.validate_population()?;
    f.validate_occupation()?;
    validate_screen(v, None)?;
    let energy_ev = channel.energy_ev();
    let epsilon_j = material_energy_j(energy_ev)?;
    let b_shell = 3.0 * channel.a_s_inv() / (8.0 * PI);
    let h = Mat2::identity() + f;
    let vfv = v_x_vt(v, f);
    let vhv = v_x_vt(v, h);
    let vtwpv = vt_x_v(v, wp);
    let atomic_b_shell = (vfv.scale(n_lower) - anticommutator3(vhv, wp).scale(0.5))
        .scale(b_shell);
    let photon_j_shell = (anticommutator2(h, vtwpv).scale(0.5) - f.scale(n_lower))
        .scale(b_shell);
    let a_gamma_epsilon_sq = epsilon_j * epsilon_j / (H_J_S * C_M_S).powi(3);
    let occupation_c_shell = photon_j_shell.scale(1.0 / a_gamma_epsilon_sq);
    let event_rate_per_sr = photon_j_shell.trace().re;
    check_bb_matrix(atomic_b_shell.0, "BB atomic shell source")?;
    check_bb_matrix(photon_j_shell.0, "BB photon-number shell source")?;
    check_bb_matrix(occupation_c_shell.0, "BB occupation delta coefficient")?;
    check_bb_finite(event_rate_per_sr, "BB event trace")?;
    Ok(BoundBoundKernelOutput {
        atomic_b_shell,
        photon_j_shell,
        occupation_c_shell,
        event_rate_per_sr,
        spectral: SpectralMeasure::SharpLineDeltaPerJoule { energy_ev },
    })
}

#[derive(Clone, Debug)]
pub struct BoundBoundOutput {
    /// Integral B_shell dOmega in the common atomic Cartesian basis: m^-3 s^-1.
    pub atomic_b: Mat3,
    /// Unweighted J_shell for each supplied mode, in that mode's screen.
    /// Matrices from different screens are NOT summed into one 2x2 matrix.
    pub angular_j: Vec<Mat2>,
    /// Unweighted C_shell coefficients, to be multiplied by delta_J downstream.
    pub angular_c: Vec<Mat2>,
    /// Integral tr(J_shell) dOmega: signed events m^-3 s^-1.
    pub event_rate: f64,
    pub spectral: SpectralMeasure,
    pub stencil: BbStencilDiagnostics,
}

/// Assemble the fixed angular stencil exactly once. This API has no energy
/// width, delta value, rate rescale or hidden broadcast of the first F.
/// A non-full stencil is admissible; its missing solid angle is not fabricated.
pub fn he_bb_source(
    channel: BoundBoundChannel,
    n_lower: f64,
    wp: Mat3,
    modes: &[WeightedBbMode],
) -> Result<BoundBoundOutput, CoverageError> {
    validate_nonnegative(n_lower, "lower population must be finite nonnegative")?;
    wp.validate_population()?;
    let stencil = audit_bb_stencil(modes)?;
    let mut atomic_b = Mat3::zero();
    let mut angular_j = Vec::with_capacity(modes.len());
    let mut angular_c = Vec::with_capacity(modes.len());
    let mut event_rate = 0.0;
    for mode in modes {
        // Evaluate even a zero-weight node: invalid mutable fields must reject.
        let kernel = he_bb_kernel(channel, n_lower, wp, mode.f, mode.v)?;
        atomic_b = atomic_b + kernel.atomic_b_shell.scale(mode.weight_sr);
        event_rate += mode.weight_sr * kernel.event_rate_per_sr;
        check_bb_matrix(atomic_b.0, "BB angular atomic sum")?;
        check_bb_finite(event_rate, "BB angular event sum")?;
        angular_j.push(kernel.photon_j_shell);
        angular_c.push(kernel.occupation_c_shell);
    }
    Ok(BoundBoundOutput {
        atomic_b,
        angular_j,
        angular_c,
        event_rate,
        spectral: SpectralMeasure::SharpLineDeltaPerJoule { energy_ev: channel.energy_ev() },
        stencil,
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
    /// Occupation collision source in s^-1, NOT a density per energy.
    pub photon_c: Mat2,
    /// Proper population density source per dE_J dOmega [m^-3 s^-1 J^-1 sr^-1].
    pub atomic_b: Mat3,
    /// Signed net ionization density per dE_J dOmega [m^-3 s^-1 J^-1 sr^-1].
    pub event_rate_density: f64,
    /// Applies to atomic_b and event_rate_density, not photon_c.
    pub density_measure: SpectralMeasure,
    pub gross_scale: f64,
    pub atomic_gross_scale: f64,
    pub coverage: CoverageState,
}
#[derive(Clone, Copy, Debug)]
pub struct SBoundFreeOutput {
    /// Occupation collision source in s^-1, NOT a density per energy.
    pub photon_c: Mat2,
    /// Signed net ionization density per dE_J dOmega [m^-3 s^-1 J^-1 sr^-1].
    pub event_rate_density: f64,
    /// Independent scalar atomic bracket per dE_J dOmega [m^-3 s^-1 J^-1 sr^-1].
    pub atomic_s_density: f64,
    pub atomic_gross_scale: f64,
    pub density_measure: SpectralMeasure,
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

fn check_bf_scalar(value: f64, quantity: &'static str) -> Result<(), CoverageError> {
    if !value.is_finite() {
        return Err(CoverageError::NumericalDomainUncertain {
            quantity, value, detail: "nonfinite BF arithmetic; no source clipping or normalization",
        });
    }
    Ok(())
}

fn check_bf_matrix<const N: usize>(
    matrix: [[Complex64; N]; N], quantity: &'static str,
) -> Result<(), CoverageError> {
    // Signed collision outputs are not density matrices; no PSD projection.
    for row in matrix { for x in row {
        check_bf_scalar(x.re, quantity)?;
        check_bf_scalar(x.im, quantity)?;
    }}
    Ok(())
}

/// Fixed material-frame photon energy is supplied in eV. Differential atomic
/// and event outputs are integrated against joules and steradians, not eV.
pub fn he_p_bf_source(
    energy_ev: f64,
    state: &SourceState,
    table: PBoundFreeTable,
) -> Result<PBoundFreeOutput, CoverageError> {
    validate_positive(energy_ev, "material photon energy must be positive finite eV")?;
    state.validate_bf()?;
    if energy_ev < state.constants.chi_p_ev {
        return Ok(PBoundFreeOutput {
            photon_c: Mat2::zero(),
            atomic_b: Mat3::zero(),
            event_rate_density: 0.0,
            gross_scale: 0.0,
            atomic_gross_scale: 0.0,
            density_measure: SpectralMeasure::ContinuousPerJoulePerSteradian,
            coverage: CoverageState::PhysicalZeroBelowThreshold,
        });
    }
    let q = jacobs_q_from_material_energy(
        energy_ev, state.constants.chi_p_ev, state.constants.rydberg_ev,
        "P_BOUND_FREE_JACOBS_HIGH",
    )?;
    let xs = table.lookup(q)?;
    let ss = xs.sigma_s_mb * MB_TO_M2;
    let sd = xs.sigma_d_mb * MB_TO_M2;
    let st = ss + sd;
    let et = eta(state, energy_ev, state.constants.chi_p_ev);
    check_bf_scalar(et, "P Maxwell inverse coefficient")?;
    let h = Mat2::identity() + state.f;
    let kw = vt_x_v(state.v, te_map(state.wp.transpose(), ss, sd));
    let gain = h.scale(3.0 * et * st);
    let loss = anticommutator2(state.f, kw).scale(0.5);
    let cph = (gain - loss).scale(C_M_S);
    let e_j = material_energy_j(energy_ev)?;
    let ag = 1.0 / (H_J_S * C_M_S).powi(3);
    let j_f = v_x_vt(state.v, state.f.transpose());
    let j_h = v_x_vt(state.v, h.transpose());
    let kf = te_map(j_f, ss, sd);
    let atom_gain = te_map(j_h, ss, sd).scale(et);
    let atom_loss = anticommutator3(kf, state.wp).scale(0.5);
    let ab = (atom_gain - atom_loss).scale(C_M_S * ag * e_j * e_j);
    let event = -ag * e_j * e_j * cph.trace().re;
    check_bf_matrix(cph.0, "P photon occupation source")?;
    check_bf_matrix(ab.0, "P atomic density source")?;
    check_bf_scalar(event, "P signed event density")?;
    check_bf_scalar(C_M_S * (gain.max_abs() + loss.max_abs()), "P photon gross scale")?;
    check_bf_scalar(C_M_S * ag * e_j * e_j * (atom_gain.max_abs() + atom_loss.max_abs()), "P atom gross scale")?;
    Ok(PBoundFreeOutput {
        photon_c: cph,
        atomic_b: ab,
        event_rate_density: event,
        gross_scale: C_M_S * (gain.max_abs() + loss.max_abs()),
        atomic_gross_scale: C_M_S * ag * e_j * e_j * (atom_gain.max_abs() + atom_loss.max_abs()),
        density_measure: SpectralMeasure::ContinuousPerJoulePerSteradian,
        coverage: CoverageState::Represented,
    })
}

/// Fixed material-frame photon energy is supplied in eV. Differential atomic
/// and event outputs are integrated against joules and steradians, not eV.
pub fn he_s_bf_source(
    energy_ev: f64,
    state: &SourceState,
    table: SBoundFreeTable,
) -> Result<SBoundFreeOutput, CoverageError> {
    validate_positive(energy_ev, "material photon energy must be positive finite eV")?;
    state.validate_bf()?;
    if energy_ev < state.constants.chi_s_ev {
        return Ok(SBoundFreeOutput {
            photon_c: Mat2::zero(),
            event_rate_density: 0.0,
            atomic_s_density: 0.0,
            atomic_gross_scale: 0.0,
            gross_scale: 0.0,
            density_measure: SpectralMeasure::ContinuousPerJoulePerSteradian,
            coverage: CoverageState::PhysicalZeroBelowThreshold,
        });
    }
    let q = jacobs_q_from_material_energy(
        energy_ev, state.constants.chi_s_ev, state.constants.rydberg_ev,
        "S_BOUND_FREE_JACOBS_HIGH",
    )?;
    let sigma = table.lookup(q)? * MB_TO_M2;
    let et = eta(state, energy_ev, state.constants.chi_s_ev);
    check_bf_scalar(et, "S Maxwell inverse coefficient")?;
    let h = Mat2::identity() + state.f;
    let gain = h.scale(et);
    let loss = state.f.scale(state.ns);
    let cph = (gain - loss).scale(C_M_S * sigma);
    let e_j = material_energy_j(energy_ev)?;
    let ag = 1.0 / (H_J_S * C_M_S).powi(3);
    let event = -ag * e_j * e_j * cph.trace().re;
    // Evaluate the scalar atomic gain/loss independently of photon trace/event.
    // Same table handle and eta as forward/inverse photon source (WU30 (8)).
    let atom_gain = et * (2.0 + state.f.trace().re);
    let atom_loss = state.ns * state.f.trace().re;
    let atomic_s = C_M_S * sigma * ag * e_j * e_j * (atom_gain - atom_loss);
    let atom_gross = C_M_S * sigma * ag * e_j * e_j * (atom_gain.abs() + atom_loss.abs());
    check_bf_matrix(cph.0, "S photon occupation source")?;
    check_bf_scalar(event, "S signed event density")?;
    check_bf_scalar(atomic_s, "S atomic density source")?;
    check_bf_scalar(atom_gross, "S atom gross scale")?;
    check_bf_scalar(C_M_S * sigma * (gain.max_abs() + loss.max_abs()), "S photon gross scale")?;
    Ok(SBoundFreeOutput {
        photon_c: cph,
        event_rate_density: event,
        atomic_s_density: atomic_s,
        atomic_gross_scale: atom_gross,
        gross_scale: C_M_S * sigma * (gain.max_abs() + loss.max_abs()),
        density_measure: SpectralMeasure::ContinuousPerJoulePerSteradian,
        coverage: CoverageState::Represented,
    })
}

/// Fixed material-frame photon pair. The caller supplies occupations at
/// E1 = DeltaS*y and E2 = DeltaS*(1-y) in the two real Cartesian screens.
/// No photon-bath interpolation, normal-frame boost, or screen default is applied.
#[derive(Clone, Copy, Debug)]
pub struct PairInput {
    pub y: f64,
    pub f1: Mat2,
    pub f2: Mat2,
    pub v1: RealV,
    pub v2: RealV,
}

pub const PAIR_G_ANG: f64 = 3.0 / (64.0 * PI * PI);
pub const PAIR_GRID_Y_TOLERANCE: f64 = 4096.0 * f64::EPSILON;

/// Each C_i is an occupation-rate integrand in the other photon's solid angle
/// at FIXED E_i. It is not a density in dy and contains no atomic-event 1/2.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum PairMarginalMeasure {
    PartnerSolidAngleAtFixedMaterialEnergy,
}

#[derive(Clone, Copy, Debug)]
pub struct TwoPhotonPairOutput {
    pub screen_overlap: Mat2,
    /// M12, with no w, g_ang, or quadrature weights. Signed, not generally PSD.
    pub pair_matrix: Mat2,
    /// M21 evaluated independently in screen 2, not identified with M12.
    pub partner_pair_matrix: Mat2,
    /// Per-tag emission-plus-absorption scales, implementation diagnostics only.
    pub matrix_gross_scale: [f64; 2],
    pub delta_s_j: f64,
    pub energy1_j: f64,
    pub energy2_j: f64,
    /// (1/2) w g_ang tr(M12), density in dy dOmega1 dOmega2, NOT integrated R2g.
    pub event_rate_density: f64,
    pub density_measure: SpectralMeasure,
    /// C1 before integrating over dOmega2. Units: occupation / (s sr).
    pub tagged_c1_per_partner_sr: Mat2,
    /// C2 before integrating over dOmega1, evaluated from M21.
    pub tagged_c2_per_partner_sr: Mat2,
    pub marginal_measure: PairMarginalMeasure,
    /// Metadata only; this constant is not a number-conservation test.
    pub photon_tags_per_event: u8,
    pub atom_pair_factor: f64,
    pub w_s_inv: f64,
    pub atomic_event_weight_s_inv: f64,
    pub photon_marginal_weight_s_inv: f64,
}

fn check_pair_finite(value: f64, quantity: &'static str) -> Result<(), CoverageError> {
    if !value.is_finite() {
        return Err(CoverageError::NumericalDomainUncertain {
            quantity,
            value,
            detail: "nonfinite pair arithmetic; no clipping or source rescale",
        });
    }
    Ok(())
}

fn check_pair_matrix(matrix: Mat2, quantity: &'static str) -> Result<(), CoverageError> {
    // Do not enforce PSD on a signed collision source.
    for row in matrix.0 {
        for entry in row {
            check_pair_finite(entry.re, quantity)?;
            check_pair_finite(entry.im, quantity)?;
        }
    }
    Ok(())
}

fn pair_product(a: f64, b: f64, quantity: &'static str) -> Result<f64, CoverageError> {
    let product = a * b;
    check_pair_finite(product, quantity)?;
    if a != 0.0 && b != 0.0 && product == 0.0 {
        return Err(CoverageError::NumericalDomainUncertain {
            quantity,
            value: product,
            detail: "nonzero pair factor underflowed; it is not a physical zero",
        });
    }
    Ok(product)
}

fn pair_screen_overlap(v1: RealV, v2: RealV) -> Mat2 {
    let mut t = Mat2::zero();
    for (i, row) in t.0.iter_mut().enumerate() {
        for (j, entry) in row.iter_mut().enumerate() {
            *entry = Complex64::new((0..3).map(|a| v1[a][i] * v2[a][j]).sum(), 0.0);
        }
    }
    t
}

fn pair_matrix_for_tag(
    ng: f64,
    ns: f64,
    f1: Mat2,
    f2: Mat2,
    t12: Mat2,
) -> Result<(Mat2, f64), CoverageError> {
    let h1 = Mat2::identity() + f1;
    let h2 = Mat2::identity() + f2;
    // WU29 Eq.(16), T4 section 2.5: transpose is NOT a Hermitian conjugate.
    let xh = mat2_mul(mat2_mul(t12, h2.transpose()), t12.dagger());
    let xf = mat2_mul(mat2_mul(t12, f2.transpose()), t12.dagger());
    let emission = anticommutator2(h1, xh).scale(0.5 * ns);
    let absorption = anticommutator2(f1, xf).scale(0.5 * ng);
    check_pair_matrix(emission, "pair emission matrix")?;
    check_pair_matrix(absorption, "pair absorption matrix")?;
    let matrix = emission - absorption;
    check_pair_matrix(matrix, "pair signed matrix")?;
    let gross = emission.max_abs() + absorption.max_abs();
    check_pair_finite(gross, "pair matrix gross scale")?;
    Ok((matrix, gross))
}

fn pair_marginal_denominator(energy_j: f64, delta_j: f64) -> Result<f64, CoverageError> {
    let a_gamma = 1.0 / (H_J_S * C_M_S).powi(3);
    let e2 = pair_product(energy_j, energy_j, "pair energy squared")?;
    let mode_density = pair_product(a_gamma, e2, "pair photon mode measure")?;
    pair_product(mode_density, delta_j, "pair marginal energy Jacobian")
}

/// Unweighted pointwise pair source: no dy or dOmega quadrature weight enters.
/// D86 is evaluated at material y on the canonical band with no total-rate rescale.
/// M21 is recomputed with exchanged F and screens using the same ng/ns.
pub fn he_two_photon_pair_source(
    input: &PairInput,
    state: &SourceState,
) -> Result<TwoPhotonPairOutput, CoverageError> {
    state.validate()?;
    input.f1.validate_occupation()?;
    input.f2.validate_occupation()?;
    validate_screen(input.v1, None)?;
    validate_screen(input.v2, None)?;
    let w = d86_w(input.y)?;
    let delta_s_j = material_energy_j(state.constants.delta_s_ev)?;
    // Single owner of the material energy split and eV -> J conversion.
    let energy1_j = pair_product(delta_s_j, input.y, "pair material E1")?;
    let energy2_j = pair_product(delta_s_j, 1.0 - input.y, "pair material E2")?;
    let t12 = pair_screen_overlap(input.v1, input.v2);
    let (m12, gross1) = pair_matrix_for_tag(state.ng, state.ns, input.f1, input.f2, t12)?;
    let (m21, gross2) = pair_matrix_for_tag(state.ng, state.ns, input.f2, input.f1, t12.transpose())?;
    let marginal_weight = w * PAIR_G_ANG;
    let atomic_weight = 0.5 * marginal_weight;
    let c1 = m12.scale(marginal_weight / pair_marginal_denominator(energy1_j, delta_s_j)?);
    let c2 = m21.scale(marginal_weight / pair_marginal_denominator(energy2_j, delta_s_j)?);
    check_pair_matrix(c1, "pair tagged C1")?;
    check_pair_matrix(c2, "pair tagged C2")?;
    let event_rate_density = pair_product(atomic_weight, m12.trace().re, "pair atomic-event integrand")?;
    Ok(TwoPhotonPairOutput {
        screen_overlap: t12,
        pair_matrix: m12,
        partner_pair_matrix: m21,
        matrix_gross_scale: [gross1, gross2],
        delta_s_j,
        energy1_j,
        energy2_j,
        event_rate_density,
        density_measure: SpectralMeasure::PairDyDOmega1DOmega2,
        tagged_c1_per_partner_sr: c1,
        tagged_c2_per_partner_sr: c2,
        marginal_measure: PairMarginalMeasure::PartnerSolidAngleAtFixedMaterialEnergy,
        photon_tags_per_event: 2,
        atom_pair_factor: 0.5,
        w_s_inv: w,
        atomic_event_weight_s_inv: atomic_weight,
        photon_marginal_weight_s_inv: marginal_weight,
    })
}

/// Only the full ordered, exchange-closed convention is adopted here.
/// "Full ordered" does not certify full spectral/angular coverage or convergence.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum PairGridConvention {
    FullOrderedExchangeClosed,
    UnorderedHalfGridUnsupported,
}

#[derive(Clone, Copy, Debug)]
pub struct WeightedPairMode {
    pub input: PairInput,
    pub weight_dy: f64,
    pub weight_omega1_sr: f64,
    pub weight_omega2_sr: f64,
    /// Index of (1-y, F2, F1, V2, V1) with exchanged angular weights.
    /// Must form an involution; missing partners are not synthesized.
    pub exchange_partner: usize,
}

#[derive(Clone, Copy, Debug)]
pub struct PairAssemblyOutput {
    /// Integrated unordered atomic rate; ready for ChannelRates.r2g WITHOUT 1/2.
    pub event_rate: f64,
    /// Two independent FULL photon-number estimates. Each is 2*event_rate.
    /// Do NOT add them: the full ordered grid already contains both tags.
    pub photon_number_from_marginals: [f64; 2],
    /// Two independent FULL photon-power estimates in J m^-3 s^-1.
    pub photon_energy_from_marginals_j: [f64; 2],
    pub photon_number_residuals: [f64; 2],
    pub photon_energy_residuals_j: [f64; 2],
    pub delta_s_j: f64,
    pub node_count: usize,
    pub quadrature_weight_sum: f64,
    pub convention: PairGridConvention,
}

fn validate_pair_exchange(nodes: &[WeightedPairMode]) -> Result<(), CoverageError> {
    for (i, node) in nodes.iter().enumerate() {
        let partner = nodes.get(node.exchange_partner).ok_or(CoverageError::InvalidInput(
            "pair exchange index outside ordered grid",
        ))?;
        if partner.exchange_partner != i {
            return Err(CoverageError::InvalidInput("pair exchange map is not an involution"));
        }
        // Domain checks have already rejected outband/nonfinite y in the kernel.
        // This tolerance is an f64 symmetry check, never a coverage clamp.
        if (partner.input.y - (1.0 - node.input.y)).abs() > PAIR_GRID_Y_TOLERANCE
            || partner.input.f1 != node.input.f2
            || partner.input.f2 != node.input.f1
            || partner.input.v1 != node.input.v2
            || partner.input.v2 != node.input.v1
            || partner.weight_dy != node.weight_dy
            || partner.weight_omega1_sr != node.weight_omega2_sr
            || partner.weight_omega2_sr != node.weight_omega1_sr
        {
            return Err(CoverageError::InvalidInput("pair exchange inputs or weights do not match"));
        }
    }
    Ok(())
}

/// Assemble a supplied exchange-closed quadrature ON ITS REPRESENTED SUPPORT.
/// Kernel rates get dy*dOmega1*dOmega2 exactly once. Both photon moments are
/// independently integrated from the returned C1/C2 using dE=DeltaS*dy, not
/// manufactured as 2R or DeltaS*R. Residuals are diagnostics, not overwritten.
/// Matrices living in distinct screens are not summed into one 2x2 matrix.
pub fn assemble_he_pair_grid(
    state: &SourceState,
    nodes: &[WeightedPairMode],
    convention: PairGridConvention,
) -> Result<PairAssemblyOutput, CoverageError> {
    if convention != PairGridConvention::FullOrderedExchangeClosed {
        return Err(CoverageError::MissingAuthority {
            family: "TWO_PHOTON_UNORDERED_HALF_GRID",
            value: 0.0,
            detail: "no adopted half-grid contract; supply the full ordered exchange-closed grid",
        });
    }
    state.validate()?;
    if nodes.is_empty() {
        return Err(CoverageError::InvalidInput("pair grid is empty"));
    }
    let mut kernels = Vec::with_capacity(nodes.len());
    for node in nodes {
        validate_nonnegative(node.weight_dy, "pair dy weight must be finite nonnegative")?;
        validate_nonnegative(node.weight_omega1_sr, "pair Omega1 weight must be finite nonnegative")?;
        validate_nonnegative(node.weight_omega2_sr, "pair Omega2 weight must be finite nonnegative")?;
        // Validate every mode even at zero weight. No partial result escapes an error.
        kernels.push(he_two_photon_pair_source(&node.input, state)?);
    }
    validate_pair_exchange(nodes)?;
    let delta_s_j = kernels[0].delta_s_j;
    let a_gamma = 1.0 / (H_J_S * C_M_S).powi(3);
    let mut event_rate = 0.0;
    let mut number = [0.0; 2];
    let mut energy = [0.0; 2];
    let mut weight_sum = 0.0;
    for (node, kernel) in nodes.iter().zip(&kernels) {
        let solid_angle = pair_product(node.weight_omega1_sr, node.weight_omega2_sr, "pair angular weight")?;
        let measure = pair_product(node.weight_dy, solid_angle, "pair dy/angular weight")?;
        event_rate += pair_product(measure, kernel.event_rate_density, "integrated pair event")?;
        weight_sum += measure;
        // Independent photon marginal integration, not derived from the atomic rate.
        let de_j = pair_product(delta_s_j, node.weight_dy, "pair dE=DeltaS dy")?;
        let photon_measure = pair_product(de_j, solid_angle, "pair photon quadrature measure")?;
        let energies = [kernel.energy1_j, kernel.energy2_j];
        let marginals = [kernel.tagged_c1_per_partner_sr, kernel.tagged_c2_per_partner_sr];
        for tag in 0..2 {
            let e2 = pair_product(energies[tag], energies[tag], "pair moment energy squared")?;
            let state_density = pair_product(a_gamma, e2, "pair moment mode density")?;
            let n_density = pair_product(state_density, marginals[tag].trace().re, "pair marginal number density")?;
            let n = pair_product(photon_measure, n_density, "pair marginal photon number")?;
            number[tag] += n;
            energy[tag] += pair_product(energies[tag], n, "pair marginal photon energy")?;
            check_pair_finite(number[tag], "pair photon number accumulation")?;
            check_pair_finite(energy[tag], "pair photon energy accumulation")?;
        }
        check_pair_finite(event_rate, "pair event accumulation")?;
        check_pair_finite(weight_sum, "pair weight accumulation")?;
    }
    let expected_number = pair_product(2.0, event_rate, "pair number residual reference")?;
    let expected_energy = pair_product(delta_s_j, event_rate, "pair energy residual reference")?;
    let number_residuals = [number[0] - expected_number, number[1] - expected_number];
    let energy_residuals = [energy[0] - expected_energy, energy[1] - expected_energy];
    for value in number_residuals.into_iter().chain(energy_residuals) {
        check_pair_finite(value, "pair moment residual")?;
    }
    Ok(PairAssemblyOutput {
        event_rate,
        photon_number_from_marginals: number,
        photon_energy_from_marginals_j: energy,
        photon_number_residuals: number_residuals,
        photon_energy_residuals_j: energy_residuals,
        delta_s_j,
        node_count: nodes.len(),
        quadrature_weight_sum: weight_sum,
        convention,
    })
}
