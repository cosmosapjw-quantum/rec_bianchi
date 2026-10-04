//! Physical null-gauge screen transport at one normal/material ray event.
//! The caller supplies a screen for each ray; no Stokes or basis orientation is imposed.

use crate::coverage::CoverageError;
use crate::frame::MaterialVelocity;
use crate::he_singlet::{Complex64, Mat2, RealV, SCREEN_TOLERANCE, validate_screen};

const ROUNDING_LIMIT: f64 = 4096.0 * f64::EPSILON;
const SUBNORMAL_SCALE: f64 = 1.0 / f64::MIN_POSITIVE;

fn uncertain(quantity: &'static str, value: f64, detail: &'static str) -> CoverageError {
    CoverageError::NumericalDomainUncertain {
        quantity,
        value,
        detail,
    }
}

fn finite(value: f64, quantity: &'static str) -> Result<f64, CoverageError> {
    if !value.is_finite() {
        return Err(uncertain(quantity, value, "nonfinite screen arithmetic"));
    }
    Ok(value)
}

fn product(a: f64, b: f64, quantity: &'static str) -> Result<f64, CoverageError> {
    let value = finite(a * b, quantity)?;
    if a != 0.0 && b != 0.0 && value == 0.0 {
        return Err(uncertain(
            quantity,
            value,
            "nonzero screen product underflowed",
        ));
    }
    if value.is_subnormal() {
        let reference = if a.abs() <= b.abs() {
            (a * SUBNORMAL_SCALE) * b
        } else {
            a * (b * SUBNORMAL_SCALE)
        };
        let reference = finite(reference, quantity)?;
        if (value * SUBNORMAL_SCALE - reference).abs() > ROUNDING_LIMIT * reference.abs() {
            return Err(uncertain(
                quantity,
                value,
                "destructive nonzero subnormal rounding",
            ));
        }
    }
    Ok(value)
}

fn quotient(a: f64, b: f64, quantity: &'static str) -> Result<f64, CoverageError> {
    let value = finite(a / b, quantity)?;
    if a != 0.0 && value == 0.0 {
        return Err(uncertain(
            quantity,
            value,
            "nonzero screen quotient underflowed",
        ));
    }
    if value.is_subnormal() {
        let reference = finite((a * SUBNORMAL_SCALE) / b, quantity)?;
        if (value * SUBNORMAL_SCALE - reference).abs() > ROUNDING_LIMIT * reference.abs() {
            return Err(uncertain(
                quantity,
                value,
                "destructive nonzero subnormal rounding",
            ));
        }
    }
    Ok(value)
}

fn dot3(a: [f64; 3], b: [f64; 3], quantity: &'static str) -> Result<f64, CoverageError> {
    let mut sum = 0.0;
    for k in 0..3 {
        sum = finite(sum + product(a[k], b[k], quantity)?, quantity)?;
    }
    Ok(sum)
}

fn column(v: RealV, j: usize) -> [f64; 3] {
    [v[0][j], v[1][j], v[2][j]]
}

/// A rotation/reflection between caller-bound physical screens at one ray event.
/// `T[A][a]` is the material screen A overlap with gauged, boosted normal screen a.
#[derive(Clone, Copy, Debug)]
pub struct ScreenTransform {
    transported_normal_screen: RealV,
    overlap: [[f64; 2]; 2],
}

