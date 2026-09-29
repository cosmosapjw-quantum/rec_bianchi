use rec_microphysics::he_singlet::{WeightedPairMode, PairGridConvention, assemble_he_pair_grid};
use rec_microphysics::coverage::{CoverageError, d86_w};
use rec_microphysics::he_singlet::{
    AngularSample, BoundBoundChannel, Complex64, Mat2, Mat3, PBoundFreeTable, SBoundFreeTable,
    SourceState, PairInput, WeightedBbMode, he_bb_kernel, he_bb_source, he_p_bf_source, he_s_bf_source, he_two_photon_pair_source,
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
    let out = he_bb_source(BoundBoundChannel::He584, 0.0, wp, &bb_modes_for_fixture(f_zero(), &octahedron())).unwrap();
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
    let out = he_two_photon_pair_source(&same_screen_pair(0.5, f1, f1), &state).unwrap();
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
        let out = he_bb_source(channel, lower, wp, &bb_modes_for_fixture(fm, &stencil)).unwrap();
        let want = channel.a_s_inv() * (np * (1.0 + f) - 3.0 * lower * f);
        assert!((out.event_rate - want).abs() <= 2e-13 * (1.0 + want.abs()));
        assert_eq!(out.spectral, rec_microphysics::he_singlet::SpectralMeasure::SharpLineDeltaPerJoule { energy_ev: channel.energy_ev() });
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
        let out = he_bb_source(channel, lower, state.wp, &bb_modes_for_fixture(f, &stencil)).unwrap();
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
    let out = he_two_photon_pair_source(&same_screen_pair(y, f1, f2), &state).unwrap();
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
        he_two_photon_pair_source(&same_screen_pair(0.5, Mat2::zero(), Mat2::zero()), &pair),
        Err(CoverageError::InvalidInput(_))
    ));
}

// Task 2 preregistered domain tests. Written before the guard changes.
// These tests must be compiled and run by local Codex, not this web work unit.
fn task2_state() -> SourceState {
    let mut s = SourceState::simple(2.0, 0.7, wp_diag(0.4, 0.7, 1.1), 0.3, 0.4, 9000.0).unwrap();
    s.f = Mat2([[c(0.2, 0.0), c(0.03, 0.04)], [c(0.03, -0.04), c(0.1, 0.0)]]);
    s.wp[0][1] = c(0.05, 0.02);
    s.wp[1][0] = c(0.05, -0.02);
    s
}

#[test]
fn reject_nonfinite_public_inputs() {
    use rec_microphysics::he_singlet::planck_occupation;
    for bad in [f64::NAN, f64::INFINITY, f64::NEG_INFINITY] {
        for index in 0..5 {
            let mut s = task2_state();
            match index {
                0 => s.ng = bad,
                1 => s.ns = bad,
                2 => s.n_he_plus = bad,
                3 => s.ne = bad,
                _ => s.temperature_k = bad,
            }
            let ep = s.constants.chi_p_ev + 1.2 * s.constants.rydberg_ev;
            let es = s.constants.chi_s_ev + 1.2 * s.constants.rydberg_ev;
            assert!(matches!(he_p_bf_source(ep, &s, PBoundFreeTable::jacobs_high_length()), Err(CoverageError::InvalidInput(_))));
            assert!(matches!(he_s_bf_source(es, &s, SBoundFreeTable::jacobs_high_length()), Err(CoverageError::InvalidInput(_))));
            assert!(matches!(he_two_photon_pair_source(&same_screen_pair(0.5, s.f, s.f), &s), Err(CoverageError::InvalidInput(_))));
        }
        let s = task2_state();
        for axis in 0..2 {
            let mut f = s.f;
            if axis == 0 { f[0][0].re = bad; } else { f[0][0].im = bad; }
            assert!(matches!(he_bb_source(BoundBoundChannel::He584, s.ng, s.wp, &bb_modes_for_fixture(f, &octahedron())), Err(CoverageError::InvalidInput(_))));
            assert!(matches!(he_two_photon_pair_source(&same_screen_pair(0.5, f, s.f), &s), Err(CoverageError::InvalidInput(_))));
            assert!(!f.is_hermitian(1e-12));
        }
        assert!(planck_occupation(bad, 9000.0).is_nan());
        assert!(planck_occupation(1.0, bad).is_nan());
    }
    assert!(SourceState::lte_populations(0.0, 1.0, 1.0).is_err());
    assert!(SourceState::lte_populations(-1.0, 1.0, 1.0).is_err());
}

#[test]
fn reject_non_psd_input() {
    let s = task2_state();
    for scale in [1e-280, 1.0, 1e280] {
        let f = Mat2([[c(-scale, 0.0), c(0.0, 0.0)], [c(0.0, 0.0), c(scale, 0.0)]]);
        let w = wp_diag(-scale, scale, scale);
        assert!(matches!(f.validate_occupation(), Err(CoverageError::InvalidInput(_))));
        assert!(matches!(w.validate_population(), Err(CoverageError::InvalidInput(_))));
        assert!(he_bb_source(BoundBoundChannel::He584, 1.0, s.wp, &bb_modes_for_fixture(f, &octahedron())).is_err());
        assert!(he_bb_source(BoundBoundChannel::He584, 1.0, w, &bb_modes_for_fixture(s.f, &octahedron())).is_err());
        assert!(he_two_photon_pair_source(&same_screen_pair(0.5, s.f, f), &s).is_err());
    }
    // Positive diagonal AND positive 2x2 principal minors, but negative 3x3 determinant.
    let w = Mat3([[c(1.0, 0.0), c(-0.9, 0.0), c(-0.9, 0.0)],
                  [c(-0.9, 0.0), c(1.0, 0.0), c(-0.9, 0.0)],
                  [c(-0.9, 0.0), c(-0.9, 0.0), c(1.0, 0.0)]]);
    assert!(matches!(w.validate_population(), Err(CoverageError::InvalidInput(_))));
    let s_bad = SourceState::simple(1.0, 1.0, w, 0.0, 0.0, 9000.0);
    assert!(matches!(s_bad, Err(CoverageError::InvalidInput(_))));
}

#[test]
fn roundoff_psd_boundary_is_uncertain() {
    use rec_microphysics::he_singlet::PSD_MINOR_TOLERANCE;
    for eps in [PSD_MINOR_TOLERANCE / 4.0, PSD_MINOR_TOLERANCE] {
        let w = wp_diag(-eps, 1.0, 1.0);
        let before = w;
        assert!(matches!(w.validate_population(), Err(CoverageError::NumericalDomainUncertain { .. })));
        assert_eq!(w, before);
    }
    assert!(matches!(wp_diag(-PSD_MINOR_TOLERANCE / 4.0, -1.0, 1.0).validate_population(), Err(CoverageError::InvalidInput(_))));
    assert!(Mat2::zero().validate_occupation().is_ok());
    assert!(Mat3::zero().validate_population().is_ok());
}

#[test]
fn reject_nonorthonormal_screen() {
    use rec_microphysics::he_singlet::validate_screen;
    let s = task2_state();
    for v in [[[2.0, 0.0], [0.0, 2.0], [0.0, 0.0]],
              [[0.0, 0.0]; 3],
              [[1.0, 1.0], [0.0, 0.0], [0.0, 0.0]],
              [[f64::INFINITY, 0.0], [0.0, 1.0], [0.0, 0.0]]] {
        let mut bf = s; bf.v = v;
        assert!(matches!(bf.validate(), Err(CoverageError::InvalidInput(_))));
        assert!(he_p_bf_source(bf.constants.chi_p_ev + bf.constants.rydberg_ev, &bf, PBoundFreeTable::jacobs_high_length()).is_err());
        let mode = AngularSample { v, weight_sr: 1.0 };
        assert!(he_bb_source(BoundBoundChannel::He584, s.ng, s.wp, &bb_modes_for_fixture(s.f, &[mode])).is_err());
    }
    assert!(validate_screen(s.v, Some([0.0, 0.0, 1.0])).is_ok());
    assert!(validate_screen(s.v, Some([1.0, 0.0, 0.0])).is_err());
    assert!(validate_screen(s.v, Some([0.0, 0.0, 2.0])).is_err());
}

#[test]
fn reject_inconsistent_or_nonfinite_constants() {
    use rec_microphysics::he_singlet::HeConstants;
    assert!(HeConstants::canonical().validate().is_ok());
    for index in 0..7 {
        for bad in [0.0, -1.0, f64::NAN, f64::INFINITY] {
            let mut s = task2_state();
            match index {
                0 => s.constants.delta_s_ev = bad,
                1 => s.constants.delta_p_ev = bad,
                2 => s.constants.i_he_ev = bad,
                3 => s.constants.epsilon_ir_ev = bad,
                4 => s.constants.chi_p_ev = bad,
                5 => s.constants.chi_s_ev = bad,
                _ => s.constants.rydberg_ev = bad,
            }
            assert!(matches!(s.validate(), Err(CoverageError::InvalidInput(_))));
            assert!(he_s_bf_source(20.0, &s, SBoundFreeTable::jacobs_high_length()).is_err());
            assert!(he_two_photon_pair_source(&same_screen_pair(0.5, s.f, s.f), &s).is_err());
        }
    }
    let mut s = task2_state(); s.constants.chi_p_ev += 0.25;
    assert!(matches!(s.validate(), Err(CoverageError::InvalidInput(_))));
}

#[test]
fn bf_zero_vs_missing_vs_invalid() {
    use rec_microphysics::he_singlet::CoverageState;
    let s = task2_state();
    for bad in [-1.0, 0.0, f64::NAN, f64::INFINITY, f64::NEG_INFINITY] {
        assert!(matches!(he_p_bf_source(bad, &s, PBoundFreeTable::jacobs_high_length()), Err(CoverageError::InvalidInput(_))));
        assert!(matches!(he_s_bf_source(bad, &s, SBoundFreeTable::jacobs_high_length()), Err(CoverageError::InvalidInput(_))));
    }
    let p0 = he_p_bf_source(s.constants.chi_p_ev / 2.0, &s, PBoundFreeTable::jacobs_high_length()).unwrap();
    let s0 = he_s_bf_source(s.constants.chi_s_ev / 2.0, &s, SBoundFreeTable::jacobs_high_length()).unwrap();
    assert_eq!(p0.coverage, CoverageState::PhysicalZeroBelowThreshold);
    assert_eq!(s0.coverage, CoverageState::PhysicalZeroBelowThreshold);
    assert_eq!(p0.event_rate_density, 0.0);
    assert_eq!(s0.event_rate_density, 0.0);
    for q in [0.0, 0.8, 1.6] {
        assert!(matches!(he_p_bf_source(s.constants.chi_p_ev + q * s.constants.rydberg_ev, &s, PBoundFreeTable::jacobs_high_length()), Err(CoverageError::MissingAuthority { .. })));
        assert!(matches!(he_s_bf_source(s.constants.chi_s_ev + q * s.constants.rydberg_ev, &s, SBoundFreeTable::jacobs_high_length()), Err(CoverageError::MissingAuthority { .. })));
    }
}

