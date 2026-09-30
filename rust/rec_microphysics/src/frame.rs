//! Local, rotation-free normal/material tetrad bridge for homogeneous finite tilt.
//! Metric signature is (-,+,+,+); beta is material velocity divided by c.
use crate::coverage::CoverageError;
use crate::he_singlet::{C_M_S, Complex64, Mat2, Mat3};
use crate::ledger::MaterialFourForce;

// A binary64 arithmetic guard, not a physical error or coverage tolerance.
const ROUNDING_LIMIT: f64 = 4096.0 * f64::EPSILON;
const SUBNORMAL_SCALE: f64 = 1.0 / f64::MIN_POSITIVE;

fn subnormal_precision(
    value: f64,
    scaled_reference: f64,
    name: &'static str,
) -> Result<(), CoverageError> {
    let reference = finite_result(scaled_reference, name)?;
    if (value * SUBNORMAL_SCALE - reference).abs() > ROUNDING_LIMIT * reference.abs() {
        return Err(uncertain(
            name,
            value,
            "destructive nonzero subnormal rounding",
        ));
    }
    Ok(())
}

fn invalid(message: &'static str) -> CoverageError {
    CoverageError::InvalidInput(message)
}
fn uncertain(quantity: &'static str, value: f64, detail: &'static str) -> CoverageError {
    CoverageError::NumericalDomainUncertain {
        quantity,
        value,
        detail,
    }
}
fn finite_input(value: f64, name: &'static str) -> Result<(), CoverageError> {
    if !value.is_finite() {
        return Err(invalid(name));
    }
    Ok(())
}
fn finite_result(value: f64, name: &'static str) -> Result<f64, CoverageError> {
    if !value.is_finite() {
        return Err(uncertain(name, value, "nonfinite frame arithmetic"));
    }
    Ok(value)
}
fn product(a: f64, b: f64, name: &'static str) -> Result<f64, CoverageError> {
    let value = finite_result(a * b, name)?;
    if a != 0.0 && b != 0.0 && value == 0.0 {
        return Err(uncertain(name, value, "nonzero frame product underflowed"));
    }
    if value.is_subnormal() {
        // Scale the smaller operand first; this is normal-range arithmetic
        // for a nonzero subnormal product, with no change to the result.
        let reference = if a.abs() <= b.abs() {
            (a * SUBNORMAL_SCALE) * b
        } else {
            a * (b * SUBNORMAL_SCALE)
        };
        subnormal_precision(value, reference, name)?;
    }
    Ok(value)
}
fn quotient(a: f64, b: f64, name: &'static str) -> Result<f64, CoverageError> {
    let value = finite_result(a / b, name)?;
    if a != 0.0 && value == 0.0 {
        return Err(uncertain(name, value, "nonzero frame quotient underflowed"));
    }
    if value.is_subnormal() {
        subnormal_precision(value, (a * SUBNORMAL_SCALE) / b, name)?;
    }
    Ok(value)
}
fn dot(a: [f64; 3], b: [f64; 3], name: &'static str) -> Result<f64, CoverageError> {
    let mut sum = 0.0;
    for k in 0..3 {
        sum = finite_result(sum + product(a[k], b[k], name)?, name)?;
    }
    Ok(sum)
}
fn unit_direction(e: [f64; 3]) -> Result<(), CoverageError> {
    for x in e {
        finite_input(x, "photon direction must be finite")?;
    }
    let norm = e[0].hypot(e[1]).hypot(e[2]);
    if !norm.is_finite() || (norm - 1.0).abs() > 64.0 * f64::EPSILON {
        return Err(invalid("photon direction must be unit length"));
    }
    Ok(())
}

/// A finite, strictly subluminal material velocity in a normal orthonormal tetrad.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct MaterialVelocity {
    beta: [f64; 3],
    gamma: f64,
}
impl MaterialVelocity {
    pub fn new(beta: [f64; 3]) -> Result<Self, CoverageError> {
        for x in beta {
            finite_input(x, "material beta must be finite")?;
        }
        let norm = beta[0].hypot(beta[1]).hypot(beta[2]);
        if !norm.is_finite() || norm >= 1.0 {
            return Err(invalid("material beta norm must be below one"));
        }
        let residual = (1.0 - norm) * (1.0 + norm);
        // Two hypot operations and the norm subtraction can amplify a few
        // ulps by 1/(1-beta^2). Refuse the ill-conditioned domain instead of
        // returning an apparently valid but inaccurate Lorentz factor.
        if 4.0 * f64::EPSILON / residual > ROUNDING_LIMIT {
            return Err(uncertain(
                "material gamma",
                residual,
                "near-light-speed norm is numerically ill-conditioned",
            ));
        }
        let gamma = finite_result(1.0 / residual.sqrt(), "material gamma")?;
        Ok(Self { beta, gamma })
    }
    pub fn beta(self) -> [f64; 3] {
        self.beta
    }
    pub fn gamma(self) -> f64 {
        self.gamma
    }
    pub fn inverse_gamma(self) -> f64 {
        1.0 / self.gamma
    }