impl ScreenTransform {
    pub fn new(
        velocity: MaterialVelocity,
        direction_normal: [f64; 3],
        screen_normal: RealV,
        screen_material: RealV,
    ) -> Result<Self, CoverageError> {
        let ray = velocity.normal_to_material_ray(1.0, direction_normal)?;
        validate_screen(screen_normal, Some(direction_normal))?;
        validate_screen(screen_material, Some(ray.direction_material()))?;

        let beta = velocity.beta();
        let doppler = ray.doppler();
        let mut transported = [[0.0; 2]; 3];
        for a in 0..2 {
            let v = column(screen_normal, a);
            // Eq. (135): b_g = b + (u.b)/D k, with b=(0,v), k=(1,e).
            let u_dot_b = product(
                velocity.gamma(),
                dot3(beta, v, "material velocity screen overlap")?,
                "material four-velocity screen overlap",
            )?;
            let gauge = quotient(u_dot_b, doppler, "null-gauge coefficient")?;
            let mut gauged = [gauge, 0.0, 0.0, 0.0];
            for k in 0..3 {
                gauged[k + 1] = finite(
                    v[k] + product(gauge, direction_normal[k], "null-gauge spatial term")?,
                    "null-gauge spatial component",
                )?;
            }
            let mapped = velocity.normal_to_material_four_vector(gauged)?;
            // In the material tetrad a physical screen has zero time component.
            if mapped[0].abs() > ROUNDING_LIMIT * (1.0 + gauge.abs()) {
                return Err(uncertain(
                    "transported screen time component",
                    mapped[0],
                    "null-gauge boost lost material simultaneity",
                ));
            }
            for k in 0..3 {
                transported[k][a] = mapped[k + 1];
            }
        }
        // This checks both norm and transversality without projecting or normalizing.
        validate_screen(transported, Some(ray.direction_material()))?;

        let mut overlap = [[0.0; 2]; 2];
        for (a, row) in overlap.iter_mut().enumerate() {
            for (b, entry) in row.iter_mut().enumerate() {
                *entry = dot3(
                    column(screen_material, a),
                    column(transported, b),
                    "physical screen overlap",
                )?;
            }
        }
        // A valid pair of bases must yield O(2), allowing either handedness.
        for a in 0..2 {
            for b in 0..2 {
                let norm = finite(
                    overlap[a][0] * overlap[b][0] + overlap[a][1] * overlap[b][1],
                    "screen overlap orthogonality",
                )?;
                let target = if a == b { 1.0 } else { 0.0 };
                if (norm - target).abs() > 4.0 * SCREEN_TOLERANCE {
                    return Err(uncertain(
                        "screen overlap orthogonality",
                        norm,
                        "screen bases lost an orthogonal component map",
                    ));
                }
            }
        }
        Ok(Self {
            transported_normal_screen: transported,
            overlap,
        })
    }

    pub fn overlap(self) -> [[f64; 2]; 2] {
        self.overlap
    }

    pub fn transported_normal_screen(self) -> RealV {
        self.transported_normal_screen
    }

    /// Occupation/coherency or signed collision block: F_m = T F_n T^T.
    pub fn normal_to_material(self, block: Mat2) -> Result<Mat2, CoverageError> {
        self.transform(block, false)
    }

    /// Inverse component map: F_n = T^T F_m T. No clock factor is applied.
    pub fn material_to_normal(self, block: Mat2) -> Result<Mat2, CoverageError> {
        self.transform(block, true)
    }

    fn transform(self, block: Mat2, inverse: bool) -> Result<Mat2, CoverageError> {
        for row in block.0 {
            for z in row {
                if !z.re.is_finite() || !z.im.is_finite() {
                    return Err(CoverageError::InvalidInput("screen block must be finite"));
                }
            }
        }
        let t = |i: usize, j: usize| {
            if inverse {
                self.overlap[j][i]
            } else {
                self.overlap[i][j]
            }
        };
        let mut middle = [[Complex64::default(); 2]; 2];
        let mut out = [[Complex64::default(); 2]; 2];
        for i in 0..2 {
            for j in 0..2 {
                for k in 0..2 {
                    middle[i][j].re = finite(
                        middle[i][j].re
                            + product(t(i, k), block.0[k][j].re, "screen block real product")?,
                        "screen block real sum",
                    )?;
                    middle[i][j].im = finite(
                        middle[i][j].im
                            + product(t(i, k), block.0[k][j].im, "screen block imaginary product")?,
                        "screen block imaginary sum",
                    )?;
                }
            }
        }
        for i in 0..2 {
            for j in 0..2 {
                for k in 0..2 {
                    out[i][j].re = finite(
                        out[i][j].re
                            + product(middle[i][k].re, t(j, k), "screen block real product")?,
                        "screen block real sum",
                    )?;
                    out[i][j].im = finite(
                        out[i][j].im
                            + product(middle[i][k].im, t(j, k), "screen block imaginary product")?,
                        "screen block imaginary sum",
                    )?;
                }
            }
        }
        Ok(Mat2(out))
    }
}
