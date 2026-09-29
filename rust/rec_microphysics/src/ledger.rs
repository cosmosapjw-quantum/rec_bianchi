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
    /// Existing ledger scalars use a caller-consistent energy unit (canonical: eV).
    /// canonical_si() and the new material-moment API use explicit SI instead.
    pub fn validate(self) -> Result<(), CoverageError> {
        let values = [
            self.delta_s,
            self.delta_p,
            self.epsilon_ir,
            self.chi_p,
            self.chi_s,
        ];
        if values.iter().any(|x| !x.is_finite() || *x <= 0.0) {
            return Err(CoverageError::InvalidInput(
                "ledger energies must be positive and finite",
            ));
        }
        let tol = crate::he_singlet::PSD_MINOR_TOLERANCE;
        let scale = self.delta_p.max(self.delta_s).max(self.epsilon_ir);
        if (self.delta_p / scale - self.delta_s / scale - self.epsilon_ir / scale).abs() > tol {
            return Err(CoverageError::InvalidInput(
                "inconsistent ledger excitation cycle",
            ));
        }
        let scale = values.into_iter().fold(0.0_f64, f64::max);
        if (self.delta_p / scale + self.chi_p / scale - self.delta_s / scale - self.chi_s / scale)
            .abs()
            > tol
        {
            return Err(CoverageError::InvalidInput(
                "inconsistent ledger ionization cycle",
            ));
        }
        Ok(())
    }

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
    e.validate()?;
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

// Task 5: selected finite-support, material-frame moments. No normal-frame boost,
// expansion, escape probability, species force partition, or recoil closure.
use crate::he_singlet::{
    BoundBoundChannel, C_M_S, Complex64, CoverageState, EV_J, H_J_S, Mat2, Mat3, PBoundFreeTable,
    PairAssemblyOutput, PairGridConvention, RealV, SBoundFreeTable, SourceState, WeightedBbMode,
    WeightedPairMode, assemble_he_pair_grid, he_bb_kernel, he_p_bf_source, he_s_bf_source,
    he_two_photon_pair_source, material_energy_j, validate_screen,
};

impl HeEnergies {
    /// SI registry for the new material ledger. Legacy canonical() remains eV.
    pub fn canonical_si() -> Self {
        Self::from_constants_si(HeConstants::canonical())
    }

    fn from_constants_si(c: HeConstants) -> Self {
        Self {
            delta_s: c.delta_s_ev * EV_J,
            delta_p: c.delta_p_ev * EV_J,
            epsilon_ir: c.epsilon_ir_ev * EV_J,
            chi_p: c.chi_p_ev * EV_J,
            chi_s: c.chi_s_ev * EV_J,
        }
    }
}

#[derive(Clone, Copy, Debug)]
pub enum BfChannel {
    P(PBoundFreeTable),
    S(SBoundFreeTable),
}

/// A finite quadrature mode. Energy query is eV; integration weight is J.
/// The table handle owns BOTH directions of this channel. No model splice.
#[derive(Clone, Copy, Debug)]
pub struct WeightedBfMode {
    pub channel: BfChannel,
    pub energy_ev: f64,
    pub f: Mat2,
    pub v: RealV,
    pub direction: [f64; 3],
    pub weight_energy_j: f64,
    pub weight_omega_sr: f64,
}

#[derive(Clone, Copy, Debug)]
pub struct DirectedBbMode {
    pub mode: WeightedBbMode,
    pub direction: [f64; 3],
}

#[derive(Clone, Copy, Debug)]
pub struct DirectedPairMode {
    pub mode: WeightedPairMode,
    pub direction1: [f64; 3],
    pub direction2: [f64; 3],
}

/// Signed moments per material proper m^3 and proper second.
#[derive(Clone, Copy, Debug, Default)]
pub struct MaterialPhotonMoments {
    pub number_rate: f64,
    /// J m^-3 s^-1, positive for photon emission.
    pub energy_rate_j: f64,
    /// kg m^-2 s^-2 = N m^-3, positive along photon momentum gain.
    pub momentum_rate: [f64; 3],
    /// Sums of absolute NET per-node contributions; not independent oracle scales.
    pub number_gross: f64,
    pub energy_gross_j: f64,
}