#[test]
fn jacobs_energy_endpoint_roundtrip() {
    use rec_microphysics::he_singlet::CoverageState;
    let s = task2_state();
    for q in [1.0, 1.2, 1.4] {
        for table in [PBoundFreeTable::jacobs_high_length(), PBoundFreeTable::jacobs_high_velocity()] {
            assert_eq!(he_p_bf_source(s.constants.chi_p_ev + q * s.constants.rydberg_ev, &s, table).unwrap().coverage, CoverageState::Represented);
        }
        for table in [SBoundFreeTable::jacobs_high_length(), SBoundFreeTable::jacobs_high_velocity()] {
            assert_eq!(he_s_bf_source(s.constants.chi_s_ev + q * s.constants.rydberg_ev, &s, table).unwrap().coverage, CoverageState::Represented);
        }
    }
    let plo = s.constants.chi_p_ev + s.constants.rydberg_ev;
    let phi = s.constants.chi_p_ev + 1.4 * s.constants.rydberg_ev;
    let slo = s.constants.chi_s_ev + s.constants.rydberg_ev;
    let shi = s.constants.chi_s_ev + 1.4 * s.constants.rydberg_ev;
    for e in [plo.next_down(), phi.next_up()] {
        assert!(matches!(he_p_bf_source(e, &s, PBoundFreeTable::jacobs_high_length()), Err(CoverageError::MissingAuthority { .. })));
    }
    for e in [slo.next_down(), shi.next_up()] {
        assert!(matches!(he_s_bf_source(e, &s, SBoundFreeTable::jacobs_high_length()), Err(CoverageError::MissingAuthority { .. })));
    }
    assert!(PBoundFreeTable::jacobs_high_length().lookup(1.0_f64.next_down()).is_err());
    assert!(SBoundFreeTable::jacobs_high_length().lookup(1.4_f64.next_up()).is_err());
}

#[test]
fn energy_and_width_measures_are_explicit() {
    use rec_microphysics::he_singlet::{material_energy_j, energy_width_j, SpectralMeasure, EV_J};
    assert_eq!(material_energy_j(1.0).unwrap(), EV_J);
    assert_eq!(energy_width_j(0.25).unwrap(), 0.25 * EV_J);
    assert_eq!(energy_width_j(0.0).unwrap(), 0.0);
    assert!(energy_width_j(-1.0).is_err());
    assert!(matches!(energy_width_j(f64::from_bits(1)), Err(CoverageError::NumericalDomainUncertain { .. })));
    let s = task2_state();
    let p = he_p_bf_source(s.constants.chi_p_ev + s.constants.rydberg_ev, &s, PBoundFreeTable::jacobs_high_length()).unwrap();
    let sf = he_s_bf_source(s.constants.chi_s_ev + s.constants.rydberg_ev, &s, SBoundFreeTable::jacobs_high_length()).unwrap();
    assert_eq!(p.density_measure, SpectralMeasure::ContinuousPerJoulePerSteradian);
    assert_eq!(sf.density_measure, SpectralMeasure::ContinuousPerJoulePerSteradian);
}

#[test]
fn signed_sources_are_not_projected() {
    let s = SourceState::simple(10.0, 0.0, Mat3::identity(), 0.0, 0.0, 9000.0).unwrap();
    let bb = he_bb_source(BoundBoundChannel::He584, 0.0, s.wp, &bb_modes_for_fixture(Mat2::zero(), &octahedron())).unwrap();
    assert!(bb.atomic_b[0][0].re < 0.0);
    let pair = he_two_photon_pair_source(&same_screen_pair(0.5, Mat2::identity(), Mat2::identity()), &s).unwrap();
    assert!(pair.pair_matrix[0][0].re < 0.0);
    let mut bf = s; bf.f = Mat2::identity();
    assert!(he_p_bf_source(bf.constants.chi_p_ev + 1.2 * bf.constants.rydberg_ev, &bf, PBoundFreeTable::jacobs_high_length()).unwrap().photon_c[0][0].re < 0.0);
}

#[test]
fn valid_complex_and_zero_inputs_unchanged() {
    let s = task2_state();
    let old_w = s.wp; let old_f = s.f; let old_v = s.v;
    assert!(s.validate().is_ok());
    assert_eq!(s.wp, old_w); assert_eq!(s.f, old_f); assert_eq!(s.v, old_v);
    let z = SourceState::simple(0.0, 0.0, Mat3::zero(), 0.0, 0.0, 9000.0).unwrap();
    assert!(z.validate().is_ok());
    assert_eq!(he_s_bf_source(z.constants.chi_s_ev + z.constants.rydberg_ev, &z, SBoundFreeTable::jacobs_high_length()).unwrap().photon_c, Mat2::zero());
    let mut f = s.f; f[1][0] = c(0.0, 0.0);
    assert!(matches!(f.validate_occupation(), Err(CoverageError::InvalidInput(_))));
}

#[test]
fn ledger_energy_inputs_reject_nonfinite_but_signed_rates_allowed() {
    let rates = ChannelRates { r584: -1.0, rir: 0.0, rp: 0.0, rs: 0.0, r2g: 0.0 };
    let en = HeEnergies::canonical();
    assert!(assemble_he_event_ledger(rates, en, 0.0, 0.0).is_ok());
    for bad in [f64::NAN, f64::INFINITY, 0.0, -1.0] {
        let mut e = en; e.chi_p = bad;
        assert!(matches!(assemble_he_event_ledger(rates, e, 0.0, 0.0), Err(CoverageError::InvalidInput(_))));
    }
    let mut e = en; e.delta_p += 1.0;
    assert!(assemble_he_event_ledger(rates, e, 0.0, 0.0).is_err());
}

// Task 3 tests are written before BB repair. Rust compilation/execution is local-only.
// References: bb_reference_task3.json, generated independently by exact component sums.
fn bb3_cmp(a: f64, b: f64, gross: f64) {
    assert!(a.is_finite() && b.is_finite() && gross.is_finite() && gross >= 0.0);
    if gross == 0.0 { assert_eq!(a,b); }
    else { assert!((a-b).abs() <= 4096.0*f64::EPSILON*gross, "actual={a}, expected={b}, reference gross={gross}"); }
}
fn bb3_m2(a: Mat2,b: Mat2,gross: f64) {
    for i in 0..2 { for j in 0..2 {
        bb3_cmp(a[i][j].re,b[i][j].re,gross);
        bb3_cmp(a[i][j].im,b[i][j].im,gross);
    }}
}
fn bb3_m3(a: Mat3,b: Mat3,gross: f64) {
    for i in 0..3 { for j in 0..3 {
        bb3_cmp(a[i][j].re,b[i][j].re,gross);
        bb3_cmp(a[i][j].im,b[i][j].im,gross);
    }}
}
fn bb3_case_0() -> (f64, Mat3, Vec<(WeightedBbMode, Mat3, Mat2, f64, f64)>) {
    ((3.0 / 5.0), Mat3([[c((2.0 / 5.0),0.0), c(0.0,0.0), c(0.0,0.0)], [c(0.0,0.0), c((7.0 / 10.0),0.0), c(0.0,0.0)], [c(0.0,0.0), c(0.0,0.0), c((11.0 / 10.0),0.0)]]), vec![
        (WeightedBbMode {v: [[1.0, 0.0], [0.0, 1.0], [0.0, 0.0]], f: Mat2([[c((1.0 / 10.0),0.0), c(0.0,0.0)], [c(0.0,0.0), c((2.0 / 5.0),0.0)]]), weight_sr: 1.0},
         Mat3([[c((-19.0 / 50.0),0.0), c(0.0,0.0), c(0.0,0.0)], [c(0.0,0.0), c((-37.0 / 50.0),0.0), c(0.0,0.0)], [c(0.0,0.0), c(0.0,0.0), c(0.0,0.0)]]), Mat2([[c((19.0 / 50.0),0.0), c(0.0,0.0)], [c(0.0,0.0), c((37.0 / 50.0),0.0)]]),
         (43.0 / 25.0), (43.0 / 25.0)),
        (WeightedBbMode {v: [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]], f: Mat2([[c((7.0 / 10.0),0.0), c(0.0,0.0)], [c(0.0,0.0), c((1.0 / 5.0),0.0)]]), weight_sr: 1.0},
         Mat3([[c(0.0,0.0), c(0.0,0.0), c(0.0,0.0)], [c(0.0,0.0), c((-77.0 / 100.0),0.0), c(0.0,0.0)], [c(0.0,0.0), c(0.0,0.0), c((-6.0 / 5.0),0.0)]]), Mat2([[c((77.0 / 100.0),0.0), c(0.0,0.0)], [c(0.0,0.0), c((6.0 / 5.0),0.0)]]),
         (61.0 / 20.0), (61.0 / 20.0)),
    ])
}
fn bb3_case_1() -> (f64, Mat3, Vec<(WeightedBbMode, Mat3, Mat2, f64, f64)>) {
    ((7.0 / 10.0), Mat3([[c((2.0 / 5.0),0.0), c((1.0 / 20.0),(1.0 / 50.0)), c((3.0 / 100.0),(-1.0 / 100.0))], [c((1.0 / 20.0),(-1.0 / 50.0)), c((7.0 / 10.0),0.0), c((-1.0 / 25.0),(1.0 / 40.0))], [c((3.0 / 100.0),(1.0 / 100.0)), c((-1.0 / 25.0),(-1.0 / 40.0)), c((11.0 / 10.0),0.0)]]), vec![
        (WeightedBbMode {v: [[(3.0 / 5.0), 0.0], [(4.0 / 5.0), 0.0], [0.0, 1.0]], f: Mat2([[c((1.0 / 5.0),0.0), c((3.0 / 100.0),(1.0 / 25.0))], [c((3.0 / 100.0),(-1.0 / 25.0)), c((1.0 / 10.0),0.0)]]), weight_sr: (5.0 / 2.0)},
         Mat3([[c((-303.0 / 2000.0),0.0), c((-13987.0 / 50000.0),(-2139.0 / 200000.0)), c((-79.0 / 6250.0),(-89.0 / 50000.0))], [c((-13987.0 / 50000.0),(2139.0 / 200000.0)), c((-2979.0 / 6250.0),0.0), c((2323.0 / 100000.0),(-2729.0 / 100000.0))], [c((-79.0 / 6250.0),(89.0 / 50000.0)), c((2323.0 / 100000.0),(2729.0 / 100000.0)), c((-57007.0 / 50000.0),0.0)]]), Mat2([[c((31407.0 / 50000.0),0.0), c((-11.0 / 1000.0),(229.0 / 10000.0))], [c((-11.0 / 1000.0),(-229.0 / 10000.0)), c((57007.0 / 50000.0),0.0)]]),
         (337503.0 / 100000.0), (30101.0 / 12500.0)),
        (WeightedBbMode {v: [[1.0, 0.0], [0.0, 1.0], [0.0, 0.0]], f: Mat2([[c((2.0 / 5.0),0.0), c((1.0 / 25.0),(-3.0 / 100.0))], [c((1.0 / 25.0),(3.0 / 100.0)), c((1.0 / 5.0),0.0)]]), weight_sr: (3.0 / 4.0)},
         Mat3([[c((-1407.0 / 5000.0),0.0), c((-59.0 / 1000.0),(-61.0 / 2000.0)), c((-823.0 / 40000.0),(59.0 / 10000.0))], [c((-59.0 / 1000.0),(61.0 / 2000.0)), c((-3507.0 / 5000.0),0.0), c((93.0 / 4000.0),(-61.0 / 4000.0))], [c((-823.0 / 40000.0),(-59.0 / 10000.0)), c((93.0 / 4000.0),(61.0 / 4000.0)), c(0.0,0.0)]]), Mat2([[c((1407.0 / 5000.0),0.0), c((59.0 / 1000.0),(61.0 / 2000.0))], [c((59.0 / 1000.0),(-61.0 / 2000.0)), c((3507.0 / 5000.0),0.0)]]),
         (359.0 / 160.0), (10569.0 / 5000.0)),
    ])
}

