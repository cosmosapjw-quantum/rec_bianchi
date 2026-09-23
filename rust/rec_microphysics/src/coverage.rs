use core::fmt;

#[derive(Debug, Clone, PartialEq)]
pub enum CoverageError {
    OutOfBand {
        family: &'static str,
        value: f64,
        min: f64,
        max: f64,
    },
    MissingAuthority {
        family: &'static str,
        value: f64,
        detail: &'static str,
    },
    InvalidInput(&'static str),
}

impl fmt::Display for CoverageError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::OutOfBand {
                family,
                value,
                min,
                max,
            } => {
                write!(f, "{family}: {value} outside represented [{min},{max}]")
            }
            Self::MissingAuthority {
                family,
                value,
                detail,
            } => {
                write!(
                    f,
                    "{family}: no adopted numerical authority at {value}: {detail}"
                )
            }
            Self::InvalidInput(msg) => write!(f, "invalid input: {msg}"),
        }
    }
}

impl std::error::Error for CoverageError {}

pub const D86_Y_MIN: f64 = 1.0 / 40.0;
pub const D86_Y_MAX: f64 = 39.0 / 40.0;

const D86_HALF: [f64; 20] = [
    7.736, 25.158, 43.302, 59.693, 73.920, 86.112, 96.523, 105.407, 112.986, 119.447, 124.942,
    129.596, 133.508, 136.760, 139.416, 141.525, 143.128, 144.253, 144.921, 145.142,
];

/// Canonical WU31-A1 D86 length-gauge representative.
/// Reflect y -> 1-y, then linearly interpolate the printed j/40 half-grid.
/// Outside [1/40,39/40] is UNKNOWN and therefore a typed error, never zero.
pub fn d86_w(y: f64) -> Result<f64, CoverageError> {
    if !y.is_finite() {
        return Err(CoverageError::InvalidInput("two-photon y must be finite"));
    }
    if !(D86_Y_MIN..=D86_Y_MAX).contains(&y) {
        return Err(CoverageError::OutOfBand {
            family: "D86_TABLE_V_LENGTH_LINEAR_B",
            value: y,
            min: D86_Y_MIN,
            max: D86_Y_MAX,
        });
    }
    let yr = if y > 0.5 { 1.0 - y } else { y };
    let x = yr * 40.0;
    let nearest = x.round();
    if (x - nearest).abs() <= 16.0 * f64::EPSILON * x.abs().max(1.0) {
        let idx = nearest as usize;
        if (1..=20).contains(&idx) {
            return Ok(D86_HALF[idx - 1]);
        }
    }
    let j0 = x.floor() as usize;
    let j1 = j0 + 1;
    if j0 < 1 || j1 > 20 {
        return Err(CoverageError::OutOfBand {
            family: "D86_TABLE_V_LENGTH_LINEAR_B",
            value: y,
            min: D86_Y_MIN,
            max: D86_Y_MAX,
        });
    }
    let t = x - j0 as f64;
    Ok(D86_HALF[j0 - 1] * (1.0 - t) + D86_HALF[j1 - 1] * t)
}
