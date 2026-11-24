//! Cold-electron Thomson attenuation on a caller-supplied normal-tetrad null ray.
//!
//! Times are normal proper seconds and directions point along photon propagation.
//! The receiver is the final sample. Each interval uses a log-linear positive
//! rest reference density and linear endpoint values of x_e * gamma*(1-beta.e).
//! This preserves the original F08 gas interpolant for comoving electrons.
use crate::coverage::CoverageError;
use crate::frame::MaterialVelocity;
use crate::rei_f05_material::{C_CM_PER_S, SIGMA_T_CM2};

/// Source-pinned c sigma_T in m^3/s. The source constants use cm and seconds.
pub const C_SIGMA_T_M3_S: f64 = C_CM_PER_S * SIGMA_T_CM2 * 1e-6;

fn finite(value: f64, quantity: &'static str) -> Result<f64, CoverageError> {
    if value.is_finite() {
        Ok(value)
    } else {
        Err(CoverageError::NumericalDomainUncertain {
            quantity,
            value,
            detail: "nonfinite Thomson history arithmetic",
        })
    }
}
// Choose another association if an intermediate over/underflows while the
// final product is representable, as for very small densities and long clocks.
fn product3(a: f64, b: f64, c: f64, quantity: &'static str) -> Result<f64, CoverageError> {
    if a == 0. || b == 0. || c == 0. {
        return Ok(0.);
    }
    for (x, y, z) in [(a, b, c), (b, c, a), (a, c, b)] {
        let xy = x * y;
        if xy.is_normal() {
            let result = xy * z;
            if result.is_finite() && result != 0. {
                return Ok(result);
            }
        }
    }
    Err(CoverageError::NumericalDomainUncertain {
        quantity,
        value: (a * b) * c,
        detail: "optical product outside floating-point range",
    })
}
fn dot(a: [f64; 3], b: [f64; 3]) -> f64 {
    a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
}

#[derive(Clone, Copy, Debug)]
pub struct RaySample {
    t_s: f64,
    n_ref_m3: f64,
    x_e: f64,
    velocity: MaterialVelocity,
    direction: [f64; 3],
    doppler: f64,
    yield_doppler: f64,
}

impl RaySample {
    /// Use one material owner for each physical interval. For a supplied total
    /// density n_e use any constant positive reference density and x_e=n_e/n_ref.
    pub fn new(
        normal_t_s: f64,
        n_reference_rest_m3: f64,
        electrons_per_reference: f64,
        beta: [f64; 3],
        photon_direction: [f64; 3],
    ) -> Result<Self, CoverageError> {
        if !normal_t_s.is_finite()
            || !n_reference_rest_m3.is_finite()
            || n_reference_rest_m3 <= 0.
            || !electrons_per_reference.is_finite()
            || electrons_per_reference < 0.
        {
            return Err(CoverageError::InvalidInput(
                "finite time, positive reference density and nonnegative electron yield required",
            ));
        }
        let velocity = MaterialVelocity::new(beta)?;
        let doppler = velocity
            .normal_to_material_ray(1., photon_direction)?
            .doppler();
        Ok(Self {
            t_s: normal_t_s,
            n_ref_m3: n_reference_rest_m3,
            x_e: electrons_per_reference,
            velocity,
            direction: photon_direction,
            doppler,
            yield_doppler: finite(electrons_per_reference * doppler, "x_e Doppler")?,
        })
    }

    /// Charge-neutral H/He gas. Ion ordering is [n_HII, n_HeII, n_HeIII],
    /// each a proper particle density in m^-3.
    pub fn from_ion_densities(
        normal_t_s: f64,
        n_h_rest_m3: f64,
        ions_rest_m3: [f64; 3],
        beta: [f64; 3],
        photon_direction: [f64; 3],
    ) -> Result<Self, CoverageError> {
        if ions_rest_m3.iter().any(|x| !x.is_finite() || *x < 0.) || ions_rest_m3[0] > n_h_rest_m3 {
            return Err(CoverageError::InvalidInput(
                "invalid proper ion number densities",
            ));
        }
        let ne = ions_rest_m3[0] + ions_rest_m3[1] + 2. * ions_rest_m3[2];
        Self::new(
            normal_t_s,
            n_h_rest_m3,
            ne / n_h_rest_m3,
            beta,
            photon_direction,
        )
    }

