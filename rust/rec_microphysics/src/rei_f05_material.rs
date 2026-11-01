//! Source-bound original REI F05 accepted H/He material -> proper Thomson rate.
//!
//! This is a **material consumer**. The original 26-event owner, source forcing,
//! accepted history, photon transport and production gates remain unchanged.
//! Inputs refer to *one* original physical cell; 3 audit lanes are not 3 states.
use crate::coverage::CoverageError;

/// Original REI numerical source convention, cm, s.
pub const MPC_CM: f64 = 3.085_677_581_491_367e24;
pub const C_CM_PER_S: f64 = 29_979_245_800.0;
pub const SIGMA_T_CM2: f64 = 6.652_458_705_1e-25;
pub const FIRST_SOURCE_Z: f64 = 5.95;
pub const ORIGINAL_F05_CELLS: usize = 46_080;

/// Original five species order: HI, HII, HeI, HeII, HeIII.
#[derive(Clone, Copy, Debug)]
pub struct SourceCell {
    pub weight: f64,
    pub initial: [f64; 5],
    pub accepted_lower: [f64; 5],
    pub accepted_upper: [f64; 5],
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ElectronSign {
    Gain,
    Loss,
    Ambiguous,
}
impl ElectronSign {
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Gain => "definite_gain",
            Self::Loss => "definite_loss",
            Self::Ambiguous => "sign_ambiguous",
        }
    }
}

#[derive(Clone, Copy, Debug)]
pub struct MaterialWitness {
    pub volume_cm3: f64,
    pub initial_electron_h: f64,
    pub initial_electron_he: f64,
    pub initial_electron: f64,
    pub accepted_electron_lower: f64,
    pub accepted_electron_upper: f64,
    pub delta_h_lower: f64,
    pub delta_h_upper: f64,
    pub delta_he_lower: f64,
    pub delta_he_upper: f64,
    pub gamma_initial_s: f64,
    pub gamma_accepted_lower_s: f64,
    pub gamma_accepted_upper_s: f64,
    pub delta_gamma_lower_s: f64,
    pub delta_gamma_upper_s: f64,
    pub sign: ElectronSign,
}

/// Source volume from the original positive comoving W_j, with no Bianchi ray
/// geometry inferred. The first source interval has constant z=5.95.
pub fn source_volume_cm3(weight: f64) -> Result<f64, CoverageError> {
    if !weight.is_finite() || weight <= 0.0 {
        return Err(CoverageError::InvalidInput(
            "F05 source W_node must be positive",
        ));
    }
    let volume = weight * MPC_CM.powi(3) / (1.0 + FIRST_SOURCE_Z).powi(3);
    if !volume.is_finite() || volume <= 0.0 {
        return Err(CoverageError::InvalidInput(
            "invalid F05 proper source volume",
        ));
    }
    Ok(volume)
}

fn check_finite_positive(value: f64, msg: &'static str) -> Result<(), CoverageError> {
    if !value.is_finite() || value <= 0.0 {
        return Err(CoverageError::InvalidInput(msg));
    }
    Ok(())
}

pub fn evaluate_source_cell(source: SourceCell) -> Result<MaterialWitness, CoverageError> {
    let volume = source_volume_cm3(source.weight)?;
    for j in 0..5 {
        check_finite_positive(source.initial[j], "invalid original initial species")?;
        check_finite_positive(source.accepted_lower[j], "invalid accepted lower species")?;
        if !source.accepted_upper[j].is_finite()
            || source.accepted_lower[j] > source.accepted_upper[j]
        {
            return Err(CoverageError::InvalidInput(
                "invalid original accepted interval",
            ));
        }
    }
    // Original state encloses conserved nuclei. Intervals on components are
    // independent boxes and need not sum *exactly* to the original point.
    let h0 = source.initial[0] + source.initial[1];
    let he0 = source.initial[2] + source.initial[3] + source.initial[4];
    let tol_h = 16.0 * f64::EPSILON * h0;
    let tol_he = 16.0 * f64::EPSILON * he0;
    let hl = source.accepted_lower[0] + source.accepted_lower[1];
    let hu = source.accepted_upper[0] + source.accepted_upper[1];
    let hel = source.accepted_lower[2] + source.accepted_lower[3] + source.accepted_lower[4];
    let heu = source.accepted_upper[2] + source.accepted_upper[3] + source.accepted_upper[4];
    if hl > h0 + tol_h || hu < h0 - tol_h || hel > he0 + tol_he || heu < he0 - tol_he {
        return Err(CoverageError::InvalidInput(
            "original H/He nuclei not enclosed",
        ));
    }
    let h_initial = source.initial[1];
    let he_initial = source.initial[3] + 2.0 * source.initial[4];
    let e_initial = h_initial + he_initial;
    let h_lower = source.accepted_lower[1];
    let h_upper = source.accepted_upper[1];
    let he_lower = source.accepted_lower[3] + 2.0 * source.accepted_lower[4];
    let he_upper = source.accepted_upper[3] + 2.0 * source.accepted_upper[4];
    let e_lower = h_lower + he_lower;
    let e_upper = h_upper + he_upper;
    for e in [e_initial, e_lower, e_upper] {
        check_finite_positive(e, "original electron number must be positive")?;
    }
    if e_lower > e_upper {
        return Err(CoverageError::InvalidInput("inverted electron interval"));
    }
    let scale = C_CM_PER_S * SIGMA_T_CM2 / volume;
    let gamma_initial = scale * e_initial;
    let gamma_lower = scale * e_lower;
    let gamma_upper = scale * e_upper;
    if [gamma_initial, gamma_lower, gamma_upper]
        .iter()
        .any(|x| !x.is_finite() || *x <= 0.0)
    {
        return Err(CoverageError::InvalidInput(
            "invalid local Thomson collision rate",
        ));
    }
    let delta_h_lower = h_lower - h_initial;
    let delta_h_upper = h_upper - h_initial;
    let delta_he_lower = he_lower - he_initial;
    let delta_he_upper = he_upper - he_initial;
    // Subtract accepted electron numbers BEFORE multiplying by the Thomson
    // factor. Subtraction of two almost equal gamma values loses low bits.
    let delta_number_lower = e_lower - e_initial;
    let delta_number_upper = e_upper - e_initial;
    let delta_lower = scale * delta_number_lower;
    let delta_upper = scale * delta_number_upper;
    let sign = if delta_number_lower > 0.0 {
        ElectronSign::Gain
    } else if delta_number_upper < 0.0 {
        ElectronSign::Loss
    } else {
        ElectronSign::Ambiguous
    };
    Ok(MaterialWitness {
        volume_cm3: volume,
        initial_electron_h: h_initial,
        initial_electron_he: he_initial,
        initial_electron: e_initial,
        accepted_electron_lower: e_lower,
        accepted_electron_upper: e_upper,
        delta_h_lower,
        delta_h_upper,
        delta_he_lower,
        delta_he_upper,
        gamma_initial_s: gamma_initial,
        gamma_accepted_lower_s: gamma_lower,
        gamma_accepted_upper_s: gamma_upper,
        delta_gamma_lower_s: delta_lower,
        delta_gamma_upper_s: delta_upper,
        sign,
    })
}