#[test]
fn bb_anisotropic_node_modes() {
    let (lower, wp, reference) = bb3_case_0();
    let modes: Vec<_> = reference.iter().map(|x|x.0).collect();
    let ch = BoundBoundChannel::He584;
    let b = 3.0*ch.a_s_inv()/(8.0*std::f64::consts::PI);
    let out = he_bb_source(ch,lower,wp,&modes).unwrap();
    let mut expect = Mat3::zero(); let mut egross=0.0; let mut r=0.0; let mut rgross=0.0;
    for (i,(m,ba,ja,bg,jg)) in reference.iter().enumerate() {
        bb3_m2(out.angular_j[i],ja.scale(b),b*jg);
        expect=expect+ba.scale(b*m.weight_sr); egross+=bg*b*m.weight_sr;
        r+=ja.trace().re*b*m.weight_sr; rgross+=jg*b*m.weight_sr;
    }
    bb3_m3(out.atomic_b,expect,egross); bb3_cmp(out.event_rate,r,rgross);
    let broadcast: Vec<_> = modes.iter().map(|m|WeightedBbMode{f:modes[0].f,..*m}).collect();
    let wrong = he_bb_source(ch,lower,wp,&broadcast).unwrap();
    assert!((wrong.atomic_b-out.atomic_b).max_abs() > 1e-3*b);
    assert!(!out.stencil.full_sphere_moments_match);
}

#[test]
fn bb_atom_photon_trace_complex() {
    let (lower, wp, reference) = bb3_case_1();
    for ch in [BoundBoundChannel::He584,BoundBoundChannel::IrPToS] {
        let b = 3.0*ch.a_s_inv()/(8.0*std::f64::consts::PI);
        let mut all_bg=0.0; let mut all_jg=0.0;
        let modes: Vec<_> = reference.iter().map(|x|x.0).collect();
        for (m,ba,ja,bg,jg) in &reference {
            let out = he_bb_kernel(ch,lower,wp,m.f,m.v).unwrap();
            bb3_m3(out.atomic_b_shell,ba.scale(b),bg*b);
            bb3_m2(out.photon_j_shell,ja.scale(b),jg*b);
            bb3_cmp(out.atomic_b_shell.trace().re+out.photon_j_shell.trace().re,0.0,(bg+jg)*b);
            bb3_cmp(out.atomic_b_shell.trace().im+out.photon_j_shell.trace().im,0.0,(bg+jg)*b);
            all_bg+=bg*b*m.weight_sr; all_jg+=jg*b*m.weight_sr;
        }
        let out=he_bb_source(ch,lower,wp,&modes).unwrap();
        bb3_cmp(out.atomic_b.trace().re+out.event_rate,0.0,all_bg+all_jg);
        assert_eq!(wp,bb3_case_1().1); // the one caller-owned W_P is never altered
    }
}

#[test]
fn vacuum_bb_full_stencil_minus_aw() {
    let wp=bb3_case_1().1;
    let modes=bb_modes_for_fixture(Mat2::zero(),&octahedron());
    for ch in [BoundBoundChannel::He584,BoundBoundChannel::IrPToS] {
        let out=he_bb_source(ch,0.0,wp,&modes).unwrap();
        bb3_m3(out.atomic_b,wp.scale(-ch.a_s_inv()),10.0*ch.a_s_inv()*wp.max_abs());
        bb3_cmp(out.event_rate,ch.a_s_inv()*wp.trace().re,10.0*ch.a_s_inv()*wp.max_abs());
        assert!(out.stencil.full_sphere_moments_match);
    }
}

#[test]
fn bb_lte_each_mode_584_ir() {
    use rec_microphysics::he_singlet::planck_occupation;
    let t=7600.0;
    let state=SourceState::lte_populations(t,2e7,3e7).unwrap();
    let v0=[[1.0,0.0],[0.0,1.0],[0.0,0.0]];
    let v1=[[0.6,0.0],[0.8,0.0],[0.0,1.0]];
    for (ch,lower) in [(BoundBoundChannel::He584,state.ng),(BoundBoundChannel::IrPToS,state.ns)] {
        let f=planck_occupation(ch.energy_ev(),t);
        let b=3.0*ch.a_s_inv()/(8.0*std::f64::consts::PI);
        let independent_gross=6.0*b*(lower*f+state.wp.max_abs()*(1.0+f));
        for v in [v0,v1] {
            let out=he_bb_kernel(ch,lower,state.wp,Mat2::scalar(f),v).unwrap();
            bb3_m3(out.atomic_b_shell,Mat3::zero(),independent_gross);
            bb3_m2(out.photon_j_shell,Mat2::zero(),independent_gross);
            bb3_cmp(out.event_rate_per_sr,0.0,independent_gross);
        }
    }
}

#[test]
fn bb_sharp_shell_not_profile() {
    use rec_microphysics::he_singlet::{SpectralMeasure,H_J_S,C_M_S,EV_J};
    let (lower,wp,reference)=bb3_case_1(); let (m,_,ja,_,jg)=reference[0];
    for ch in [BoundBoundChannel::He584,BoundBoundChannel::IrPToS] {
        let out=he_bb_kernel(ch,lower,wp,m.f,m.v).unwrap();
        assert_eq!(out.spectral,SpectralMeasure::SharpLineDeltaPerJoule{energy_ev:ch.energy_ev()});
        let ej=ch.energy_ev()*EV_J;
        let mode_density=ej*ej/(H_J_S*C_M_S).powi(3);
        let b=3.0*ch.a_s_inv()/(8.0*std::f64::consts::PI);
        bb3_m2(out.occupation_c_shell.scale(mode_density),ja.scale(b),jg*b);
        let assembled=he_bb_source(ch,lower,wp,&[m]).unwrap();
        bb3_m2(assembled.angular_c[0],out.occupation_c_shell,jg*b/mode_density);
        // No energy width or delta(E=epsilon) numeric value is accepted by either API.
    }
}

#[test]
fn bb_same_wp_two_channels() {
    let wp=bb3_case_1().1;
    let modes=bb_modes_for_fixture(Mat2::scalar(0.2),&octahedron());
    let saved=wp;
    let a=he_bb_source(BoundBoundChannel::He584,0.7,wp,&modes).unwrap();
    let b=he_bb_source(BoundBoundChannel::IrPToS,0.7,wp,&modes).unwrap();
    bb3_m3(a.atomic_b.scale(1.0/BoundBoundChannel::He584.a_s_inv()),b.atomic_b.scale(1.0/BoundBoundChannel::IrPToS.a_s_inv()),20.0*wp.max_abs());
    assert_ne!(a.spectral,b.spectral); assert_eq!(wp,saved);
    // Each real caller chooses ng for 584 and nS for IR; no second W_P is constructed.
}

#[test]
fn bb_partial_stencil_is_not_renormalized() {
    let v=[[1.0,0.0],[0.0,1.0],[0.0,0.0]];
    let modes=[WeightedBbMode{v,f:Mat2::zero(),weight_sr:1.0}];
    let wp=wp_diag(1.0,2.0,3.0); let ch=BoundBoundChannel::He584;
    let b=3.0*ch.a_s_inv()/(8.0*std::f64::consts::PI);
    let out=he_bb_source(ch,0.0,wp,&modes).unwrap();
    bb3_m3(out.atomic_b,wp_diag(-b,-2.0*b,0.0),6.0*b);
    assert_eq!(out.stencil.weight_sum_sr,1.0);
    assert!(!out.stencil.full_sphere_moments_match);
    assert_eq!(out.atomic_b[2][2].re,0.0);
    assert!((out.atomic_b[2][2].re+ch.a_s_inv()*wp[2][2].re).abs() > ch.a_s_inv());
}

#[test]
fn bb_angular_weight_applied_once() {
    let (lower,wp,r)=bb3_case_1();let (m,ba,ja,bg,jg)=r[0];
    let ch=BoundBoundChannel::He584;
    let b=3.0*ch.a_s_inv()/(8.0*std::f64::consts::PI);
    let o=he_bb_source(ch,lower,wp,&[m]).unwrap();
    bb3_m3(o.atomic_b,ba.scale(b*m.weight_sr),bg*b*m.weight_sr);
    bb3_m2(o.angular_j[0],ja.scale(b),jg*b); // unweighted in its own screen
    bb3_cmp(o.event_rate,ja.trace().re*b*m.weight_sr,jg*b*m.weight_sr);
    let doubled=WeightedBbMode{weight_sr:2.0*m.weight_sr,..m};
    let d=he_bb_source(ch,lower,wp,&[doubled]).unwrap();
    bb3_m3(d.atomic_b,o.atomic_b.scale(2.0),2.0*bg*b*m.weight_sr);
    bb3_m2(d.angular_j[0],o.angular_j[0],jg*b);
}