/// Contravariant orthonormal material-tetrad components (P/c, momentum rate).
/// u=(1,0,0,0), g=(-,+,+,+). Opposite signs are imposed by the event ledger;
/// scalar/moment parity is a separate diagnostic, not implied by this definition.
#[derive(Clone, Copy, Debug)]
pub struct MaterialFourForce {
    pub q_photon: [f64; 4],
    pub q_matter: [f64; 4],
}

fn finite(value: f64, quantity: &'static str) -> Result<f64, CoverageError> {
    if !value.is_finite() {
        return Err(CoverageError::NumericalDomainUncertain {
            quantity,
            value,
            detail: "nonfinite material-moment arithmetic",
        });
    }
    Ok(value)
}

fn product(a: f64, b: f64, quantity: &'static str) -> Result<f64, CoverageError> {
    let value = finite(a * b, quantity)?;
    if a != 0.0 && b != 0.0 && value == 0.0 {
        return Err(CoverageError::NumericalDomainUncertain {
            quantity,
            value,
            detail: "nonzero moment factor underflowed; not a physical zero",
        });
    }
    Ok(value)
}

fn weight(value: f64, name: &'static str) -> Result<(), CoverageError> {
    if !value.is_finite() || value < 0.0 {
        return Err(CoverageError::InvalidInput(name));
    }
    Ok(())
}

fn add(target: &mut f64, increment: f64, name: &'static str) -> Result<(), CoverageError> {
    *target = finite(*target + increment, name)?;
    Ok(())
}

fn add_matrix(target: &mut Mat3, source: Mat3, w: f64) -> Result<(), CoverageError> {
    for i in 0..3 {
        for j in 0..3 {
            add(
                &mut target[i][j].re,
                product(source[i][j].re, w, "atomic real moment")?,
                "atomic real sum",
            )?;
            add(
                &mut target[i][j].im,
                product(source[i][j].im, w, "atomic imaginary moment")?,
                "atomic imaginary sum",
            )?;
        }
    }
    Ok(())
}

impl MaterialPhotonMoments {
    fn add_photons(&mut self, n: f64, energy_j: f64, e: [f64; 3]) -> Result<(), CoverageError> {
        let power = product(energy_j, n, "photon power moment")?;
        add(&mut self.number_rate, n, "photon number sum")?;
        add(&mut self.energy_rate_j, power, "photon energy sum")?;
        add(
            &mut self.number_gross,
            n.abs(),
            "photon net-number gross sum",
        )?;
        add(
            &mut self.energy_gross_j,
            power.abs(),
            "photon net-energy gross sum",
        )?;
        let momentum = product(power, 1.0 / C_M_S, "photon momentum")?;
        for (k, direction) in e.into_iter().enumerate() {
            add(
                &mut self.momentum_rate[k],
                product(momentum, direction, "directional photon momentum")?,
                "momentum sum",
            )?;
        }
        Ok(())
    }

    pub fn four_force(self) -> Result<MaterialFourForce, CoverageError> {
        finite(self.number_rate, "photon number")?;
        finite(self.energy_rate_j, "photon power")?;
        let q0 = product(
            self.energy_rate_j,
            1.0 / C_M_S,
            "photon force time component",
        )?;
        let q = [
            q0,
            self.momentum_rate[0],
            self.momentum_rate[1],
            self.momentum_rate[2],
        ];
        for x in q {
            finite(x, "photon force component")?;
        }
        Ok(MaterialFourForce {
            q_photon: q,
            q_matter: q.map(|x| -x),
        })
    }
}

#[derive(Clone, Copy, Debug)]
pub struct BfAssemblyOutput {
    /// Net ionization rates [P,S], m^-3 s^-1. Negative inverse rates are retained.
    pub rates: [f64; 2],
    pub atomic_p: Mat3,
    pub atomic_s: f64,
    /// Computed from occupation sources, not assigned from -rates.
    pub photon: MaterialPhotonMoments,
    /// integral E*j_i dE_J dOmega; positive for photon energy removal.
    pub absorbed_photon_power_j: f64,
    /// integral chi_i*j_i dE_J dOmega.
    pub internal_power_j: f64,
    /// integral (E-chi_i)*j_i dE_J dOmega, NOT a conservation residual.
    pub heat_power_j: f64,
    pub event_gross: [f64; 2],
    pub represented_nodes: usize,
    pub physical_zero_nodes: usize,
    pub atomic_p_trace_residual: Complex64,
    pub atomic_s_residual: f64,
}