    pub fn normal_rate_per_s(&self) -> Result<f64, CoverageError> {
        product3(
            C_SIGMA_T_M3_S,
            self.n_ref_m3,
            self.yield_doppler,
            "normal collision rate",
        )
    }

    fn yield_doppler_tangent(&self, d: RayTangent) -> Result<f64, CoverageError> {
        if !d.d_ln_reference.is_finite()
            || !d.d_electrons_per_reference.is_finite()
            || d.d_beta
                .iter()
                .chain(d.d_direction.iter())
                .any(|x| !x.is_finite())
        {
            return Err(CoverageError::InvalidInput("ray tangent must be finite"));
        }
        let norm = d.d_direction[0]
            .hypot(d.d_direction[1])
            .hypot(d.d_direction[2]);
        if dot(self.direction, d.d_direction).abs() > 128. * f64::EPSILON * norm {
            return Err(CoverageError::InvalidInput(
                "direction tangent must lie in tangent plane",
            ));
        }
        let beta = self.velocity.beta();
        let gamma = self.velocity.gamma();
        let ddoppler = self.doppler * gamma * gamma * dot(beta, d.d_beta)
            - gamma * (dot(d.d_beta, self.direction) + dot(beta, d.d_direction));
        finite(
            self.doppler * d.d_electrons_per_reference + self.x_e * ddoppler,
            "x_e Doppler tangent",
        )
    }
}

/// Derivatives with respect to one scalar parameter at fixed normal times.
#[derive(Clone, Copy, Debug, Default)]
pub struct RayTangent {
    pub d_ln_reference: f64,
    pub d_electrons_per_reference: f64,
    pub d_beta: [f64; 3],
    pub d_direction: [f64; 3],
}

#[derive(Clone, Copy, Debug, Default)]
pub struct VisibilityBin {
    pub far_t_s: f64,
    pub near_t_s: f64,
    pub delta_tau: f64,
    pub tau_near: f64,
    pub tau_far: f64,
    pub survival_near: f64,
    pub visibility_mass: f64,
}

#[derive(Clone, Copy, Debug, Default)]
pub struct VisibilityTangent {
    pub d_delta_tau: f64,
    pub d_tau_near: f64,
    pub d_tau_far: f64,
    pub d_visibility_mass: f64,
}

// M_j = integral_0^1 u^j exp(-lambda u) du, oriented from larger density
// towards smaller. This avoids both exponential overflow and signed weights.
fn moments(lambda: f64) -> [f64; 3] {
    if lambda < 0.5 {
        if lambda == 0. {
            return [1., 0.5, 1. / 3.];
        }
        let mut m = [0.; 3];
        let mut power = 1.;
        for k in 0..18 {
            for (j, value) in m.iter_mut().enumerate() {
                *value += power / (k + j + 1) as f64;
            }
            power *= -lambda / (k + 1) as f64;
        }
        m
    } else {
        let end = (-lambda).exp();
        let m0 = -(-lambda).exp_m1() / lambda;
        let m1 = (m0 - end) / lambda;
        [m0, m1, (2. * m1 - end) / lambda]
    }
}

