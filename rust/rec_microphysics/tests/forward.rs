use rec_microphysics::coverage::{CoverageError, d86_w};
use rec_microphysics::he_singlet::{
    AngularSample, BoundBoundChannel, Complex64, Mat2, Mat3, PBoundFreeTable, SBoundFreeTable,
    SourceState, he_bb_source, he_p_bf_source, he_s_bf_source, he_two_photon_pair_source,
};
use rec_microphysics::ledger::{ChannelRates, HeEnergies, assemble_he_event_ledger};

fn c(re: f64, im: f64) -> Complex64 {
    Complex64::new(re, im)
}
fn f_zero() -> Mat2 {
    Mat2([[c(0.0, 0.0); 2]; 2])
}
fn wp_diag(a: f64, b: f64, d: f64) -> Mat3 {
    Mat3([
        [c(a, 0.0), c(0.0, 0.0), c(0.0, 0.0)],
        [c(0.0, 0.0), c(b, 0.0), c(0.0, 0.0)],
        [c(0.0, 0.0), c(0.0, 0.0), c(d, 0.0)],
    ])
}
fn octahedron() -> Vec<AngularSample> {
    AngularSample::octahedron_6()
}

#[test]
fn d86_canonical_nodes_and_outband_are_typed() {
    assert!((d86_w(0.025).unwrap() - 7.736).abs() < 1e-12);
    assert!((d86_w(0.5).unwrap() - 145.142).abs() < 1e-12);
    assert!((d86_w(0.975).unwrap() - 7.736).abs() < 1e-12);
    assert!(matches!(d86_w(0.024), Err(CoverageError::OutOfBand { .. })));
}

#[test]
fn vacuum_bound_bound_is_minus_a_wp() {
    let wp = wp_diag(1.0, 2.0, 3.0);
    let out = he_bb_source(BoundBoundChannel::He584, 0.0, wp, f_zero(), &octahedron()).unwrap();
    let a = BoundBoundChannel::He584.a_s_inv();
    for i in 0..3 {
        for j in 0..3 {
            let want = wp[i][j].scale(-a);
            assert!(out.atomic_b[i][j].approx_eq(want, 2e-6));
        }
    }
    assert!((out.event_rate - a * 6.0).abs() < 1e-5 * a.max(1.0));
}

#[test]
fn high_band_lookup_is_interpolated_and_low_missing_is_not_zero() {
    let p = PBoundFreeTable::jacobs_high_length();
    let xs = p.lookup(1.2).unwrap();
    assert!((xs.sigma_s_mb - 0.011987983616479864).abs() < 1e-12);
    assert!((xs.sigma_d_mb - 0.010059902806023145).abs() < 1e-12);
    assert!(matches!(
        p.lookup(0.8),
        Err(CoverageError::MissingAuthority { .. })
    ));
    let s = SBoundFreeTable::jacobs_high_length();
    assert!((s.lookup(1.0).unwrap() - 0.543492904604474).abs() < 1e-12);
    assert!(matches!(
        s.lookup(0.5),
        Err(CoverageError::MissingAuthority { .. })
    ));
}

#[test]
fn isotropic_p_bound_free_reduces_to_scalar_limit_and_lte_zero() {
    let t = 8000.0;
    let nplus = 2.0e7;
    let ne = 3.0e7;
    let mut state = SourceState::lte_populations(t, nplus, ne).unwrap();
    state.f = Mat2::scalar(rec_microphysics::he_singlet::planck_occupation(
        state.constants.chi_p_ev + 1.2 * state.constants.rydberg_ev,
        t,
    ));
    let e = state.constants.chi_p_ev + 1.2 * state.constants.rydberg_ev;
    let out = he_p_bf_source(e, &state, PBoundFreeTable::jacobs_high_length()).unwrap();
    let tol = 4096.0 * f64::EPSILON;
    assert!(out.photon_c.max_abs() <= tol * out.gross_scale.max(f64::MIN_POSITIVE));
    assert!(out.atomic_b.max_abs() <= tol * out.atomic_gross_scale.max(f64::MIN_POSITIVE));
}

#[test]
fn s_bound_free_lte_zero() {
    let t = 8000.0;
    let mut state = SourceState::lte_populations(t, 2.0e7, 3.0e7).unwrap();
    state.f = Mat2::scalar(rec_microphysics::he_singlet::planck_occupation(
        state.constants.chi_s_ev + 1.2 * state.constants.rydberg_ev,
        t,
    ));
    let e = state.constants.chi_s_ev + 1.2 * state.constants.rydberg_ev;
    let out = he_s_bf_source(e, &state, SBoundFreeTable::jacobs_high_length()).unwrap();
    let tol = 4096.0 * f64::EPSILON;
    assert!(out.photon_c.max_abs() <= tol * out.gross_scale.max(f64::MIN_POSITIVE));
}