#[test]
fn bb_invalid_modes_and_weights() {
    let (n,w,r)=bb3_case_1();let m=r[0].0;let ch=BoundBoundChannel::He584;
    assert!(he_bb_source(ch,n,w,&[]).is_err());
    for bad in [-1.0,f64::NAN,f64::INFINITY,f64::NEG_INFINITY] {
        let bad_mode=WeightedBbMode{weight_sr:bad,..m};
        assert!(he_bb_source(ch,n,w,&[bad_mode]).is_err());
        assert!(he_bb_source(ch,bad,w,&[m]).is_err());
    }
    let mut bad=m;bad.weight_sr=0.0;bad.f[0][0].re=f64::NAN;
    assert!(he_bb_source(ch,n,w,&[bad]).is_err()); // zero weight cannot mask bad input
    bad=m;bad.v=[[2.0,0.0],[0.0,2.0],[0.0,0.0]];
    assert!(he_bb_source(ch,n,w,&[bad]).is_err());
    assert!(he_bb_kernel(ch,n,w,bad.f,bad.v).is_err());
    assert!(he_bb_kernel(ch,n,wp_diag(-1.0,1.0,1.0),m.f,m.v).is_err());
}

#[test]
fn bb_stencil_diagnostics_are_moments_only() {
    use rec_microphysics::he_singlet::audit_bb_stencil;
    let modes=bb_modes_for_fixture(Mat2::zero(),&octahedron());
    let good=audit_bb_stencil(&modes).unwrap();assert!(good.full_sphere_moments_match);
    let target=8.0*std::f64::consts::PI/3.0;
    for i in 0..3 {for j in 0..3 {bb3_cmp(good.projector_sum_sr[i][j],if i==j {target}else{0.0},target);}}
    let bad:Vec<_>=modes.iter().map(|m|WeightedBbMode{v:modes[0].v,..*m}).collect();
    let defect=audit_bb_stencil(&bad).unwrap();
    assert!(defect.weight_relative_residual < 4096.0*f64::EPSILON);
    assert!(defect.projector_relative_residual > 0.1);
    assert!(!defect.full_sphere_moments_match);
}

#[test]
fn bb_zero_sources_and_zero_weight() {
    let (lower,wp,r)=bb3_case_1();let m=r[0].0;
    let ch=BoundBoundChannel::He584;
    let empty=he_bb_source(ch,0.0,Mat3::zero(),&[m]).unwrap();
    assert_eq!(empty.atomic_b,Mat3::zero());assert_eq!(empty.event_rate,0.0);
    assert_eq!(empty.angular_j[0],Mat2::zero());assert_eq!(empty.angular_c[0],Mat2::zero());
    let zero=WeightedBbMode{weight_sr:0.0,..m};
    let out=he_bb_source(ch,lower,wp,&[zero]).unwrap();
    assert_eq!(out.atomic_b,Mat3::zero());assert_eq!(out.event_rate,0.0);
    assert!(out.angular_j[0].max_abs() > 0.0); // kernel was not weighted or discarded
    assert!(!out.stencil.full_sphere_moments_match);
}

#[test]
fn bb_nonfinite_arithmetic_is_not_success() {
    let ch=BoundBoundChannel::He584;let v=[[1.0,0.0],[0.0,1.0],[0.0,0.0]];
    let result=he_bb_kernel(ch,f64::MAX,Mat3::zero(),Mat2::identity(),v);
    assert!(matches!(result,Err(CoverageError::NumericalDomainUncertain{..})));
    let mode=WeightedBbMode{v,f:Mat2::identity(),weight_sr:f64::MAX};
    assert!(he_bb_source(ch,1.0,Mat3::identity(),&[mode,mode]).is_err());
}

// Only these historical fixtures explicitly broadcast F at the caller site.
// The production API receives a distinct F in every WeightedBbMode.
fn bb_modes_for_fixture(f: Mat2, angular: &[AngularSample]) -> Vec<WeightedBbMode> {
    angular.iter().map(|s| WeightedBbMode {
        v: s.v, f, weight_sr: s.weight_sr,
    }).collect()
}

// Explicit same-screen fixture adapter only, never a production geometry default.
fn same_screen_pair(y: f64, f1: Mat2, f2: Mat2) -> PairInput {
    PairInput { y, f1, f2, v1: [[1.0,0.0],[0.0,1.0],[0.0,0.0]],
        v2: [[1.0,0.0],[0.0,1.0],[0.0,0.0]] }
}

fn t4_pair_state(ng: f64, ns: f64) -> SourceState {
    SourceState::simple(ng, ns, Mat3::zero(), 0.0, 0.0, 8000.0).unwrap()
}
fn t4_vx() -> [[f64; 2]; 3] {
    [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]]
}
fn t4_vt() -> [[f64; 2]; 3] {
    [[0.0, -3.0 / 5.0], [1.0, 0.0], [0.0, -4.0 / 5.0]]
}
fn t4_fa() -> Mat2 {
    Mat2([[c(0.2, 0.0), c(0.03, 0.04)], [c(0.03, -0.04), c(0.1, 0.0)]])
}
fn t4_fb() -> Mat2 {
    Mat2([[c(0.4, 0.0), c(-0.07, 0.03)], [c(-0.07, -0.03), c(0.3, 0.0)]])
}
fn t4_assert_scaled(actual: f64, expected: f64, reference_scale: f64) {
    assert!(actual.is_finite() && expected.is_finite());
    assert!(reference_scale.is_finite() && reference_scale > 0.0);
    assert!((actual - expected).abs() / reference_scale <= 4096.0 * f64::EPSILON,
        "actual={actual}, expected={expected}, scale={reference_scale}");
}
fn t4_assert_matrix(actual: Mat2, expected: Mat2, reference_scale: f64) {
    for i in 0..2 {
        for j in 0..2 {
            t4_assert_scaled(actual[i][j].re, expected[i][j].re, reference_scale);
            t4_assert_scaled(actual[i][j].im, expected[i][j].im, reference_scale);
        }
    }
}
fn t4_complex_input() -> PairInput {
    PairInput {
        y: 0.3, f1: t4_fa(), f2: t4_fb(),
        v1: [[1.0, 0.0], [0.0, 1.0], [0.0, 0.0]], v2: t4_vt(),
    }
}
fn t4_ordered_grid() -> Vec<WeightedPairMode> {
    let screens = [[[1.0, 0.0], [0.0, 1.0], [0.0, 0.0]], t4_vx()];
    let occupations = [[t4_fa(), t4_fb()], [t4_fb().scale(2.0), t4_fa().scale(3.0)]];
    let angular = [2.0, 3.0];
    let ys = [0.25, 0.75];
    let mut nodes = Vec::new();
    for yi in 0..2 {
        for i in 0..2 {
            for j in 0..2 {
                nodes.push(WeightedPairMode {
                    input: PairInput { y: ys[yi], f1: occupations[yi][i],
                        f2: occupations[1 - yi][j], v1: screens[i], v2: screens[j] },
                    weight_dy: 0.125, weight_omega1_sr: angular[i], weight_omega2_sr: angular[j],
                    exchange_partner: (1 - yi) * 4 + j * 2 + i,
                });
            }
        }
    }
    nodes
}

#[test]
fn pair_perpendicular_vacuum_screen_overlap() {
    let state = t4_pair_state(1.4, 1.0);
    let mut input = same_screen_pair(0.25, Mat2::zero(), Mat2::zero());
    input.v2 = t4_vx();
    let out = he_two_photon_pair_source(&input, &state).unwrap();
    t4_assert_matrix(out.screen_overlap, Mat2([[c(0.0,0.0),c(0.0,0.0)], [c(1.0,0.0),c(0.0,0.0)]]), 1.0);
    t4_assert_matrix(out.pair_matrix, Mat2([[c(0.0,0.0),c(0.0,0.0)], [c(0.0,0.0),c(1.0,0.0)]]), 1.0);
    assert_eq!(out.pair_matrix.trace().re, 1.0);
    assert_ne!(out.pair_matrix.trace().re, 2.0); // Reject the old identity shortcut.
}

#[test]
fn pair_complex_transpose_reference() {
    // Independent exact component contraction frozen before production edits.
    let out = he_two_photon_pair_source(&t4_complex_input(), &t4_pair_state(1.3, 2.1)).unwrap();
    let expected = Mat2([
        [c(35991.0/31250.0, 0.0), c(4443.0/31250.0, 3161.0/125000.0)],
        [c(4443.0/31250.0, -3161.0/125000.0), c(99451.0/31250.0, 0.0)],
    ]);
    let partner = Mat2([
        [c(99451.0/31250.0, 0.0), c(-4613.0/31250.0, -1527.0/125000.0)],
        [c(-4613.0/31250.0, 1527.0/125000.0), c(35991.0/31250.0, 0.0)],
    ]);
    t4_assert_matrix(out.pair_matrix, expected, 4.0);
    t4_assert_matrix(out.partner_pair_matrix, partner, 4.0);
}

#[test]
fn pair_swapped_tags_match() {
    let state = t4_pair_state(1.3, 2.1);
    let input = t4_complex_input();
    let swapped = PairInput { y: 1.0 - input.y, f1: input.f2, f2: input.f1, v1: input.v2, v2: input.v1 };
    let a = he_two_photon_pair_source(&input, &state).unwrap();
    let b = he_two_photon_pair_source(&swapped, &state).unwrap();
    t4_assert_matrix(a.partner_pair_matrix, b.pair_matrix, 4.0);
    t4_assert_scaled(a.pair_matrix.trace().re, b.pair_matrix.trace().re, 8.0);
    t4_assert_scaled(a.energy1_j, b.energy2_j, a.delta_s_j);
    t4_assert_scaled(a.energy2_j, b.energy1_j, a.delta_s_j);
    assert_ne!(a.pair_matrix, a.partner_pair_matrix); // Distinct screens, no matrix identification.
}

#[test]
fn pair_lte_all_represented_modes() {
    let state = SourceState::lte_populations(8000.0, 2.0e7, 3.0e7).unwrap();
    for j in 1..40 {
        let y = f64::from(j) / 40.0;
        let delta_ev = state.constants.delta_s_ev;
        let input = PairInput {
            y,
            f1: Mat2::scalar(rec_microphysics::he_singlet::planck_occupation(delta_ev*y, 8000.0)),
            f2: Mat2::scalar(rec_microphysics::he_singlet::planck_occupation(delta_ev*(1.0-y), 8000.0)),
            v1: [[1.0,0.0],[0.0,1.0],[0.0,0.0]], v2: t4_vt(),
        };
        let out = he_two_photon_pair_source(&input, &state).unwrap();
        // Independent emission bound from the scalar Planck factors and this T.
        let gross = 2.0 * state.ns * (1.0 + input.f1[0][0].re) * (1.0 + input.f2[0][0].re);
        t4_assert_matrix(out.pair_matrix, Mat2::zero(), gross);
        t4_assert_matrix(out.partner_pair_matrix, Mat2::zero(), gross);
    }
}