/// Assemble only supplied BF contributions. An empty slice is the empty sum,
/// NOT a claim that the omitted spectrum or channel has zero physical source.
/// All nodes are validated/evaluated even if their quadrature weight is zero.
pub fn assemble_he_bf_grid(
    state: &SourceState,
    nodes: &[WeightedBfMode],
) -> Result<BfAssemblyOutput, CoverageError> {
    state.validate()?;
    let mut out = BfAssemblyOutput {
        rates: [0.0; 2],
        atomic_p: Mat3::zero(),
        atomic_s: 0.0,
        photon: MaterialPhotonMoments::default(),
        absorbed_photon_power_j: 0.0,
        internal_power_j: 0.0,
        heat_power_j: 0.0,
        event_gross: [0.0; 2],
        represented_nodes: 0,
        physical_zero_nodes: 0,
        atomic_p_trace_residual: Complex64::new(0.0, 0.0),
        atomic_s_residual: 0.0,
    };
    let ag = 1.0 / (H_J_S * C_M_S).powi(3);
    for node in nodes {
        weight(
            node.weight_energy_j,
            "BF weight must be finite nonnegative joules",
        )?;
        weight(
            node.weight_omega_sr,
            "BF angular weight must be finite nonnegative sr",
        )?;
        validate_screen(node.v, Some(node.direction))?;
        let energy_j = material_energy_j(node.energy_ev)?;
        let mut local = *state;
        local.f = node.f;
        local.v = node.v;
        let measure = product(node.weight_energy_j, node.weight_omega_sr, "BF dE_J dOmega")?;
        let (idx, chi_ev, j, cph, coverage) = match node.channel {
            BfChannel::P(table) => {
                let src = he_p_bf_source(node.energy_ev, &local, table)?;
                add_matrix(&mut out.atomic_p, src.atomic_b, measure)?;
                (
                    0,
                    state.constants.chi_p_ev,
                    src.event_rate_density,
                    src.photon_c,
                    src.coverage,
                )
            }
            BfChannel::S(table) => {
                let src = he_s_bf_source(node.energy_ev, &local, table)?;
                add(
                    &mut out.atomic_s,
                    product(src.atomic_s_density, measure, "S atomic contribution")?,
                    "S atomic sum",
                )?;
                (
                    1,
                    state.constants.chi_s_ev,
                    src.event_rate_density,
                    src.photon_c,
                    src.coverage,
                )
            }
        };
        match coverage {
            CoverageState::Represented => out.represented_nodes += 1,
            CoverageState::PhysicalZeroBelowThreshold => out.physical_zero_nodes += 1,
        }
        let event = product(j, measure, "BF integrated signed event")?;
        add(&mut out.rates[idx], event, "BF signed event sum")?;
        add(
            &mut out.event_gross[idx],
            event.abs(),
            "BF net-event gross sum",
        )?;
        // Independent material terms use event density, its threshold and energy.
        add(
            &mut out.absorbed_photon_power_j,
            product(energy_j, event, "BF removed power")?,
            "BF removed power sum",
        )?;
        let chi_j = material_energy_j(chi_ev)?;
        add(
            &mut out.internal_power_j,
            product(chi_j, event, "BF internal power")?,
            "BF internal power sum",
        )?;
        // E-chi is in eV here; convert ONCE. No positivity guard on signed heat.
        let kinetic_j = product(node.energy_ev - chi_ev, EV_J, "BF kinetic energy in J")?;
        add(
            &mut out.heat_power_j,
            product(kinetic_j, event, "BF signed heat")?,
            "BF heat sum",
        )?;
        // Independent photon trace path, not n=-event nor power=-removed_power.
        let phase = product(ag, product(energy_j, energy_j, "BF E^2")?, "BF a_gamma E^2")?;
        let number = product(
            product(phase, cph.trace().re, "BF photon density")?,
            measure,
            "BF photon quadrature",
        )?;
        out.photon.add_photons(number, energy_j, node.direction)?;
    }
    out.atomic_p_trace_residual = out.atomic_p.trace() + Complex64::new(out.rates[0], 0.0);
    out.atomic_s_residual = finite(out.atomic_s + out.rates[1], "S trace residual")?;
    finite(out.atomic_p_trace_residual.re, "P trace real residual")?;
    finite(out.atomic_p_trace_residual.im, "P trace imaginary residual")?;
    Ok(out)
}