#[test]
fn complex_wp_f_trace_parity_is_preserved() {
    let mut state =
        SourceState::simple(2.0, 0.7, wp_diag(0.4, 0.7, 1.1), 0.3, 0.4, 9000.0).unwrap();
    state.f = Mat2([[c(0.2, 0.0), c(0.03, 0.04)], [c(0.03, -0.04), c(0.1, 0.0)]]);
    state.wp[0][1] = c(0.05, 0.02);
    state.wp[1][0] = c(0.05, -0.02);
    let e = state.constants.chi_p_ev + 1.2 * state.constants.rydberg_ev;
    let out = he_p_bf_source(e, &state, PBoundFreeTable::jacobs_high_length()).unwrap();
    let lhs = out.atomic_b.trace().re;
    let rhs = -out.event_rate_density;
    assert!((lhs - rhs).abs() <= 1e-10 * (1.0 + lhs.abs() + rhs.abs()));
}

#[test]
fn two_photon_pair_counts_one_event_two_photons_and_lte_zero() {
    let state = SourceState::lte_populations(7000.0, 3.0e7, 3.0e7).unwrap();
    let e1 = 0.5 * state.constants.delta_s_ev;
    let f1 = Mat2::scalar(rec_microphysics::he_singlet::planck_occupation(
        e1,
        state.temperature_k,
    ));
    let out = he_two_photon_pair_source(0.5, &state, f1, f1).unwrap();
    assert!(out.pair_matrix.max_abs() < 1e-18);
    assert!(out.event_rate_density.abs() < 1e-18);
    assert_eq!(out.photon_tags_per_event, 2);
}

#[test]
fn event_ledger_conserves_nuclei_charge_photons_and_energy() {
    let rates = ChannelRates {
        r584: 2.0,
        rir: -3.0,
        rp: 5.0,
        rs: -7.0,
        r2g: 11.0,
    };
    let e = HeEnergies::canonical();
    let h_kin = -8.0;
    let bf_photon = e.chi_p * rates.rp + e.chi_s * rates.rs + h_kin;
    let l = assemble_he_event_ledger(rates, e, bf_photon, h_kin).unwrap();
    assert!(l.he_nuclei_residual.abs() < 1e-12);
    assert!(l.charge_minus_e_residual.abs() < 1e-12);
    assert!((l.photon_number_source - (2.0 - 3.0 - 5.0 + 7.0 + 22.0)).abs() < 1e-12);
    assert!((l.p_internal + l.p_gamma + l.h_kin).abs() < 1e-10);
    assert_eq!(l.event_matrix[5][4], 2);
}

#[test]
fn below_threshold_is_physical_zero_but_above_unprovided_is_missing() {
    use rec_microphysics::he_singlet::CoverageState;
    let state = SourceState::simple(1.0, 1.0, wp_diag(1.0, 1.0, 1.0), 1.0, 1.0, 9000.0).unwrap();
    let p0 = he_p_bf_source(
        state.constants.chi_p_ev - 0.01,
        &state,
        PBoundFreeTable::jacobs_high_length(),
    )
    .unwrap();
    assert_eq!(p0.coverage, CoverageState::PhysicalZeroBelowThreshold);
    let err = he_p_bf_source(
        state.constants.chi_p_ev + 1.6 * state.constants.rydberg_ev,
        &state,
        PBoundFreeTable::jacobs_high_length(),
    )
    .unwrap_err();
    assert!(matches!(err, CoverageError::MissingAuthority { .. }));
}

#[test]
fn species_drift_bound_free_is_fail_closed() {
    use rec_microphysics::he_singlet::ElectronFramePolicy;
    let mut state =
        SourceState::simple(1.0, 1.0, wp_diag(1.0, 1.0, 1.0), 1.0, 1.0, 9000.0).unwrap();
    state.electron_frame = ElectronFramePolicy::SpeciesDriftUnsupported;
    let e = state.constants.chi_p_ev + 1.2 * state.constants.rydberg_ev;
    let err = he_p_bf_source(e, &state, PBoundFreeTable::jacobs_high_length()).unwrap_err();
    assert!(matches!(
        err,
        CoverageError::MissingAuthority {
            family: "BOUND_FREE_SPECIES_DRIFT",
            ..
        }
    ));
}

#[test]
fn isotropic_p_bf_matches_scalar_formula_off_lte() {
    use rec_microphysics::he_singlet::{C_M_S, EV_J, HBAR_J_S, KB_J_K, MB_TO_M2, ME_KG};
    let np = 4.2;
    let f = 0.17;
    let mut state =
        SourceState::simple(7.0, 0.6, Mat3::scalar(np / 3.0), 2.0e7, 3.0e7, 9000.0).unwrap();
    state.f = Mat2::scalar(f);
    let q = 1.2;
    let energy = state.constants.chi_p_ev + q * state.constants.rydberg_ev;
    let table = PBoundFreeTable::jacobs_high_length();
    let xs = table.lookup(q).unwrap();
    let sigma = (xs.sigma_s_mb + xs.sigma_d_mb) * MB_TO_M2;
    let phi = (ME_KG * KB_J_K * state.temperature_k
        / (2.0 * std::f64::consts::PI * HBAR_J_S * HBAR_J_S))
        .powf(1.5);
    let eta = state.n_he_plus
        * state.ne
        * (-(energy - state.constants.chi_p_ev) * EV_J / (KB_J_K * state.temperature_k)).exp()
        / (4.0 * phi);
    let want = C_M_S * sigma * (3.0 * eta * (1.0 + f) - np * f);
    let out = he_p_bf_source(energy, &state, table).unwrap();
    assert!((out.photon_c[0][0].re - want).abs() <= 2e-13 * (1.0 + want.abs()));
    assert!((out.photon_c[1][1].re - want).abs() <= 2e-13 * (1.0 + want.abs()));
    assert!(out.photon_c[0][1].abs() < 1e-30);
}