#[test]
fn pair_measure_factor_once() {
    use rec_microphysics::he_singlet::{EV_J, H_J_S, C_M_S, SpectralMeasure};
    let state = t4_pair_state(1.4, 1.0);
    let mut input = same_screen_pair(0.25, Mat2::zero(), Mat2::zero());
    input.v2 = t4_vx();
    let out = he_two_photon_pair_source(&input, &state).unwrap();
    let g = 3.0 / (64.0 * std::f64::consts::PI.powi(2));
    let expected_w = 119.447; // Canonical y=10/40 printed node.
    let delta = state.constants.delta_s_ev * EV_J;
    let a_gamma = 1.0 / (H_J_S*C_M_S).powi(3);
    t4_assert_scaled(out.event_rate_density, 0.5*expected_w*g, expected_w*g);
    t4_assert_scaled(out.tagged_c1_per_partner_sr[1][1].re*a_gamma*(delta*0.25).powi(2)*delta, expected_w*g, expected_w*g);
    t4_assert_scaled(out.tagged_c2_per_partner_sr[0][0].re*a_gamma*(delta*0.75).powi(2)*delta, expected_w*g, expected_w*g);
    assert_eq!(out.density_measure, SpectralMeasure::PairDyDOmega1DOmega2);
    assert_eq!(out.photon_tags_per_event, 2);
}

#[test]
fn pair_photon_count_energy_from_marginals() {
    let state = t4_pair_state(1.3, 2.1);
    let out = assemble_he_pair_grid(&state, &t4_ordered_grid(), PairGridConvention::FullOrderedExchangeClosed).unwrap();
    let g = 3.0 / (64.0 * std::f64::consts::PI.powi(2));
    let expected_event = (11203770259.0 / 5000000.0) * g;
    let delta = state.constants.delta_s_ev * rec_microphysics::he_singlet::EV_J;
    t4_assert_scaled(out.event_rate, expected_event, expected_event.abs());
    for tag in 0..2 {
        t4_assert_scaled(out.photon_number_from_marginals[tag], 2.0*expected_event, 2.0*expected_event.abs());
        t4_assert_scaled(out.photon_energy_from_marginals_j[tag], delta*expected_event, delta*expected_event.abs());
        t4_assert_scaled(out.photon_number_residuals[tag], 0.0, 2.0*expected_event.abs());
        t4_assert_scaled(out.photon_energy_residuals_j[tag], 0.0, delta*expected_event.abs());
    }
    assert!(out.photon_number_from_marginals.iter().sum::<f64>() > 3.9*expected_event);
    // Summing both full estimates is 4R, not the physical 2R.
}

#[test]
fn pair_unordered_half_grid_rejected() {
    let err = assemble_he_pair_grid(&t4_pair_state(1.3,2.1), &t4_ordered_grid(), PairGridConvention::UnorderedHalfGridUnsupported).unwrap_err();
    assert!(matches!(err, CoverageError::MissingAuthority { .. }));
}

#[test]
fn pair_exchange_contract_rejects_missing_or_mismatched_partner() {
    let state = t4_pair_state(1.3,2.1);
    let mut nodes=t4_ordered_grid(); nodes.pop();
    assert!(assemble_he_pair_grid(&state, &nodes, PairGridConvention::FullOrderedExchangeClosed).is_err());
    for mutation in 0..6 {
        let mut nodes=t4_ordered_grid();
        match mutation {
            0 => nodes[0].exchange_partner=1,
            1 => nodes[0].input.y=0.3,
            2 => nodes[0].input.f1=Mat2::scalar(0.1),
            3 => nodes[0].input.v1=t4_vt(),
            4 => nodes[0].weight_dy=0.25,
            _ => nodes[0].weight_omega1_sr=4.0,
        }
        assert!(assemble_he_pair_grid(&state, &nodes, PairGridConvention::FullOrderedExchangeClosed).is_err());
    }
}

#[test]
fn pair_grid_weights_applied_once_no_renormalization() {
    let state=t4_pair_state(1.3,2.1);
    let nodes=t4_ordered_grid();
    let a=assemble_he_pair_grid(&state,&nodes,PairGridConvention::FullOrderedExchangeClosed).unwrap();
    let mut bnodes=nodes;
    for n in &mut bnodes { n.weight_dy *= 3.0; }
    let b=assemble_he_pair_grid(&state,&bnodes,PairGridConvention::FullOrderedExchangeClosed).unwrap();
    t4_assert_scaled(b.event_rate,3.0*a.event_rate,3.0*a.event_rate.abs());
    for tag in 0..2 { t4_assert_scaled(b.photon_number_from_marginals[tag],3.0*a.photon_number_from_marginals[tag],6.0*a.event_rate.abs()); }
}

#[test]
fn pair_bad_inputs_reject_even_at_zero_weight() {
    let state=t4_pair_state(1.3,2.1);
    for bad in [f64::NAN,f64::INFINITY,f64::NEG_INFINITY,-1.0] {
        let mut nodes=t4_ordered_grid();nodes[0].weight_dy=bad;
        assert!(assemble_he_pair_grid(&state,&nodes,PairGridConvention::FullOrderedExchangeClosed).is_err());
    }
    let mut nodes=t4_ordered_grid();
    for n in &mut nodes { n.weight_dy=0.0; }
    nodes[0].input.f2[0][0]=c(f64::NAN,0.0);
    assert!(assemble_he_pair_grid(&state,&nodes,PairGridConvention::FullOrderedExchangeClosed).is_err());
    for bad in [f64::NAN,f64::INFINITY,f64::NEG_INFINITY] {
        let mut input=t4_complex_input();input.y=bad;
        assert!(he_two_photon_pair_source(&input,&state).is_err());
    }
    let mut input=t4_complex_input();input.v2[0][1]=2.0;
    assert!(matches!(he_two_photon_pair_source(&input,&state),Err(CoverageError::InvalidInput(_))));
}

#[test]
fn pair_zero_and_signed_sources_remain_distinct_from_input_psd() {
    let input=t4_complex_input();
    let zero=he_two_photon_pair_source(&input,&t4_pair_state(0.0,0.0)).unwrap();
    assert_eq!(zero.pair_matrix,Mat2::zero());
    assert_eq!(zero.tagged_c1_per_partner_sr,Mat2::zero());
    let absorption=he_two_photon_pair_source(&input,&t4_pair_state(5.0,0.0)).unwrap();
    assert!(absorption.event_rate_density<0.0);
    assert!(absorption.pair_matrix.trace().re<0.0);
    let mut nodes=t4_ordered_grid();for n in &mut nodes {n.weight_dy=0.0;}
    let out=assemble_he_pair_grid(&t4_pair_state(1.3,2.1),&nodes,PairGridConvention::FullOrderedExchangeClosed).unwrap();
    assert_eq!(out.event_rate,0.0);
    assert_eq!(out.photon_number_from_marginals,[0.0,0.0]);
}

#[test]
fn pair_nonfinite_arithmetic_is_not_success() {
    let input=same_screen_pair(0.5,Mat2::scalar(1e308),Mat2::scalar(1e308));
    assert!(matches!(he_two_photon_pair_source(&input,&t4_pair_state(0.0,1.0)),Err(CoverageError::NumericalDomainUncertain { .. })));
    let mut nodes=t4_ordered_grid();for n in &mut nodes {n.weight_dy=1e308;}
    assert!(matches!(assemble_he_pair_grid(&t4_pair_state(1.3,2.1),&nodes,PairGridConvention::FullOrderedExchangeClosed),Err(CoverageError::NumericalDomainUncertain { .. })));
}

#[test]
fn d86_all_twenty_nodes_and_reflection() {
    let printed = [7.736,25.158,43.302,59.693,73.920,86.112,96.523,105.407,112.986,119.447,
        124.942,129.596,133.508,136.760,139.416,141.525,143.128,144.253,144.921,145.142];
    for (i, expected) in printed.iter().enumerate() {
        let y=(i+1) as f64/40.0;
        assert_eq!(d86_w(y).unwrap(),*expected);
        assert_eq!(d86_w(1.0-y).unwrap(),*expected);
        if i<19 { t4_assert_scaled(d86_w((i as f64+1.5)/40.0).unwrap(),0.5*(printed[i]+printed[i+1]),printed[i+1]); }
    }
}

#[test]
fn d86_outside_band_error() {
    let lo=0.025_f64;let hi=0.975_f64;
    for y in [0.0,1.0,f64::from_bits(lo.to_bits()-1),f64::from_bits(hi.to_bits()+1)] {
        assert!(matches!(d86_w(y),Err(CoverageError::OutOfBand { .. })));
    }
    let mut input=t4_complex_input();input.y=0.024;
    assert!(matches!(he_two_photon_pair_source(&input,&t4_pair_state(1.3,2.1)),Err(CoverageError::OutOfBand { .. })));
}

#[test]
fn pair_integrated_event_passes_ledger_without_another_half() {
    let state=t4_pair_state(1.3,2.1);
    let pair=assemble_he_pair_grid(&state,&t4_ordered_grid(),PairGridConvention::FullOrderedExchangeClosed).unwrap();
    let rates=ChannelRates {r584:0.0,rir:0.0,rp:0.0,rs:0.0,r2g:pair.event_rate};
    let ledger=assemble_he_event_ledger(rates,HeEnergies::canonical(),0.0,0.0).unwrap();
    t4_assert_scaled(ledger.species_source[0],pair.event_rate,pair.event_rate.abs());
    t4_assert_scaled(ledger.species_source[1],-pair.event_rate,pair.event_rate.abs());
    t4_assert_scaled(ledger.photon_number_source,pair.photon_number_from_marginals[0],2.0*pair.event_rate.abs());
}


// Task 5 tests are authored before production edits; all require local Rust execution.
use rec_microphysics::ledger::{
    BfChannel, WeightedBfMode, DirectedBbMode, DirectedPairMode,
    assemble_he_bf_grid, assemble_selected_he_material_ledger,
};
use rec_microphysics::he_singlet::{C_M_S, H_J_S, EV_J, KB_J_K, ME_KG, HBAR_J_S};