/// Compensated positive sums prevent avoidable representation error without
/// inventing a new astrophysical error certificate.
#[derive(Default)]
struct Compensated {
    sum: f64,
    corr: f64,
}
impl Compensated {
    fn add(&mut self, x: f64) {
        let t = self.sum + x;
        if self.sum.abs() >= x.abs() {
            self.corr += (self.sum - t) + x;
        } else {
            self.corr += (x - t) + self.sum;
        }
        self.sum = t;
    }
    fn result(&self) -> f64 {
        self.sum + self.corr
    }
}

#[derive(Debug)]
pub struct MaterialAggregate {
    pub volume_cm3: f64,
    pub initial_electron: f64,
    pub accepted_lower_electron: f64,
    pub accepted_upper_electron: f64,
    pub initial_gamma_s: f64,
    pub accepted_lower_gamma_s: f64,
    pub accepted_upper_gamma_s: f64,
    pub initial_clumping: f64,
    pub accepted_lower_clumping: f64,
    pub accepted_upper_clumping: f64,
    pub delta_gamma_lower_s: f64,
    pub delta_gamma_upper_s: f64,
    pub counts: [usize; 3],
    pub count: usize,
}

pub fn aggregate_original_material(
    rows: &[MaterialWitness],
) -> Result<MaterialAggregate, CoverageError> {
    if rows.is_empty() {
        return Err(CoverageError::InvalidInput("empty source material"));
    }
    let mut volume = Compensated::default();
    let mut e0 = Compensated::default();
    let mut el = Compensated::default();
    let mut eu = Compensated::default();
    let mut q0 = Compensated::default();
    let mut ql = Compensated::default();
    let mut qu = Compensated::default();
    let mut counts = [0_usize; 3];
    for row in rows {
        volume.add(row.volume_cm3);
        e0.add(row.initial_electron);
        el.add(row.accepted_electron_lower);
        eu.add(row.accepted_electron_upper);
        q0.add(row.initial_electron.powi(2) / row.volume_cm3);
        ql.add(row.accepted_electron_lower.powi(2) / row.volume_cm3);
        qu.add(row.accepted_electron_upper.powi(2) / row.volume_cm3);
        counts[match row.sign {
            ElectronSign::Gain => 0,
            ElectronSign::Loss => 1,
            ElectronSign::Ambiguous => 2,
        }] += 1;
    }
    let v = volume.result();
    let e_init = e0.result();
    let e_lo = el.result();
    let e_hi = eu.result();
    let n0 = e_init / v;
    let nlo = e_lo / v;
    let nhi = e_hi / v;
    let g0 = n0 * C_CM_PER_S * SIGMA_T_CM2;
    let glo = nlo * C_CM_PER_S * SIGMA_T_CM2;
    let ghi = nhi * C_CM_PER_S * SIGMA_T_CM2;
    let cl0 = q0.result() * v / e_init.powi(2);
    let cllo = ql.result() * v / e_hi.powi(2);
    let clhi = qu.result() * v / e_lo.powi(2);
    if [v, e_init, e_lo, e_hi, g0, glo, ghi, cl0, cllo, clhi]
        .iter()
        .any(|x| !x.is_finite() || *x <= 0.0)
        || e_lo > e_hi
        || clhi < 1.0 - 1e-14
    {
        return Err(CoverageError::InvalidInput("invalid source aggregate"));
    }
    Ok(MaterialAggregate {
        volume_cm3: v,
        initial_electron: e_init,
        accepted_lower_electron: e_lo,
        accepted_upper_electron: e_hi,
        initial_gamma_s: g0,
        accepted_lower_gamma_s: glo,
        accepted_upper_gamma_s: ghi,
        initial_clumping: cl0,
        accepted_lower_clumping: cllo,
        accepted_upper_clumping: clhi,
        delta_gamma_lower_s: (e_lo - e_init) * C_CM_PER_S * SIGMA_T_CM2 / v,
        delta_gamma_upper_s: (e_hi - e_init) * C_CM_PER_S * SIGMA_T_CM2 / v,
        counts,
        count: rows.len(),
    })
}