#[derive(Clone, Copy, Debug)]
pub struct SelectedHeMaterialLedger {
    pub rates: ChannelRates,
    /// Legacy event matrix assembler evaluated with EXPLICIT SI HeEnergies.
    pub ledger_si: HeEventLedger,
    pub bf: BfAssemblyOutput,
    pub atomic_p: Mat3,
    pub atomic_s: f64,
    pub photon: MaterialPhotonMoments,
    pub force: MaterialFourForce,
    pub pair: Option<PairAssemblyOutput>,
    pub photon_number_residual: f64,
    pub photon_energy_residual_j: f64,
    pub atomic_p_trace_residual: Complex64,
    pub atomic_s_residual: f64,
    pub energy_residual_j: f64,
    pub matter_energy_force_residual_j: f64,
}

fn require_canonical_registry(c: HeConstants) -> Result<(), CoverageError> {
    c.validate()?;
    let reference = HeConstants::canonical();
    let fields = |x: HeConstants| {
        [
            x.delta_s_ev,
            x.delta_p_ev,
            x.i_he_ev,
            x.epsilon_ir_ev,
            x.chi_p_ev,
            x.chi_s_ev,
            x.rydberg_ev,
        ]
    };
    if fields(c) != fields(reference) {
        return Err(CoverageError::InvalidInput(
            "combined selected-He ledger requires the canonical single-owner energy registry",
        ));
    }
    Ok(())
}