fn t5_assert_ref(actual: f64, expected: f64, reference_gross: f64) {
    assert!(actual.is_finite() && expected.is_finite() && reference_gross.is_finite());
    assert!(reference_gross >= 0.0);
    if reference_gross == 0.0 { assert_eq!(actual, expected); }
    else { assert!((actual-expected).abs() <= 4096.0*f64::EPSILON*reference_gross,
        "actual={actual:e} expected={expected:e} scale={reference_gross:e}"); }
}
fn t5_state() -> SourceState {
    SourceState::simple(2.0,0.7,wp_diag(0.4,0.7,1.1),2.0e13,3.0e13,100000.0).unwrap()
}
fn t5_bf_node(channel: BfChannel, state: &SourceState, q: f64, f: Mat2) -> WeightedBfMode {
    let chi = match channel { BfChannel::P(_) => state.constants.chi_p_ev,
                              BfChannel::S(_) => state.constants.chi_s_ev };
    WeightedBfMode { channel, energy_ev: chi+q*state.constants.rydberg_ev,
        f, v:[[1.0,0.0],[0.0,1.0],[0.0,0.0]], direction:[0.0,0.0,1.0],
        weight_energy_j:0.25*EV_J, weight_omega_sr:0.4 }
}
fn t5_reference_eta(state:&SourceState,energy:f64,chi:f64)->f64 {
    let phi=(ME_KG*KB_J_K*state.temperature_k/(2.0*std::f64::consts::PI*HBAR_J_S*HBAR_J_S)).powf(1.5);
    state.n_he_plus*state.ne*(-(energy-chi)*EV_J/(KB_J_K*state.temperature_k)).exp()/(4.0*phi)
}

#[test]
fn pbf_complex_component_reference() {
    let mut state=t5_state();
    state.wp=Mat3([[c(0.4, 0.0),c(0.05, 0.02),c(0.0, 0.0)],[c(0.05, -0.02),c(0.7, 0.0),c(0.0, 0.0)],[c(0.0, 0.0),c(0.0, 0.0),c(1.1, 0.0)]]);
    state.f=Mat2([[c(0.2, 0.0),c(0.03, 0.04)],[c(0.03, -0.04),c(0.1, 0.0)]]);
    state.v=[[1.0,0.0],[0.0,0.8],[0.0,0.6]];
    let e=state.constants.chi_p_ev+1.2*state.constants.rydberg_ev;
    let out=he_p_bf_source(e,&state,PBoundFreeTable::jacobs_high_length()).unwrap();
    let ref_c=Mat2([[c(-2.1321984181897517e-16, 0.0),c(-4.6715647570768076e-17, -5.143644597956601e-17)],[c(-4.6715647570768076e-17, 5.143644597956601e-17),c(-1.5870598639425244e-16, 0.0)]]);
    let ref_b=Mat3([[c(-1.606687387985544e+23, 0.0),c(-3.4559114993934747e+22, 7.996393015859684e+21),c(-2.1817227753703694e+22, 1.359225567801649e+22)],[c(-3.4559114993934747e+22, -7.996393015859684e+21),c(-1.3965997610392994e+23, 0.0),c(-6.438487996446347e+22, 7.442646899278477e+20)],[c(-2.1817227753703694e+22, -1.359225567801649e+22),c(-6.438487996446347e+22, -7.442646899278477e+20),c(-1.7218208030060314e+23, 0.0)]]);
    for i in 0..2 { for j in 0..2 {
        t5_assert_ref(out.photon_c[i][j].re,ref_c[i][j].re,5.242019755505237e-16);
        t5_assert_ref(out.photon_c[i][j].im,ref_c[i][j].im,5.242019755505237e-16);
    }}
    for i in 0..3 { for j in 0..3 {
        t5_assert_ref(out.atomic_b[i][j].re,ref_b[i][j].re,7.421632969954199e+23);
        t5_assert_ref(out.atomic_b[i][j].im,ref_b[i][j].im,7.421632969954199e+23);
    }}
    t5_assert_ref(out.event_rate_density,4.725107952030875e+23,2.0*7.421632969954199e+23);
}

#[test]
fn pbf_isotropic_scalar_non_lte() {
    let mut state=t5_state(); let np=4.2; let f=0.17;
    state.wp=Mat3::scalar(np/3.0); state.f=Mat2::scalar(f);
    let e=state.constants.chi_p_ev+1.2*state.constants.rydberg_ev;
    for (table,fs,fd) in [(PBoundFreeTable::jacobs_high_length(),0.001486,0.001247),
                          (PBoundFreeTable::jacobs_high_velocity(),0.001380,0.001010)] {
        let sigma=8.06728372576034*(fs+fd)*1e-22;
        let eta=t5_reference_eta(&state,e,state.constants.chi_p_ev);
        let want=C_M_S*sigma*(3.0*eta*(1.0+f)-np*f);
        let gross=C_M_S*sigma*(3.0*eta*(1.0+f)+np*f);
        let out=he_p_bf_source(e,&state,table).unwrap();
        for i in 0..2 { for j in 0..2 {
            t5_assert_ref(out.photon_c[i][j].re,if i==j {want}else{0.0},gross);
            t5_assert_ref(out.photon_c[i][j].im,0.0,gross);
        }}
    }
}

#[test]
fn sbf_lte_and_non_lte() {
    let mut state=t5_state(); state.f=Mat2::scalar(0.17);
    let e=state.constants.chi_s_ev+1.2*state.constants.rydberg_ev;
    let eta=t5_reference_eta(&state,e,state.constants.chi_s_ev);
    for (table,printed) in [(SBoundFreeTable::jacobs_high_length(),0.04812),
                            (SBoundFreeTable::jacobs_high_velocity(),0.04696)] {
        let sigma=8.06728372576034*printed*1e-22;
        let wanted=C_M_S*sigma*(eta*1.17-state.ns*0.17);
        let gross=C_M_S*sigma*(eta*1.17+state.ns*0.17);
        let out=he_s_bf_source(e,&state,table).unwrap();
        t5_assert_ref(out.photon_c[0][0].re,wanted,gross);
        let ag_e2=(e*EV_J).powi(2)/(H_J_S*C_M_S).powi(3);
        t5_assert_ref(out.atomic_s_density,2.0*ag_e2*wanted,2.0*ag_e2*gross);
        t5_assert_ref(out.event_rate_density,-out.atomic_s_density,2.0*ag_e2*gross);
    }
    let mut lte=SourceState::lte_populations(8000.0,2e7,3e7).unwrap();
    let e=lte.constants.chi_s_ev+1.2*lte.constants.rydberg_ev;
    lte.f=Mat2::scalar(rec_microphysics::he_singlet::planck_occupation(e,lte.temperature_k));
    let out=he_s_bf_source(e,&lte,SBoundFreeTable::jacobs_high_length()).unwrap();
    t5_assert_ref(out.atomic_s_density,0.0,out.atomic_gross_scale);
}

#[test]
fn bf_photon_ion_electron_sign() {
    for channel in [BfChannel::P(PBoundFreeTable::jacobs_high_length()),BfChannel::S(SBoundFreeTable::jacobs_high_length())] {
        let mut state=t5_state();state.n_he_plus=0.0;state.ne=0.0;
        let node=t5_bf_node(channel,&state,1.2,Mat2::scalar(0.2));
        let full=assemble_selected_he_material_ledger(&state,&[],&[],&[node],&[],PairGridConvention::FullOrderedExchangeClosed).unwrap();
        let s=full.ledger_si.species_source;assert!(s[3]>0.0 && s[4]>0.0 && full.photon.number_rate<0.0);
        t5_assert_ref(s[3],s[4],s[3]);t5_assert_ref(full.photon.number_rate,-s[3],s[3]);
        assert!(full.bf.heat_power_j>0.0 && full.force.q_matter[0]>0.0);
        state.wp=Mat3::zero();state.ns=0.0;state.n_he_plus=2e13;state.ne=3e13;
        let inverse=t5_bf_node(channel,&state,1.2,Mat2::zero());
        let out=assemble_selected_he_material_ledger(&state,&[],&[],&[inverse],&[],PairGridConvention::FullOrderedExchangeClosed).unwrap();
        assert!(out.ledger_si.species_source[3]<0.0 && out.photon.number_rate>0.0 && out.bf.heat_power_j<0.0);
    }
}

#[test]
fn bf_independent_heat_moment() {
    let state=t5_state();
    let p=t5_bf_node(BfChannel::P(PBoundFreeTable::jacobs_high_length()),&state,1.0,Mat2::scalar(0.25));
    let mut ss=t5_bf_node(BfChannel::S(SBoundFreeTable::jacobs_high_velocity()),&state,1.4,Mat2::zero());
    ss.weight_energy_j=0.7*EV_J;ss.weight_omega_sr=0.9;
    let mut heat=0.0;let mut pint=0.0;let mut pph=0.0;let mut scale=0.0;
    for node in [p,ss] {
        let mut local=state;local.f=node.f;local.v=node.v;
        let (j,chi,trace_c)=match node.channel {
            BfChannel::P(t)=>{let o=he_p_bf_source(node.energy_ev,&local,t).unwrap();(o.event_rate_density,state.constants.chi_p_ev,o.photon_c.trace().re)},
            BfChannel::S(t)=>{let o=he_s_bf_source(node.energy_ev,&local,t).unwrap();(o.event_rate_density,state.constants.chi_s_ev,o.photon_c.trace().re)},
        };
        let weight=node.weight_energy_j*node.weight_omega_sr;
        heat+=(node.energy_ev-chi)*EV_J*j*weight;
        pint+=chi*EV_J*j*weight;
        pph+=(node.energy_ev*EV_J).powi(3)/(H_J_S*C_M_S).powi(3)*trace_c*weight;
        scale+=node.energy_ev*EV_J*j.abs()*weight;
    }
    let out=assemble_he_bf_grid(&state,&[p,ss]).unwrap();
    t5_assert_ref(out.heat_power_j,heat,scale);
    t5_assert_ref(out.internal_power_j,pint,scale);
    t5_assert_ref(out.photon.energy_rate_j,pph,scale);
    t5_assert_ref(out.heat_power_j+out.internal_power_j+out.photon.energy_rate_j,0.0,scale);
    assert!((out.heat_power_j+out.photon.energy_rate_j).abs()>1e-6*scale);
}

#[test]
fn ledger_each_signed_channel() {
    let energies=HeEnergies::canonical_si();
    let columns=[[1.,0.,-1.,0.,0.,1.],[0.,1.,-1.,0.,0.,1.],[0.,0.,-1.,1.,1.,-1.],[0.,-1.,0.,1.,1.,-1.],[1.,-1.,0.,0.,0.,2.]];
    for j in 0..5 { for sign in [1.0,-1.0] {
        let mut rs=[0.0;5];rs[j]=sign;
        let rates=ChannelRates{r584:rs[0],rir:rs[1],rp:rs[2],rs:rs[3],r2g:rs[4]};
        let kinetic=2.0*EV_J;
        let chi=if j==2 {energies.chi_p}else if j==3 {energies.chi_s}else{0.0};
        let heat=if j==2 || j==3 {kinetic*sign}else{0.0};
        let bf_energy=if j==2 || j==3 {(chi+kinetic)*sign}else{0.0};
        let l=assemble_he_event_ledger(rates,energies,bf_energy,heat).unwrap();
        for i in 0..6 {assert_eq!(l.species_source[i],sign*columns[j][i]);}
        assert_eq!(l.he_nuclei_residual,0.0);assert_eq!(l.charge_minus_e_residual,0.0);
        t5_assert_ref(l.energy_residual,0.0,l.p_internal.abs()+l.p_gamma.abs()+heat.abs());
    }}
}