    /// Normal photon ray at a fixed event to material energy (eV) and direction.
    pub fn normal_to_material_ray(
        self,
        energy_normal_ev: f64,
        direction_normal: [f64; 3],
    ) -> Result<MaterialRay, CoverageError> {
        finite_input(energy_normal_ev, "normal photon energy must be finite")?;
        if energy_normal_ev <= 0.0 {
            return Err(invalid("normal photon energy must be positive"));
        }
        unit_direction(direction_normal)?;
        let bdote = dot(self.beta, direction_normal, "beta dot photon direction")?;
        let doppler = product(
            self.gamma,
            finite_result(1.0 - bdote, "ray Doppler difference")?,
            "ray Doppler factor",
        )?;
        if doppler <= 0.0 {
            return Err(uncertain(
                "ray Doppler factor",
                doppler,
                "nonpositive ray clock",
            ));
        }
        let energy_material_ev = product(doppler, energy_normal_ev, "material photon energy")?;
        if energy_material_ev <= 0.0 {
            return Err(uncertain(
                "material photon energy",
                energy_material_ev,
                "positive energy underflowed",
            ));
        }
        // Apply the same rotation-free Lorentz map as for an arbitrary four-vector
        // to the dimensionless null vector (1,e). This avoids squaring energy.
        let mapped = self.normal_to_material_four_vector([
            1.0,
            direction_normal[0],
            direction_normal[1],
            direction_normal[2],
        ])?;
        let direction_material = [
            quotient(mapped[1], mapped[0], "material ray direction")?,
            quotient(mapped[2], mapped[0], "material ray direction")?,
            quotient(mapped[3], mapped[0], "material ray direction")?,
        ];
        let norm = direction_material[0]
            .hypot(direction_material[1])
            .hypot(direction_material[2]);
        if !norm.is_finite() || (norm - 1.0).abs() > 64.0 * f64::EPSILON {
            return Err(uncertain(
                "material ray direction",
                norm,
                "aberration lost unit length",
            ));
        }
        Ok(MaterialRay {
            energy_material_ev,
            direction_material,
            doppler,
        })
    }

    /// Generic signed contravariant four-vector, normal to material tetrad.
    pub fn normal_to_material_four_vector(
        self,
        normal: [f64; 4],
    ) -> Result<[f64; 4], CoverageError> {
        self.boost(normal, false)
    }
    /// Generic signed contravariant four-vector, material to normal tetrad.
    pub fn material_to_normal_four_vector(
        self,
        material: [f64; 4],
    ) -> Result<[f64; 4], CoverageError> {
        self.boost(material, true)
    }
    fn boost(self, input: [f64; 4], inverse: bool) -> Result<[f64; 4], CoverageError> {
        for x in input {
            finite_input(x, "four-vector components must be finite")?;
        }
        if self.beta == [0.0; 3] {
            return Ok(input);
        }
        let spatial = [input[1], input[2], input[3]];
        let bdot = dot(self.beta, spatial, "beta dot four-vector")?;
        let sign = if inverse { 1.0 } else { -1.0 };
        let time_inner = finite_result(input[0] + sign * bdot, "boost time difference")?;
        let time = product(self.gamma, time_inner, "boost time component")?;
        // gamma^2/(gamma+1) equals (gamma-1)/beta^2 without small-beta loss.
        let coefficient = self.gamma * self.gamma / (self.gamma + 1.0);
        let longitudinal = product(coefficient, bdot, "boost longitudinal coefficient")?;
        let temporal = product(self.gamma, input[0], "boost temporal coefficient")?;
        let shift = finite_result(longitudinal + sign * temporal, "boost spatial shift")?;
        let mut output = [time, 0.0, 0.0, 0.0];
        for k in 0..3 {
            output[k + 1] = finite_result(
                spatial[k] + product(shift, self.beta[k], "boost spatial product")?,
                "boost spatial component",
            )?;
        }
        Ok(output)
    }

    /// (R - theta_U n)/gamma for homogeneous material proper density.
    pub fn scalar_source_normal_time(
        self,
        material_rate: f64,
        theta_u: f64,
        proper_density: f64,
    ) -> Result<f64, CoverageError> {
        for x in [material_rate, theta_u, proper_density] {
            finite_input(x, "scalar source inputs must be finite")?;
        }
        if proper_density < 0.0 {
            return Err(invalid("material proper density must be nonnegative"));
        }
        let dilution = product(theta_u, proper_density, "scalar dilution")?;
        let numerator = finite_result(material_rate - dilution, "scalar net source")?;
        product(numerator, self.inverse_gamma(), "normal-time scalar source")
    }