#[test]
fn bound_bound_channels_share_wp_but_keep_distinct_line_coefficients() {
    let np = 2.4;
    let lower = 0.8;
    let f = 0.11;
    let wp = Mat3::scalar(np / 3.0);
    let fm = Mat2::scalar(f);
    let stencil = octahedron();
    for channel in [BoundBoundChannel::He584, BoundBoundChannel::IrPToS] {
        let out = he_bb_source(channel, lower, wp, fm, &stencil).unwrap();
        let want = channel.a_s_inv() * (np * (1.0 + f) - 3.0 * lower * f);
        assert!((out.event_rate - want).abs() <= 2e-13 * (1.0 + want.abs()));
        assert!(out.spectral.shell_integrated);
        assert!((out.spectral.energy_ev - channel.energy_ev()).abs() < 1e-14);
    }
}

#[test]
fn bound_bound_lte_zero_for_both_represented_lines() {
    let temperature_k = 7600.0;
    let state = SourceState::lte_populations(temperature_k, 2.0e7, 3.0e7).unwrap();
    let stencil = octahedron();
    for (channel, lower) in [
        (BoundBoundChannel::He584, state.ng),
        (BoundBoundChannel::IrPToS, state.ns),
    ] {
        let f = Mat2::scalar(rec_microphysics::he_singlet::planck_occupation(
            channel.energy_ev(),
            temperature_k,
        ));
        let out = he_bb_source(channel, lower, state.wp, f, &stencil).unwrap();
        let scale = channel.a_s_inv() * (1.0 + state.wp.max_abs() + lower);
        assert!(out.atomic_b.max_abs() / scale.max(f64::MIN_POSITIVE) < 4096.0 * f64::EPSILON);
        assert!(out.event_rate.abs() / scale.max(f64::MIN_POSITIVE) < 4096.0 * f64::EPSILON);
    }
}

#[test]
fn two_photon_atomic_event_uses_one_unordered_half_factor() {
    let mut state =
        SourceState::simple(1.3, 2.1, wp_diag(0.2, 0.3, 0.4), 0.0, 0.0, 8000.0).unwrap();
    let f1 = Mat2::scalar(0.2);
    let f2 = Mat2::scalar(0.4);
    state.f = f1;
    let y = 0.25;
    let out = he_two_photon_pair_source(y, &state, f1, f2).unwrap();
    let g_ang = 3.0 / (64.0 * std::f64::consts::PI * std::f64::consts::PI);
    let want = 0.5 * out.w_s_inv * g_ang * out.pair_matrix.trace().re;
    assert!((out.event_rate_density - want).abs() <= 16.0 * f64::EPSILON * (1.0 + want.abs()));
    assert_eq!(out.atom_pair_factor, 0.5);
    assert_eq!(out.photon_tags_per_event, 2);
    assert!((out.atomic_event_weight_s_inv - 0.5 * out.w_s_inv * g_ang).abs() < 1e-15);
    assert!((out.photon_marginal_weight_s_inv - out.w_s_inv * g_ang).abs() < 1e-15);
    assert!((out.photon_marginal_weight_s_inv - 2.0 * out.atomic_event_weight_s_inv).abs() < 1e-15);
}

#[test]
fn directly_mutated_invalid_densities_fail_closed_at_public_sources() {
    let mut bf = SourceState::simple(1.0, 1.0, wp_diag(1.0, 1.0, 1.0), 1.0, 1.0, 9000.0).unwrap();
    bf.ne = -1.0;
    let e = bf.constants.chi_p_ev + 1.2 * bf.constants.rydberg_ev;
    assert!(matches!(
        he_p_bf_source(e, &bf, PBoundFreeTable::jacobs_high_length()),
        Err(CoverageError::InvalidInput(_))
    ));

    let mut pair = SourceState::simple(1.0, 1.0, wp_diag(1.0, 1.0, 1.0), 0.0, 0.0, 9000.0).unwrap();
    pair.ns = -1.0;
    assert!(matches!(
        he_two_photon_pair_source(0.5, &pair, Mat2::zero(), Mat2::zero()),
        Err(CoverageError::InvalidInput(_))
    ));
}