#[test]
fn material_four_force_matches_photon_energy() {
    let state=t5_state();
    let node=t5_bf_node(BfChannel::P(PBoundFreeTable::jacobs_high_length()),&state,1.2,Mat2::scalar(0.2));
    let out=assemble_selected_he_material_ledger(&state,&[],&[],&[node],&[],PairGridConvention::FullOrderedExchangeClosed).unwrap();
    let p=out.photon.energy_rate_j;let scale=p.abs();
    t5_assert_ref(C_M_S*out.force.q_photon[0],p,scale);
    t5_assert_ref(C_M_S*out.force.q_matter[0],-p,scale);
    t5_assert_ref(out.ledger_si.p_internal+out.bf.heat_power_j,C_M_S*out.force.q_matter[0],scale);
    for k in 0..4 {assert_eq!(out.force.q_matter[k],-out.force.q_photon[k]);}
    t5_assert_ref(out.force.q_photon[3],p/C_M_S,scale/C_M_S);
    assert_eq!(out.force.q_photon[1],0.0);assert_eq!(out.force.q_photon[2],0.0);
}

#[test]
fn bf_opposite_rays_cancel_momentum_not_energy() {
    let state=t5_state();let a=t5_bf_node(BfChannel::P(PBoundFreeTable::jacobs_high_length()),&state,1.2,Mat2::scalar(0.2));
    let mut b=a;b.direction=[0.0,0.0,-1.0];
    let one=assemble_he_bf_grid(&state,&[a]).unwrap();let two=assemble_he_bf_grid(&state,&[a,b]).unwrap();
    t5_assert_ref(two.photon.energy_rate_j,2.0*one.photon.energy_rate_j,2.0*one.photon.energy_rate_j.abs());
    assert_eq!(two.photon.momentum_rate,[0.0;3]);
}

#[test]
fn bf_missing_zero_weight_is_not_physical_zero() {
    let state=t5_state();let mut node=t5_bf_node(BfChannel::P(PBoundFreeTable::jacobs_high_length()),&state,0.5,Mat2::zero());
    node.weight_energy_j=0.0;
    assert!(matches!(assemble_he_bf_grid(&state,&[node]),Err(CoverageError::MissingAuthority{..})));
    node.energy_ev=state.constants.chi_p_ev/2.0;
    let o=assemble_he_bf_grid(&state,&[node]).unwrap();assert_eq!(o.physical_zero_nodes,1);assert_eq!(o.rates,[0.0;2]);
    assert_eq!(o.photon.energy_rate_j,0.0);
}

#[test]
fn bf_assembly_invalid_measures_directions_and_drift() {
    let state=t5_state();let original=t5_bf_node(BfChannel::P(PBoundFreeTable::jacobs_high_length()),&state,1.2,Mat2::zero());
    for bad in [-1.0,f64::NAN,f64::INFINITY] {
        let mut n=original;n.weight_energy_j=bad;assert!(assemble_he_bf_grid(&state,&[n]).is_err());
        let mut n=original;n.weight_omega_sr=bad;assert!(assemble_he_bf_grid(&state,&[n]).is_err());
    }
    let mut n=original;n.direction=[0.0,0.0,2.0];assert!(assemble_he_bf_grid(&state,&[n]).is_err());
    n.direction=[1.0,0.0,0.0];assert!(assemble_he_bf_grid(&state,&[n]).is_err());
    let mut drift=state;drift.electron_frame=rec_microphysics::he_singlet::ElectronFramePolicy::SpeciesDriftUnsupported;
    assert!(matches!(assemble_he_bf_grid(&drift,&[original]),Err(CoverageError::MissingAuthority{..})));
}

#[test]
fn bf_assembly_applies_joule_and_angular_measure_once() {
    let state=t5_state();let mut n=t5_bf_node(BfChannel::S(SBoundFreeTable::jacobs_high_length()),&state,1.2,Mat2::scalar(0.1));
    let a=assemble_he_bf_grid(&state,&[n]).unwrap();n.weight_energy_j*=3.0;n.weight_omega_sr*=2.0;
    let b=assemble_he_bf_grid(&state,&[n]).unwrap();
    t5_assert_ref(b.rates[1],6.0*a.rates[1],6.0*a.rates[1].abs());
    t5_assert_ref(b.heat_power_j,6.0*a.heat_power_j,6.0*a.heat_power_j.abs());
}

#[test]
fn bf_nonfinite_arithmetic_is_not_a_valid_source() {
    let mut state=t5_state();state.n_he_plus=1e300;state.ne=1e300;
    let ep=state.constants.chi_p_ev+1.2*state.constants.rydberg_ev;
    let es=state.constants.chi_s_ev+1.2*state.constants.rydberg_ev;
    assert!(matches!(he_p_bf_source(ep,&state,PBoundFreeTable::jacobs_high_length()),Err(CoverageError::NumericalDomainUncertain{..})));
    assert!(matches!(he_s_bf_source(es,&state,SBoundFreeTable::jacobs_high_length()),Err(CoverageError::NumericalDomainUncertain{..})));
}

#[test]
fn bb_material_momentum_survives_zero_leading_recoil_heat() {
    let mut state=t5_state();state.ng=0.0;state.ns=0.0;
    let node=DirectedBbMode{mode:WeightedBbMode{f:Mat2::zero(),v:[[1.0,0.0],[0.0,1.0],[0.0,0.0]],weight_sr:0.7},direction:[0.0,0.0,1.0]};
    for ir in [false,true] {
        let one=[node]; let empty: [DirectedBbMode;0]=[];
        let (a,b)=if ir {(&empty[..],&one[..])}else{(&one[..],&empty[..])};
        let o=assemble_selected_he_material_ledger(&state,a,b,&[],&[],PairGridConvention::FullOrderedExchangeClosed).unwrap();
        assert_eq!(o.bf.heat_power_j,0.0);assert!(o.photon.energy_rate_j>0.0 && o.force.q_matter[3]<0.0);
        t5_assert_ref(o.energy_residual_j,0.0,o.photon.energy_rate_j.abs());
    }
}

fn t5_pair_nodes() -> [DirectedPairMode;2] {
    let v1=[[1.0,0.0],[0.0,1.0],[0.0,0.0]];let v2=[[0.0,0.0],[1.0,0.0],[0.0,1.0]];
    [DirectedPairMode{mode:WeightedPairMode{input:PairInput{y:0.25,f1:Mat2::zero(),f2:Mat2::zero(),v1,v2},weight_dy:0.1,weight_omega1_sr:0.5,weight_omega2_sr:0.6,exchange_partner:1},direction1:[0.0,0.0,1.0],direction2:[1.0,0.0,0.0]},
     DirectedPairMode{mode:WeightedPairMode{input:PairInput{y:0.75,f1:Mat2::zero(),f2:Mat2::zero(),v1:v2,v2:v1},weight_dy:0.1,weight_omega1_sr:0.6,weight_omega2_sr:0.5,exchange_partner:0},direction1:[1.0,0.0,0.0],direction2:[0.0,0.0,1.0]}]
}
#[test]
fn pair_material_moment_uses_one_full_tag_not_two() {
    let mut state=t5_state();state.ng=0.0;state.ns=1.0;let nodes=t5_pair_nodes();
    let o=assemble_selected_he_material_ledger(&state,&[],&[],&[],&nodes,PairGridConvention::FullOrderedExchangeClosed).unwrap();
    let r=o.rates.r2g;
    t5_assert_ref(o.photon.number_rate,2.0*r,2.0*r.abs());
    t5_assert_ref(o.photon.energy_rate_j,state.constants.delta_s_ev*EV_J*r,state.constants.delta_s_ev*EV_J*r.abs());
    assert!(o.force.q_photon[1]>0.0 && o.force.q_photon[3]>0.0);
    t5_assert_ref(o.energy_residual_j,0.0,o.photon.energy_rate_j.abs());
}
#[test]
fn pair_material_direction_exchange_is_enforced() {
    let state=t5_state();let mut nodes=t5_pair_nodes();nodes[1].direction2=[0.0,0.0,-1.0];
    assert!(assemble_selected_he_material_ledger(&state,&[],&[],&[],&nodes,PairGridConvention::FullOrderedExchangeClosed).is_err());
    assert!(assemble_selected_he_material_ledger(&state,&[],&[],&[],&t5_pair_nodes(),PairGridConvention::UnorderedHalfGridUnsupported).is_err());
}
#[test]
fn selected_material_ledger_combines_five_channels_once() {
    let state=t5_state();let bb=DirectedBbMode{mode:WeightedBbMode{f:Mat2::scalar(0.1),v:state.v,weight_sr:0.2},direction:[0.0,0.0,1.0]};
    let bf=[t5_bf_node(BfChannel::P(PBoundFreeTable::jacobs_high_length()),&state,1.2,Mat2::scalar(0.1)),t5_bf_node(BfChannel::S(SBoundFreeTable::jacobs_high_length()),&state,1.2,Mat2::scalar(0.2))];
    let o=assemble_selected_he_material_ledger(&state,&[bb],&[bb],&bf,&t5_pair_nodes(),PairGridConvention::FullOrderedExchangeClosed).unwrap();
    let scale=o.photon.number_gross;
    t5_assert_ref(o.photon_number_residual,0.0,scale);
    t5_assert_ref(o.atomic_p_trace_residual.re,0.0,scale);
    t5_assert_ref(o.atomic_p_trace_residual.im,0.0,scale);
    t5_assert_ref(o.atomic_s_residual,0.0,scale);
    t5_assert_ref(o.energy_residual_j,0.0,o.photon.energy_gross_j+o.ledger_si.p_internal.abs()+o.bf.heat_power_j.abs());
}
#[test]
fn selected_material_ledger_has_no_empty_or_mixed_registry_success() {
    let state=t5_state();
    assert!(assemble_selected_he_material_ledger(&state,&[],&[],&[],&[],PairGridConvention::FullOrderedExchangeClosed).is_err());
    let mut changed=state;changed.constants.rydberg_ev*=1.1;
    let node=t5_bf_node(BfChannel::P(PBoundFreeTable::jacobs_high_length()),&changed,1.2,Mat2::scalar(0.1));
    assert!(assemble_selected_he_material_ledger(&changed,&[],&[],&[node],&[],PairGridConvention::FullOrderedExchangeClosed).is_err());
}