struct Exposure {
    high: usize,
    low: usize,
    scale: f64,
    m: [f64; 3],
}
impl Exposure {
    fn new(samples: &[RaySample], i: usize) -> Result<Self, CoverageError> {
        let dt = samples[i + 1].t_s - samples[i].t_s;
        if !dt.is_finite() || dt <= 0. {
            return Err(CoverageError::InvalidInput(
                "normal times must be strictly increasing",
            ));
        }
        let (high, low) = if samples[i].n_ref_m3 >= samples[i + 1].n_ref_m3 {
            (i, i + 1)
        } else {
            (i + 1, i)
        };
        let hi = samples[high].n_ref_m3;
        let lo = samples[low].n_ref_m3;
        let lambda = if lo >= 0.5 * hi {
            -((lo - hi) / hi).ln_1p()
        } else {
            hi.ln() - lo.ln()
        };
        Ok(Self {
            high,
            low,
            scale: product3(C_SIGMA_T_M3_S, hi, dt, "exposure scale")?,
            m: moments(lambda),
        })
    }
    fn tau(&self, s: &[RaySample]) -> Result<f64, CoverageError> {
        let [m0, m1, _] = self.m;
        finite(
            self.scale * ((m0 - m1) * s[self.high].yield_doppler + m1 * s[self.low].yield_doppler),
            "cell optical depth",
        )
    }
    fn tangent(&self, s: &[RaySample], d: &[RayTangent], dq: &[f64]) -> Result<f64, CoverageError> {
        let [m0, m1, m2] = self.m;
        let ah = d[self.high].d_ln_reference;
        let al = d[self.low].d_ln_reference;
        let change = (m0 - m1) * dq[self.high]
            + m1 * dq[self.low]
            + s[self.high].yield_doppler * ((m0 - 2. * m1 + m2) * ah + (m1 - m2) * al)
            + s[self.low].yield_doppler * ((m1 - m2) * ah + m2 * al);
        finite(self.scale * change, "cell optical depth tangent")
    }
}

/// Returns bins ordered by increasing normal time. The finite observer is at
/// zero optical depth. The mass is the unconditional last-collision probability
/// in each cell, with the unresolved incoming survival exp(-tau_far[0]).
pub fn integrate(samples: &[RaySample]) -> Result<Vec<VisibilityBin>, CoverageError> {
    if samples.len() < 2 {
        return Err(CoverageError::InvalidInput(
            "at least two ray samples required",
        ));
    }
    let mut bins = vec![VisibilityBin::default(); samples.len() - 1];
    let mut near: f64 = 0.;
    for i in (0..bins.len()).rev() {
        let delta = Exposure::new(samples, i)?.tau(samples)?;
        let far = finite(near + delta, "cumulative optical depth")?;
        let survival = (-near).exp();
        bins[i] = VisibilityBin {
            far_t_s: samples[i].t_s,
            near_t_s: samples[i + 1].t_s,
            delta_tau: delta,
            tau_near: near,
            tau_far: far,
            survival_near: survival,
            visibility_mass: survival * -(-delta).exp_m1(),
        };
        near = far;
    }
    Ok(bins)
}

/// Analytic fixed-time Jacobian-vector product for the same discrete quadrature.
pub fn integrate_tangent(
    samples: &[RaySample],
    tangent: &[RayTangent],
) -> Result<(Vec<VisibilityBin>, Vec<VisibilityTangent>), CoverageError> {
    if samples.len() != tangent.len() {
        return Err(CoverageError::InvalidInput(
            "one tangent per ray sample required",
        ));
    }
    let bins = integrate(samples)?;
    let dq = samples
        .iter()
        .zip(tangent)
        .map(|(p, d)| p.yield_doppler_tangent(*d))
        .collect::<Result<Vec<_>, _>>()?;
    let mut out = vec![VisibilityTangent::default(); bins.len()];
    let mut d_near = 0.;
    for i in (0..bins.len()).rev() {
        let b = bins[i];
        let d_delta = Exposure::new(samples, i)?.tangent(samples, tangent, &dq)?;
        let d_far = finite(d_near + d_delta, "cumulative optical depth tangent")?;
        let mass = finite(
            b.survival_near * (-b.delta_tau).exp() * d_delta - b.visibility_mass * d_near,
            "visibility mass tangent",
        )?;
        out[i] = VisibilityTangent {
            d_delta_tau: d_delta,
            d_tau_near: d_near,
            d_tau_far: d_far,
            d_visibility_mass: mass,
        };
        d_near = d_far;
    }
    Ok((bins, out))
}