/// Source-level assembly on caller-supplied finite support. Empty channel slices
/// OMIT contributions by explicit caller choice; they do not fill missing bands.
/// BB/pair recoil heat is absent at the adopted heavy-atom order, but momentum
/// transfer is retained. BF j>0 means ionization. No accepted history is evolved.
/// Combined assembly is restricted to canonical constants because BB lines own
/// canonical energies. Standalone BF keeps its prior consistent-input contract.
pub fn assemble_selected_he_material_ledger(
    state: &SourceState,
    bb584: &[DirectedBbMode],
    ir: &[DirectedBbMode],
    bf: &[WeightedBfMode],
    pairs: &[DirectedPairMode],
    convention: PairGridConvention,
) -> Result<SelectedHeMaterialLedger, CoverageError> {
    state.validate()?;
    require_canonical_registry(state.constants)?;
    if bb584.is_empty() && ir.is_empty() && bf.is_empty() && pairs.is_empty() {
        return Err(CoverageError::InvalidInput(
            "no selected source support supplied",
        ));
    }
    let bf_out = assemble_he_bf_grid(state, bf)?;
    let mut photon = bf_out.photon;
    let mut atomic_p = bf_out.atomic_p;
    let mut atomic_s = bf_out.atomic_s;
    let mut rates = ChannelRates {
        r584: 0.0,
        rir: 0.0,
        rp: bf_out.rates[0],
        rs: bf_out.rates[1],
        r2g: 0.0,
    };
    let ag = 1.0 / (H_J_S * C_M_S).powi(3);
    for (channel, lower, nodes) in [
        (BoundBoundChannel::He584, state.ng, bb584),
        (BoundBoundChannel::IrPToS, state.ns, ir),
    ] {
        for node in nodes {
            validate_screen(node.mode.v, Some(node.direction))?;
            weight(
                node.mode.weight_sr,
                "BB angular weight must be finite nonnegative",
            )?;
            let k = he_bb_kernel(channel, lower, state.wp, node.mode.f, node.mode.v)?;
            let w = node.mode.weight_sr;
            let r = product(k.event_rate_per_sr, w, "BB event quadrature")?;
            add_matrix(&mut atomic_p, k.atomic_b_shell, w)?;
            match channel {
                BoundBoundChannel::He584 => add(&mut rates.r584, r, "584 event sum")?,
                BoundBoundChannel::IrPToS => {
                    add(&mut rates.rir, r, "IR event sum")?;
                    add(
                        &mut atomic_s,
                        product(-k.atomic_b_shell.trace().re, w, "IR lower source")?,
                        "S source sum",
                    )?;
                }
            }
            // Integrate delta_J once, then use C_shell to recover photon moment.
            let energy_j = material_energy_j(channel.energy_ev())?;
            let phase = product(
                ag,
                product(energy_j, energy_j, "BB energy squared")?,
                "BB mode factor",
            )?;
            let n = product(
                product(
                    phase,
                    k.occupation_c_shell.trace().re,
                    "BB shell photon trace",
                )?,
                w,
                "BB angular photons",
            )?;
            photon.add_photons(n, energy_j, node.direction)?;
        }
    }
    let mut pair_out = None;
    if !pairs.is_empty() {
        let modes: Vec<WeightedPairMode> = pairs.iter().map(|p| p.mode).collect();
        // Original Task4 owner validates weights, fields, coverage and exchange.
        let pair = assemble_he_pair_grid(state, &modes, convention)?;
        for node in pairs {
            validate_screen(node.mode.input.v1, Some(node.direction1))?;
            validate_screen(node.mode.input.v2, Some(node.direction2))?;
            let partner = &pairs[node.mode.exchange_partner]; // upstream index check
            if partner.direction1 != node.direction2 || partner.direction2 != node.direction1 {
                return Err(CoverageError::InvalidInput(
                    "pair directions do not follow exchange map",
                ));
            }
            let k = he_two_photon_pair_source(&node.mode.input, state)?;
            let d_omega = product(
                node.mode.weight_omega1_sr,
                node.mode.weight_omega2_sr,
                "pair angular measure",
            )?;
            let de = product(k.delta_s_j, node.mode.weight_dy, "pair dE_J=DeltaS_J dy")?;
            let measure = product(de, d_omega, "pair photon measure")?;
            let phase = product(
                ag,
                product(k.energy1_j, k.energy1_j, "pair E1 squared")?,
                "pair mode factor",
            )?;
            let n = product(
                product(
                    phase,
                    k.tagged_c1_per_partner_sr.trace().re,
                    "pair first-tag density",
                )?,
                measure,
                "pair first-tag number",
            )?;
            // Full ordered grid: the complete tag-1 marginal is the physical
            // photon moment. DO NOT add the full tag-2 moment a second time.
            photon.add_photons(n, k.energy1_j, node.direction1)?;
        }
        rates.r2g = pair.event_rate; // already integrated, with atomic 1/2 ONCE
        add(&mut atomic_s, -pair.event_rate, "two-photon S source")?;
        pair_out = Some(pair);
    }
    let ledger = assemble_he_event_ledger(
        rates,
        HeEnergies::canonical_si(),
        bf_out.absorbed_photon_power_j,
        bf_out.heat_power_j,
    )?;
    for x in ledger.species_source {
        finite(x, "species source")?;
    }
    for x in [
        ledger.p_internal,
        ledger.p_gamma,
        ledger.h_kin,
        ledger.energy_residual,
    ] {
        finite(x, "SI event ledger")?;
    }
    let force = photon.four_force()?;
    let p_residual = atomic_p.trace() - Complex64::new(ledger.species_source[2], 0.0);
    finite(p_residual.re, "selected P trace residual")?;
    finite(p_residual.im, "selected P trace imaginary residual")?;
    Ok(SelectedHeMaterialLedger {
        rates,
        ledger_si: ledger,
        bf: bf_out,
        atomic_p,
        atomic_s,
        photon,
        force,
        pair: pair_out,
        photon_number_residual: finite(
            photon.number_rate - ledger.photon_number_source,
            "photon number closure",
        )?,
        photon_energy_residual_j: finite(
            photon.energy_rate_j - ledger.p_gamma,
            "photon energy parity",
        )?,
        atomic_p_trace_residual: p_residual,
        atomic_s_residual: finite(atomic_s - ledger.species_source[1], "S source parity")?,
        energy_residual_j: finite(
            ledger.p_internal + photon.energy_rate_j + bf_out.heat_power_j,
            "independent energy closure",
        )?,
        matter_energy_force_residual_j: finite(
            ledger.p_internal + bf_out.heat_power_j - C_M_S * force.q_matter[0],
            "matter internal plus kinetic energy/force",
        )?,
    })
}