// Task7 supplemental Gate-P contracts. Source and acceptance are frozen;
// these tests are authored only here and must be executed by Local Codex.
#[test]
fn t4l01_event_matrix_exact_integer_null_vectors() {
    let a = rec_microphysics::ledger::EVENT_MATRIX;
    let nuclei: [i64; 6] = [1, 1, 1, 1, 0, 0];
    let charge: [i64; 6] = [0, 0, 0, 1, -1, 0];
    for col in 0..5 {
        let n: i64 = (0..6).map(|row| nuclei[row] * i64::from(a[row][col])).sum();
        let q: i64 = (0..6).map(|row| charge[row] * i64::from(a[row][col])).sum();
        assert_eq!(n, 0, "He-nucleus column {col}");
        assert_eq!(q, 0, "charge column {col}");
    }
    assert_eq!(a[5], [1, 1, -1, -1, 2]);
}

// Printed WU30 rows, independent of the production table accessor.
fn t7_printed_linear(q: f64, values: [f64; 3]) -> f64 {
    let index = if q <= 1.2 { 0 } else { 1 };
    let left = if index == 0 { 1.0 } else { 1.2 };
    let t = (q - left) / 0.2;
    (1.0 - t) * values[index] + t * values[index + 1]
}

#[test]
fn t4l03_bf_lte_both_gauges_nodes_and_midpoints() {
    use rec_microphysics::he_singlet::planck_occupation;
    let lte = SourceState::lte_populations(8000.0, 2.0e7, 3.0e7).unwrap();
    let screens = [
        [[1.0, 0.0], [0.0, 1.0], [0.0, 0.0]],
        [[0.6, 0.0], [0.8, 0.0], [0.0, 1.0]],
    ];
    for q in [1.0, 1.1, 1.2, 1.3, 1.4] {
        let ep = lte.constants.chi_p_ev + q * lte.constants.rydberg_ev;
        let es = lte.constants.chi_s_ev + q * lte.constants.rydberg_ev;
        let fp = planck_occupation(ep, lte.temperature_k);
        let fs = planck_occupation(es, lte.temperature_k);
        let eta_p = t5_reference_eta(&lte, ep, lte.constants.chi_p_ev);
        let eta_s = t5_reference_eta(&lte, es, lte.constants.chi_s_ev);
        for v in screens {
            let mut pstate = lte;
            pstate.v = v;
            pstate.f = Mat2::scalar(fp);
            for (table, rows_s, rows_d) in [
                (PBoundFreeTable::jacobs_high_length(),
                 [0.002114, 0.001486, 0.001134], [0.003201, 0.001247, 0.0003970]),
                (PBoundFreeTable::jacobs_high_velocity(),
                 [0.001935, 0.001380, 0.001075], [0.002810, 0.001010, 0.0002663]),
            ] {
                let sigma = 8.06728372576034e-22
                    * (t7_printed_linear(q, rows_s) + t7_printed_linear(q, rows_d));
                let gross_c = C_M_S * sigma
                    * (3.0 * eta_p * (1.0 + fp) + lte.wp.trace().re * fp);
                let phase = (ep * EV_J).powi(2) / (H_J_S * C_M_S).powi(3);
                let gross_atom = 2.0 * phase * gross_c;
                assert!(gross_c > 0.0 && gross_atom > 0.0);
                let out = he_p_bf_source(ep, &pstate, table).unwrap();
                for i in 0..2 { for j in 0..2 {
                    t5_assert_ref(out.photon_c[i][j].re, 0.0, gross_c);
                    t5_assert_ref(out.photon_c[i][j].im, 0.0, gross_c);
                }}
                for i in 0..3 { for j in 0..3 {
                    t5_assert_ref(out.atomic_b[i][j].re, 0.0, gross_atom);
                    t5_assert_ref(out.atomic_b[i][j].im, 0.0, gross_atom);
                }}
                t5_assert_ref(out.event_rate_density, 0.0, gross_atom);
            }
            let mut sstate = lte;
            sstate.v = v;
            sstate.f = Mat2::scalar(fs);
            for (table, rows) in [
                (SBoundFreeTable::jacobs_high_length(), [0.06737, 0.04812, 0.03526]),
                (SBoundFreeTable::jacobs_high_velocity(), [0.06635, 0.04696, 0.03398]),
            ] {
                let sigma = 8.06728372576034e-22 * t7_printed_linear(q, rows);
                let gross_c = C_M_S * sigma * (eta_s * (1.0 + fs) + lte.ns * fs);
                let phase = (es * EV_J).powi(2) / (H_J_S * C_M_S).powi(3);
                let gross_atom = 2.0 * phase * gross_c;
                assert!(gross_c > 0.0 && gross_atom > 0.0);
                let out = he_s_bf_source(es, &sstate, table).unwrap();
                for i in 0..2 { for j in 0..2 {
                    t5_assert_ref(out.photon_c[i][j].re, 0.0, gross_c);
                    t5_assert_ref(out.photon_c[i][j].im, 0.0, gross_c);
                }}
                t5_assert_ref(out.atomic_s_density, 0.0, gross_atom);
                t5_assert_ref(out.event_rate_density, 0.0, gross_atom);
            }
        }
    }
}

#[test]
fn t4l02_isolated_source_channel_energy_and_force() {
    let state = t5_state();
    let bb = DirectedBbMode {
        mode: WeightedBbMode { f: Mat2::scalar(0.1), v: state.v, weight_sr: 0.2 },
        direction: [0.0, 0.0, 1.0],
    };
    let p = t5_bf_node(BfChannel::P(PBoundFreeTable::jacobs_high_length()), &state, 1.2, Mat2::scalar(0.2));
    let s = t5_bf_node(BfChannel::S(SBoundFreeTable::jacobs_high_velocity()), &state, 1.2, Mat2::scalar(0.2));
    for channel in 0..5 {
        let lines584 = if channel == 0 { vec![bb] } else { vec![] };
        let lines_ir = if channel == 1 { vec![bb] } else { vec![] };
        let bf = match channel { 2 => vec![p], 3 => vec![s], _ => vec![] };
        let pairs = if channel == 4 { t5_pair_nodes().to_vec() } else { vec![] };
        let out = assemble_selected_he_material_ledger(
            &state, &lines584, &lines_ir, &bf, &pairs, PairGridConvention::FullOrderedExchangeClosed,
        ).unwrap();
        let rates = [out.rates.r584, out.rates.rir, out.rates.rp, out.rates.rs, out.rates.r2g];
        assert!(rates[channel].is_finite() && rates[channel] != 0.0);
        for (i, rate) in rates.iter().enumerate() { if i != channel { assert_eq!(*rate, 0.0); } }
        let p_int = out.ledger_si.p_internal;
        let p_gamma = out.photon.energy_rate_j;
        let heat = out.bf.heat_power_j;
        let scale = p_int.abs() + p_gamma.abs() + heat.abs();
        assert!(scale > 0.0);
        t5_assert_ref(p_int + p_gamma + heat, 0.0, scale);
        t5_assert_ref(C_M_S * out.force.q_photon[0], p_gamma, scale);
        t5_assert_ref(C_M_S * out.force.q_matter[0], p_int + heat, scale);
        if channel < 2 || channel == 4 { assert_eq!(heat, 0.0); }
        // Opposite signs are a definition, not the independent energy check above.
        for k in 0..4 { assert_eq!(out.force.q_matter[k], -out.force.q_photon[k]); }
    }
}

#[test]
fn t4l13_pbf_is_not_relabelled_as_584_decay() {
    let mut state = t5_state();
    state.n_he_plus = 0.0;
    state.ne = 0.0;
    let line = DirectedBbMode {
        mode: WeightedBbMode { f: Mat2::scalar(0.1), v: state.v, weight_sr: 0.2 },
        direction: [0.0, 0.0, 1.0],
    };
    let bf = t5_bf_node(BfChannel::P(PBoundFreeTable::jacobs_high_length()), &state, 1.2, Mat2::scalar(0.2));
    let convention = PairGridConvention::FullOrderedExchangeClosed;
    let a = assemble_selected_he_material_ledger(&state, &[line], &[], &[], &[], convention).unwrap();
    let b = assemble_selected_he_material_ledger(&state, &[], &[], &[bf], &[], convention).unwrap();
    let mix = assemble_selected_he_material_ledger(&state, &[line], &[], &[bf], &[], convention).unwrap();
    assert!(b.rates.rp > 0.0);
    assert_eq!(mix.rates.r584, a.rates.r584);
    assert_eq!(mix.rates.rp, b.rates.rp);
    assert_eq!(mix.rates.rir, 0.0);
    assert_eq!(mix.rates.rs, 0.0);
    assert_eq!(mix.rates.r2g, 0.0);
    let expected = a.atomic_p + b.atomic_p;
    let scale = a.atomic_p.max_abs() + b.atomic_p.max_abs();
    for i in 0..3 { for j in 0..3 {
        t5_assert_ref(mix.atomic_p[i][j].re, expected[i][j].re, scale);
        t5_assert_ref(mix.atomic_p[i][j].im, expected[i][j].im, scale);
    }}
    t5_assert_ref(mix.photon.number_rate, a.photon.number_rate + b.photon.number_rate,
        a.photon.number_gross + b.photon.number_gross);
    t5_assert_ref(mix.ledger_si.species_source[2], -(a.rates.r584 + b.rates.rp),
        a.rates.r584.abs() + b.rates.rp.abs());
}

#[test]
fn t4l10_isotropic_wp_keeps_complex_photon_matrix() {
    let mut state = t5_state();
    let np = 4.2;
    state.wp = Mat3::scalar(np / 3.0);
    state.f = Mat2([[c(0.2, 0.0), c(0.03, 0.04)], [c(0.03, -0.04), c(0.1, 0.0)]]);
    state.v = [[0.6, 0.0], [0.8, 0.0], [0.0, 1.0]];
    let energy = state.constants.chi_p_ev + 1.2 * state.constants.rydberg_ev;
    let eta = t5_reference_eta(&state, energy, state.constants.chi_p_ev);
    for (table, printed_s, printed_d) in [
        (PBoundFreeTable::jacobs_high_length(), 0.001486, 0.001247),
        (PBoundFreeTable::jacobs_high_velocity(), 0.001380, 0.001010),
    ] {
        let sigma = 8.06728372576034e-22 * (printed_s + printed_d);
        let gain = (Mat2::identity() + state.f).scale(3.0 * eta);
        let loss = state.f.scale(np);
        let wanted = (gain - loss).scale(C_M_S * sigma);
        let gross = C_M_S * sigma * (gain.max_abs() + loss.max_abs());
        assert!(wanted[0][1].im != 0.0 && gross > 0.0);
        let out = he_p_bf_source(energy, &state, table).unwrap();
        for i in 0..2 { for j in 0..2 {
            t5_assert_ref(out.photon_c[i][j].re, wanted[i][j].re, gross);
            t5_assert_ref(out.photon_c[i][j].im, wanted[i][j].im, gross);
        }}
    }
}
