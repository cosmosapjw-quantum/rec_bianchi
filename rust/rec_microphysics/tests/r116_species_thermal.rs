use rec_microphysics::anisotropic::DirectionalSky;
use rec_microphysics::species_thermal::{
    HeliumModel, KB_J_K, Point, State, TransitionRates, matched_step, proper_rate,
};
fn state(xp: f64, h2: f64, h3: f64, tm: f64, fhe: f64) -> State {
    State::from_xp_tm(xp, h2, h3, tm, fhe).unwrap()
}
fn point(t: f64, n: f64, h: f64, g: f64, theta: f64, model: HeliumModel) -> Point {
    Point::new(
        &DirectionalSky {
            weights: &[1.],
            temperature_k: &[t],
            expansion_factor: &[1.],
        },
        n,
        h,
        g,
        theta,
        0.,
        model,
    )
    .unwrap()
}
#[test]
fn exact_reference_identity_with_helium_and_temperature() {
    let f = 0.08188416223421702;
    let a = state(0.99999, 0.055, 0., 5700., f);
    let b = state(0.99998, 0.054, 0., 5650., f);
    let p = point(5700., 1.7e9, 1.2e-13, 1., 3., HeliumModel::NativeHeI);
    let (out, diag) = matched_step(a, a, b, 0.002, f, &p, &p).unwrap();
    assert_eq!(out, b);
    assert_eq!(diag.iterations, 0);
}
#[test]
fn hydrogen_uses_all_electrons_and_thermal_particle_count() {
    let f = 0.08;
    let a = state(0.4, 0., 0., 20., f);
    let b = state(0.4, 0.04, 0.02, 20., f);
    let p = point(
        1.,
        1e8,
        1e-12,
        1.,
        3.,
        HeliumModel::Supplied {
            hei: TransitionRates::ZERO,
            heii: TransitionRates::ZERO,
        },
    );
    let ra = proper_rate(a, f, &p).unwrap();
    let rb = proper_rate(b, f, &p).unwrap();
    assert!((rb.d_x_hi / ra.d_x_hi - b.xe() / a.xe()).abs() < 1e-12);
    assert!((b.tm(f) - 20.).abs() < 1e-14);
    assert!((rb.d_w_k + 2. * b.w_k * p.clock_s() - rb.compton_w_k_s).abs() < 1e-18);
}
#[test]
fn supplied_heiii_evolves_and_preserves_species_and_heat_ledger() {
    let f = 0.08;
    let a = state(0.4, 0.02, 0.03, 100., f);
    let p = point(
        100.,
        1e7,
        1e-11,
        1.1,
        2.8,
        HeliumModel::Supplied {
            hei: TransitionRates {
                ionization_s: 2e-12,
                recombination_m3_s: 1e-18,
            },
            heii: TransitionRates {
                ionization_s: 1e-12,
                recombination_m3_s: 5e-18,
            },
        },
    );
    let r = point(
        100.,
        1e7,
        1e-11,
        1.,
        3.,
        HeliumModel::Supplied {
            hei: TransitionRates::ZERO,
            heii: TransitionRates::ZERO,
        },
    );
    let (b, diag) = matched_step(a, a, a, 0.02, f, &p, &r).unwrap();
    assert!(b.x_heiii < a.x_heiii && b.x_heii > a.x_heii);
    b.validate(f).unwrap();
    assert!(diag.thermal_balance_defect_j_per_h.abs() < 1e-28);
    assert!((b.xe() - (b.xp() + b.x_heii + 2. * b.x_heiii)).abs() < 1e-15);
    assert!(KB_J_K > 0.);
}
#[test]
fn invalid_phase_and_nonphysical_states_fail_closed() {
    let f = 0.08;
    let a = state(0.999, 0.03, 0.001, 5000., f);
    let p = point(5000., 1e9, 1e-13, 1., 3., HeliumModel::NativeHeI);
    assert!(proper_rate(a, f, &p).is_err());
    let p = point(100., 1e7, 1e-11, 1., 3., HeliumModel::NeutralHelium);
    assert!(proper_rate(a, f, &p).is_err());
    assert!(State::from_xp_tm(0.5, 0.07, 0.02, 100., f).is_err());
}

