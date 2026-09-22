use crate::coverage::CoverageError;
use crate::he_singlet::HeConstants;

pub const EVENT_MATRIX: [[i32; 5]; 6] = [
    [1, 0, 0, 0, 1],
    [0, 1, 0, -1, -1],
    [-1, -1, -1, 0, 0],
    [0, 0, 1, 1, 0],
    [0, 0, 1, 1, 0],
    [1, 1, -1, -1, 2],
];

#[derive(Clone, Copy, Debug)]
pub struct ChannelRates {
    pub r584: f64,
    pub rir: f64,
    pub rp: f64,
    pub rs: f64,
    pub r2g: f64,
}
impl ChannelRates {
    fn as_array(self) -> [f64; 5] {
        [self.r584, self.rir, self.rp, self.rs, self.r2g]
    }
}

#[derive(Clone, Copy, Debug)]
pub struct HeEnergies {
    pub delta_s: f64,
    pub delta_p: f64,
    pub epsilon_ir: f64,
    pub chi_p: f64,
    pub chi_s: f64,
}
impl HeEnergies {
    pub fn canonical() -> Self {
        let c = HeConstants::canonical();
        Self {
            delta_s: c.delta_s_ev,
            delta_p: c.delta_p_ev,
            epsilon_ir: c.epsilon_ir_ev,
            chi_p: c.chi_p_ev,
            chi_s: c.chi_s_ev,
        }
    }
}

#[derive(Clone, Copy, Debug)]
pub struct HeEventLedger {
    pub species_source: [f64; 6],
    pub he_nuclei_residual: f64,
    pub charge_minus_e_residual: f64,
    pub photon_number_source: f64,
    pub p_internal: f64,
    pub p_gamma: f64,
    pub h_kin: f64,
    pub energy_residual: f64,
    pub event_matrix: [[i32; 5]; 6],
}

/// Assemble the selected-He signed event ledger. `bf_photon_energy` is
/// integral E (j_P+j_S) dE dOmega in the same energy units as `HeEnergies`.
pub fn assemble_he_event_ledger(
    r: ChannelRates,
    e: HeEnergies,
    bf_photon_energy: f64,
    h_kin: f64,
) -> Result<HeEventLedger, CoverageError> {
    let vals = [r.r584, r.rir, r.rp, r.rs, r.r2g, bf_photon_energy, h_kin];
    if vals.iter().any(|x| !x.is_finite()) {
        return Err(CoverageError::InvalidInput("ledger values must be finite"));
    }
    let rates = r.as_array();
    let mut s = [0.0; 6];
    for i in 0..6 {
        for j in 0..5 {
            s[i] += EVENT_MATRIX[i][j] as f64 * rates[j];
        }
    }
    let nuclei = s[0] + s[1] + s[2] + s[3];
    let charge = s[3] - s[4];
    let pint = -e.delta_p * r.r584 - e.epsilon_ir * r.rir - e.delta_s * r.r2g
        + e.chi_p * r.rp
        + e.chi_s * r.rs;
    let pg = e.delta_p * r.r584 + e.epsilon_ir * r.rir + e.delta_s * r.r2g - bf_photon_energy;
    Ok(HeEventLedger {
        species_source: s,
        he_nuclei_residual: nuclei,
        charge_minus_e_residual: charge,
        photon_number_source: s[5],
        p_internal: pint,
        p_gamma: pg,
        h_kin,
        energy_residual: pint + pg + h_kin,
        event_matrix: EVENT_MATRIX,
    })
}