    /// Orbital collision block B/gamma only; no triad rotation or transport connection.
    pub fn orbital_collision_normal_time(self, material_b: Mat3) -> Result<Mat3, CoverageError> {
        let mut out = material_b;
        for row in &mut out.0 {
            for z in row {
                finite_input(z.re, "orbital collision matrix must be finite")?;
                finite_input(z.im, "orbital collision matrix must be finite")?;
                z.re = product(
                    z.re,
                    self.inverse_gamma(),
                    "normal-time orbital real source",
                )?;
                z.im = product(
                    z.im,
                    self.inverse_gamma(),
                    "normal-time orbital imaginary source",
                )?;
            }
        }
        Ok(out)
    }

    /// Boost both signed force vectors; inherited SI components (P/c, momentum rate).
    pub fn material_four_force_to_normal(
        self,
        force: MaterialFourForce,
    ) -> Result<NormalFourForce, CoverageError> {
        Ok(NormalFourForce {
            q_matter: self.material_to_normal_four_vector(force.q_matter)?,
            q_photon: self.material_to_normal_four_vector(force.q_photon)?,
        })
    }
}

/// Only `MaterialVelocity::normal_to_material_ray` can construct a validated ray.
/// ```compile_fail
/// use rec_microphysics::frame::MaterialRay;
/// let _ = MaterialRay { energy_material_ev: 1.0, direction_material: [1.0, 0.0, 0.0], doppler: -1.0 };
/// ```
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct MaterialRay {
    energy_material_ev: f64,
    direction_material: [f64; 3],
    /// D = E_material/E_normal = dt_material_ray/dt_normal_ray.
    doppler: f64,
}
impl MaterialRay {
    pub fn energy_material_ev(self) -> f64 {
        self.energy_material_ev
    }
    pub fn direction_material(self) -> [f64; 3] {
        self.direction_material
    }
    pub fn doppler(self) -> f64 {
        self.doppler
    }
    /// Apply only after the caller has mapped the material photon collision Mat2
    /// through the physical material-to-normal screen component map.
    /// Occupation collision RHS per normal second = D times mapped material RHS.
    pub fn normal_time_after_screen_map(
        self,
        mapped_material_source: Mat2,
    ) -> Result<Mat2, CoverageError> {
        scale_mat2(
            mapped_material_source,
            self.doppler,
            "normal-time photon collision",
        )
    }
    /// As above, for normal path length in meters: D/c times mapped RHS.
    pub fn normal_length_after_screen_map(
        self,
        mapped_material_source: Mat2,
    ) -> Result<Mat2, CoverageError> {
        let per_second = self.normal_time_after_screen_map(mapped_material_source)?;
        scale_mat2(per_second, 1.0 / C_M_S, "normal-length photon collision")
    }
    /// Normal energy (eV) supporting material sharp line epsilon.
    pub fn sharp_line_normal_energy_ev(
        self,
        epsilon_material_ev: f64,
    ) -> Result<f64, CoverageError> {
        finite_input(epsilon_material_ev, "material line energy must be finite")?;
        if epsilon_material_ev <= 0.0 {
            return Err(invalid("material line energy must be positive"));
        }
        quotient(
            epsilon_material_ev,
            self.doppler,
            "normal sharp-line energy",
        )
    }
    /// Distribution-coordinate Jacobian in delta(D E_n-epsilon)=delta(E_n-epsilon/D)/D.
    /// This is separate from, and must be applied exactly once after, any rate-clock scaling.
    pub fn sharp_line_delta_jacobian(self) -> Result<f64, CoverageError> {
        quotient(1.0, self.doppler, "sharp-line delta Jacobian")
    }
}
fn scale_mat2(input: Mat2, factor: f64, name: &'static str) -> Result<Mat2, CoverageError> {
    let mut out = input;
    for row in &mut out.0 {
        for z in row {
            finite_input(z.re, "mapped photon collision matrix must be finite")?;
            finite_input(z.im, "mapped photon collision matrix must be finite")?;
            *z = Complex64::new(product(z.re, factor, name)?, product(z.im, factor, name)?);
        }
    }
    Ok(out)
}

/// Signed force in the normal orthonormal tetrad, SI `(power/c, momentum rate)`.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct NormalFourForce {
    pub q_photon: [f64; 4],
    pub q_matter: [f64; 4],
}