#[test]
fn reference_has_one_species_owner_and_consistent_anchors() {
    use rec_microphysics::species_thermal::ReferenceHistory;
    let good = "rec_species_reference_v1\nf_he 0.08\nhelium neutral\neta x_hi x_heii x_heiii w_k n_h_m3 h_s tr_k\n0 0.2 0 0 940 100 1e-12 500\n0.1 0.3 0 0 800 74.08182206817179 8e-13 452.4187090179798\n";
    let r = ReferenceHistory::parse(good).unwrap();
    let n = r.at(0.05).unwrap();
    assert!((n.state.x_hi - 0.25).abs() < 1e-15);
    assert!((n.state.w_k - 870.).abs() < 1e-13);
    assert!((n.n_h_m3 / 100. - (-0.15f64).exp()).abs() < 1e-14);
    assert!(r.at(0.11).is_err());
    assert!(ReferenceHistory::parse(&good.replace("0.3 0 0", "0.3 0.01 0")).is_err());
    assert!(ReferenceHistory::parse(&good.replace("74.08182206817179", "70.")).is_err());
}

#[test]
fn native_hei_matches_original_c_oracle() {
    use rec_microphysics::species_thermal::native_hei_rate_s;
    let fixture = include_str!("../../../research/r116_species_thermal/HEI_C_FIXTURE.tsv");
    let mut max_abs: f64 = 0.;
    let mut max_rel: f64 = 0.;
    let mut n = 0;
    for l in fixture.lines().skip(1) {
        let a = l
            .split_whitespace()
            .map(|v| v.parse::<f64>().unwrap())
            .collect::<Vec<_>>();
        assert_eq!(a.len(), 7);
        let y = State::from_hi_tm(a[0], a[1], 0., a[5], a[2]).unwrap();
        let r = native_hei_rate_s(y, a[2], a[3], a[4], a[5]).unwrap();
        max_abs = max_abs.max((r - a[6]).abs());
        max_rel = max_rel.max((r - a[6]).abs() / a[6].abs().max(1e-18));
        n += 1;
    }
    eprintln!("native helium C comparison n={n} max_abs={max_abs:e} max_rel={max_rel:e}");
    assert_eq!(n, 27);
    assert!(max_rel < 1e-7);
}

#[test]
fn adiabatic_w_on_material_clock_has_exact_backward_euler_solution() {
    let fhe = 0.08;
    let ref_state = state(0., 0., 0., 100., fhe);
    let p = point(0.1, 1e7, 1e-12, 1.4, 2.7, HeliumModel::NeutralHelium);
    let r = point(0.1, 1e7, 1e-12, 1., 0., HeliumModel::NeutralHelium);
    let mut y = ref_state;
    let dt = 0.01;
    for _ in 0..100 {
        let (z, diag) = matched_step(y, ref_state, ref_state, dt, fhe, &p, &r).unwrap();
        assert!(diag.thermal_balance_defect_j_per_h.abs() < 1e-29);
        assert_eq!(z.xe(), 0.);
        y = z;
    }
    let expected = ref_state.w_k * (1. + 2. / 3. * 2.7 * dt).powi(-100);
    eprintln!("adiabatic W error {:.4e}", (y.w_k - expected).abs());
    assert!((y.w_k - expected).abs() < 1e-9);
}

#[test]
fn tiny_matched_thermal_increment_is_not_rounded_away_by_solver_tolerance() {
    let fhe = 0.;
    let y = state(0., 0., 0., 100., fhe);
    let p = Point::new(
        &DirectionalSky {
            weights: &[1.],
            temperature_k: &[0.1],
            expansion_factor: &[1.],
        },
        1.,
        1e-12,
        1.,
        0.,
        1.5 * KB_J_K * 1e-12 * 1e-9,
        HeliumModel::NeutralHelium,
    )
    .unwrap();
    let r = point(0.1, 1., 1e-12, 1., 0., HeliumModel::NeutralHelium);
    let (next, _) = matched_step(y, y, y, 0.1, fhe, &p, &r).unwrap();
    assert!(
        (next.w_k - y.w_k - 1e-10).abs() < 3e-14,
        "tiny heat increment lost"
    );
}
